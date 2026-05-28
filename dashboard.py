import argparse
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st


STATUSES = ["applied", "interviewing", "rejected", "offer"]
STATUS_UI_ORDER = ["applied", "queued", "failed", "review needed", "submitted", "draft", "interviewing", "rejected", "offer"]
SUBMITTED_STATUSES = set(STATUSES)
NON_SUBMITTED_STATUSES = {
    "draft",
    "retry",
    "retries",
    "queued",
    "queue",
    "failed",
    "placeholder",
    "pending",
    "in_progress",
}


def parse_workspace_arg() -> Optional[Path]:
    """Parse optional --workspace passed after `--` in Streamlit CLI."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--workspace", type=str, default=None)
    args, _ = parser.parse_known_args()
    return Path(args.workspace).expanduser().resolve() if args.workspace else None


def resolve_workspace() -> Path:
    script_dir = Path(__file__).resolve().parent
    override = parse_workspace_arg()
    if override:
        return override
    return script_dir.parent


@st.cache_data(ttl=2)
def load_applications(csv_path: str) -> pd.DataFrame:
    path = Path(csv_path)
    if not path.exists():
        return pd.DataFrame(
            columns=[
                "date",
                "company",
                "role",
                "jd_url",
                "ats_platform",
                "status",
                "resume_file",
                "cover_letter_file",
                "match_score",
                "notes",
            ]
        )

    parse_warning = None
    parse_warning_detail = None
    try:
        df = pd.read_csv(path)
    except pd.errors.ParserError as exc:
        # Fallback for malformed CSV rows (extra delimiters, broken quoting, etc).
        # Skip unreadable rows instead of crashing the whole dashboard.
        parse_warning = (
            "Malformed CSV rows were detected and skipped while loading the log. "
            "Please review and repair the source file for full fidelity."
        )
        parse_warning_detail = str(exc)
        df = pd.read_csv(path, engine="python", on_bad_lines="skip")
    for col in ["date", "company", "role", "status", "match_score", "notes", "jd_url", "resume_file"]:
        if col not in df.columns:
            df[col] = pd.NA

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["match_score"] = pd.to_numeric(df["match_score"], errors="coerce")
    df["status"] = df["status"].astype("string").str.strip().str.lower().fillna("applied")
    if parse_warning:
        df.attrs["parse_warning"] = parse_warning
    if parse_warning_detail:
        df.attrs["parse_warning_detail"] = parse_warning_detail
    return df


def save_status_updates(df: pd.DataFrame, csv_path: Path) -> None:
    if "date" in df.columns:
        out = df.copy()
        out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    else:
        out = df
    out.to_csv(csv_path, index=False)


def _build_application_key(df: pd.DataFrame) -> pd.Series:
    if "application_id" in df.columns:
        app_id = df["application_id"].fillna("").astype("string").str.strip().str.lower()
    else:
        app_id = pd.Series([""] * len(df), index=df.index, dtype="string")
    company = df["company"].fillna("").astype("string").str.strip().str.lower()
    role = df["role"].fillna("").astype("string").str.strip().str.lower()
    # Deliberately avoid date in the primary identity key so retries/re-entries
    # of the same job posting do not inflate "Total Applied".
    fallback = company + "|" + role
    return app_id.where(app_id.ne(""), fallback)


def compute_metrics_frame(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Build a deterministic metrics frame and diagnostics."""
    metrics_df = df.copy()
    metrics_df["status"] = metrics_df["status"].astype("string").str.strip().str.lower()
    metrics_df["application_key"] = _build_application_key(metrics_df)
    metrics_df["has_required_identity"] = (
        metrics_df["company"].notna() & metrics_df["role"].notna()
        & metrics_df["company"].astype("string").str.strip().ne("")
        & metrics_df["role"].astype("string").str.strip().ne("")
    )
    metrics_df["is_submitted_status"] = metrics_df["status"].isin(SUBMITTED_STATUSES)
    metrics_df["is_excluded_status"] = metrics_df["status"].isin(NON_SUBMITTED_STATUSES)
    metrics_df["is_submitted_candidate"] = metrics_df["has_required_identity"] & metrics_df["is_submitted_status"]

    submitted = metrics_df[metrics_df["is_submitted_candidate"]].copy()
    dedup_submitted = (
        submitted.sort_values(["date"], ascending=False)
        .drop_duplicates(subset=["application_key"], keep="first")
    )

    status_counts = metrics_df["status"].value_counts(dropna=False).to_dict()
    duplicate_rows = int(metrics_df.duplicated(keep=False).sum())
    duplicate_application_keys = int(metrics_df["application_key"].duplicated(keep=False).sum())
    malformed_statuses = sorted(
        set(metrics_df["status"].dropna().unique()) - SUBMITTED_STATUSES - NON_SUBMITTED_STATUSES
    )
    diagnostics = {
        "raw_rows": len(metrics_df),
        "submitted_candidate_rows": len(submitted),
        "deduplicated_submitted_rows": len(dedup_submitted),
        "duplicate_full_rows": duplicate_rows,
        "duplicate_application_keys": duplicate_application_keys,
        "unique_company_role_pairs": int(
            metrics_df.assign(
                company_norm=metrics_df["company"].fillna("").astype("string").str.strip().str.lower(),
                role_norm=metrics_df["role"].fillna("").astype("string").str.strip().str.lower(),
            )[["company_norm", "role_norm"]].drop_duplicates().shape[0]
        ),
        "status_counts": status_counts,
        "malformed_statuses": malformed_statuses,
        "excluded_status_rows": int(metrics_df["is_excluded_status"].sum()),
    }
    return dedup_submitted, diagnostics


def render_stats(df: pd.DataFrame) -> None:
    metrics_df, diagnostics = compute_metrics_frame(df)
    total = len(metrics_df)
    responded = metrics_df["status"].isin(["interviewing", "offer"]).sum() if total else 0
    response_rate = (responded / total * 100) if total else 0
    avg_match = metrics_df["match_score"].mean() if total else 0

    last_applied_days = None
    if total and metrics_df["date"].notna().any():
        last_date = metrics_df["date"].max()
        last_applied_days = (pd.Timestamp.now().normalize() - last_date.normalize()).days

    stats = [
        ("Total Applied", f"{total}", "Deduplicated submitted apps"),
        ("Response Rate", f"{response_rate:.1f}%", "Interviewing + offer"),
        ("Avg Match Score", f"{avg_match:.1f}", "Submitted set only"),
        ("Days Since Last Application", "N/A" if last_applied_days is None else str(last_applied_days), "From most recent submission"),
    ]
    cols = st.columns(4)
    for col, (label, value, hint) in zip(cols, stats):
        col.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-hint">{hint}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("Metric Debug Details"):
        st.write("Metric logic: submitted rows = status in applied/interviewing/rejected/offer + non-empty company/role; deduplicated by application_id when present, else company|role.")
        st.write(f"Raw dataframe rows: {diagnostics['raw_rows']}")
        st.write(f"Submitted candidate rows before dedupe: {diagnostics['submitted_candidate_rows']}")
        st.write(f"Total applied after dedupe (displayed metric): {diagnostics['deduplicated_submitted_rows']}")
        st.write(f"Rows excluded due to non-submitted statuses: {diagnostics['excluded_status_rows']}")
        st.write(f"Duplicate full rows detected: {diagnostics['duplicate_full_rows']}")
        st.write(f"Duplicate application keys detected: {diagnostics['duplicate_application_keys']}")
        st.write(f"Unique company+role pairs: {diagnostics['unique_company_role_pairs']}")
        st.write("Status counts:", diagnostics["status_counts"])
        if diagnostics["malformed_statuses"]:
            st.warning(f"Malformed/unknown statuses detected: {', '.join(diagnostics['malformed_statuses'])}")
        if diagnostics["deduplicated_submitted_rows"] > diagnostics["unique_company_role_pairs"]:
            st.warning("Submitted count exceeds unique company+role pairs; possible multiple applications/retries exist.")
        if diagnostics["duplicate_application_keys"] > 0:
            st.warning("Duplicate application keys detected; deduplication applied in metrics.")
        st.write("Rows contributing to Total Applied (deduplicated submitted set):")
        st.dataframe(
            metrics_df[["date", "company", "role", "status", "match_score", "application_key"]].sort_values("date", ascending=False),
            use_container_width=True,
        )


def render_pipeline(df: pd.DataFrame) -> None:
    st.subheader("Pipeline")
    cols = st.columns(len(STATUSES))
    for idx, status in enumerate(STATUSES):
        with cols[idx]:
            st.markdown(f"**{status.title()}**")
            bucket = df[df["status"] == status].sort_values("date", ascending=False)
            if bucket.empty:
                st.caption("No applications")
            for _, row in bucket.iterrows():
                date_str = row["date"].strftime("%Y-%m-%d") if pd.notna(row["date"]) else "Unknown date"
                score = "—" if pd.isna(row["match_score"]) else f"{row['match_score']:.1f}"
                st.markdown(
                    f"""
                    <div class="pipeline-card">
                        <div class="pipeline-company">{row.get('company', '')}</div>
                        <div class="pipeline-role">{row.get('role', '')}</div>
                        <div class="pipeline-meta">{date_str} · Match: {score}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_log_table(df: pd.DataFrame, csv_path: Path) -> pd.DataFrame:
    st.subheader("Application Log")
    st.caption("Filter by status and edit status inline. Changes are saved immediately.")
    all_statuses = sorted(set(df["status"].dropna().astype("string").str.strip().str.lower().tolist()) | set(STATUS_UI_ORDER))
    default_statuses = [s for s in STATUS_UI_ORDER if s in all_statuses]
    filter_status = st.multiselect("Status", options=all_statuses, default=default_statuses)
    filtered = df[df["status"].isin(filter_status)] if filter_status else df.iloc[0:0]

    editable = filtered.copy()
    editable["status"] = pd.Categorical(editable["status"], categories=STATUSES, ordered=False)

    edited = st.data_editor(
        editable,
        key="applications_editor",
        use_container_width=True,
        hide_index=False,
        disabled=[c for c in editable.columns if c != "status"],
        column_config={
            "status": st.column_config.SelectboxColumn("status", options=all_statuses, required=True),
            "date": st.column_config.DateColumn("date", format="YYYY-MM-DD"),
        },
    )

    changed = edited["status"].astype("string").fillna("").ne(editable["status"].astype("string").fillna(""))
    if changed.any():
        updated = df.copy()
        for idx in edited[changed].index:
            updated.loc[idx, "status"] = str(edited.loc[idx, "status"])
        save_status_updates(updated, csv_path)
        load_applications.clear()
        st.success("Status updated and saved to CSV.")
        st.rerun()

    return filtered


def render_detail_drawer(df: pd.DataFrame, workspace_root: Path) -> None:
    st.subheader("Application Details")
    if df.empty:
        st.caption("No records to inspect.")
        return

    options = [
        f"{r.index}: {r.company} — {r.role}"
        for r in df.reset_index().itertuples(index=False)
    ]
    selected = st.selectbox("Select an application", options=options)
    original_idx = int(selected.split(":", 1)[0])
    row = df.loc[original_idx]

    jd_file = row.get("jd_url", "")
    resume_file = row.get("resume_file", "")

    st.markdown(f"**Company:** {row.get('company', '')}")
    st.markdown(f"**Role:** {row.get('role', '')}")
    status_value = str(row.get('status', '')).strip().title()
    st.markdown(f"**Status:** <span class='status-pill status-{str(row.get('status', '')).strip().lower().replace(' ', '-')}'>{status_value}</span>", unsafe_allow_html=True)
    st.markdown(f"**Date:** {row['date'].strftime('%Y-%m-%d') if pd.notna(row['date']) else 'Unknown'}")
    st.markdown(f"**Match Score:** {'—' if pd.isna(row.get('match_score')) else row.get('match_score')}")
    st.markdown(f"**JD file/url:** `{jd_file}`")
    st.markdown(f"**Resume file:** `{resume_file}`")
    st.markdown("**Notes:**")
    st.code(str(row.get("notes", "")))

    jd_dir = workspace_root / "Job Descriptions"
    res_dir = workspace_root / "Resumes"
    st.caption(f"JD directory: {jd_dir}")
    st.caption(f"Resumes directory: {res_dir}")


def main() -> None:
    st.set_page_config(page_title="Job Application Dashboard", layout="wide")

    st.markdown(
        """
        <style>
            :root {
              --bg: #0f1115;
              --panel: #151922;
              --panel-2: #171c26;
              --border: #252c38;
              --text: #e6e8ec;
              --muted: #9aa4b2;
              --accent: #7aa2f7;
              --ok: #7cbf9a;
              --warn: #c9aa7a;
              --bad: #b57d86;
            }
            .stApp {
              background: var(--bg);
              color: var(--text);
              font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
            }
            .block-container {padding-top: 2rem; padding-bottom: 2rem;}
            h1, h2, h3 {letter-spacing: -0.02em;}
            h1 {font-weight: 700; margin-bottom: 0.25rem;}
            h2, h3 {font-weight: 600;}
            .kpi-card {
              background: linear-gradient(180deg, var(--panel), var(--panel-2));
              border: 1px solid var(--border);
              border-radius: 12px;
              padding: 0.85rem 1rem;
              min-height: 94px;
              transition: border-color .15s ease, transform .15s ease;
            }
            .kpi-card:hover {border-color: #364152; transform: translateY(-1px);}
            .kpi-label {font-size: 0.8rem; color: var(--muted); margin-bottom: 0.35rem; text-transform: uppercase; letter-spacing: .04em;}
            .kpi-value {font-size: 1.65rem; line-height: 1.1; font-weight: 650; color: var(--text);}
            .kpi-hint {font-size: 0.75rem; color: #7f8997; margin-top: 0.3rem;}
            .pipeline-card {
              background: #121720;
              border: 1px solid var(--border);
              border-radius: 10px;
              padding: 0.65rem 0.75rem;
              margin-bottom: 0.5rem;
            }
            .pipeline-company {font-weight: 620; margin-bottom: 0.15rem;}
            .pipeline-role {color: #ccd3dd; margin-bottom: 0.2rem; font-size: 0.95rem;}
            .pipeline-meta {font-size: 0.8rem; color: var(--muted);}
            .status-pill {
              border-radius: 999px; padding: 0.2rem 0.55rem; border: 1px solid transparent; font-size: 0.78rem;
              background: #1a1f2b; color: #cfd6e0;
            }
            .status-applied, .status-submitted {border-color: #335777; color: #95bddf;}
            .status-interviewing, .status-offer {border-color: #2f5b45; color: #95c9ac;}
            .status-rejected, .status-failed {border-color: #6a3c45; color: #d5a4ad;}
            .status-draft, .status-review-needed, .status-queued {border-color: #5e5366; color: #c1b5ca;}
            [data-testid="stDataFrame"], [data-testid="stDataEditor"] {
              border: 1px solid var(--border);
              border-radius: 10px;
              overflow: hidden;
            }
            [data-testid="stSidebar"] {background: #11151d;}
            [data-testid="stExpander"] {border: 1px solid var(--border); border-radius: 10px;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    workspace_root = resolve_workspace()
    csv_path = workspace_root / "logs" / "applications_log.csv"

    st.title("Job Applications Dashboard")
    st.caption(f"Workspace root: {workspace_root}")

    df = load_applications(str(csv_path))
    if df.attrs.get("parse_warning"):
        st.warning(df.attrs["parse_warning"])
        if df.attrs.get("parse_warning_detail"):
            st.caption(f"Parser detail: {df.attrs['parse_warning_detail']}")

    render_stats(df)
    st.divider()
    render_pipeline(df)
    st.divider()
    filtered = render_log_table(df, csv_path)
    st.divider()
    render_detail_drawer(filtered, workspace_root)


if __name__ == "__main__":
    main()
