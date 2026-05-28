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
              --bg: #0d1016;
              --bg-soft: #10141c;
              --panel: #141923;
              --panel-2: #161c27;
              --panel-3: #1a2130;
              --border: #252d3a;
              --border-soft: #212837;
              --text: #e7eaf0;
              --muted: #9ba6b5;
              --muted-2: #7f8a9b;
              --accent: #86a8d8;
              --ok: #8fbda5;
              --warn: #c7ad8a;
              --bad: #bd8f98;
            }
            .stApp {
              background: var(--bg);
              color: var(--text);
              font-family: "SF Pro Display", Inter, "Helvetica Neue", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }
            .block-container {padding-top: 1.7rem; padding-bottom: 2rem; max-width: 1320px;}
            .app-header {
              background: linear-gradient(180deg, var(--panel), var(--panel-2));
              border: 1px solid var(--border-soft);
              border-radius: 12px;
              padding: 0.8rem 1rem 0.85rem 1rem;
              margin-bottom: 1rem;
              box-shadow: 0 4px 18px rgba(3, 7, 18, 0.24);
            }
            .app-header-row {
              display: flex;
              align-items: center;
              justify-content: space-between;
              gap: 0.75rem;
              flex-wrap: wrap;
            }
            .brand-title {
              font-size: 1.35rem;
              font-weight: 700;
              letter-spacing: -0.02em;
              color: #eef2f8;
              line-height: 1.1;
            }
            .brand-title .accent {color: #9ebbe3;}
            .brand-subtitle {
              font-size: 0.78rem;
              color: var(--muted);
              margin-top: 0.2rem;
              letter-spacing: .02em;
            }
            .brand-meta {
              font-size: 0.74rem;
              color: var(--muted-2);
              margin-top: 0.18rem;
            }
            .header-badges {display: flex; gap: 0.4rem; flex-wrap: wrap;}
            .header-pill {
              display: inline-block;
              border: 1px solid var(--border-soft);
              border-radius: 999px;
              padding: 0.18rem 0.52rem;
              font-size: 0.7rem;
              color: #c5cfdd;
              background: #182133;
            }
            .header-pill.ok {
              color: #a9d0bb;
              border-color: #2e4d40;
              background: rgba(94, 145, 114, 0.14);
            }
            h1, h2, h3 {letter-spacing: -0.02em; color: var(--text);}
            h1 {font-weight: 680; margin-bottom: 0.25rem; font-size: 2.45rem;}
            h2, h3 {font-weight: 620;}
            p, label, [data-testid="stMarkdownContainer"] p {color: #c8d0db;}
            [data-testid="stCaptionContainer"] {color: var(--muted-2);}
            .kpi-card {
              background: linear-gradient(180deg, var(--panel), var(--panel-2));
              border: 1px solid var(--border-soft);
              border-radius: 11px;
              padding: 0.8rem 0.95rem;
              min-height: 88px;
              box-shadow: 0 2px 14px rgba(3, 7, 18, 0.2);
              transition: border-color .15s ease, transform .15s ease, box-shadow .15s ease;
            }
            .kpi-card:hover {border-color: #334159; transform: translateY(-1px); box-shadow: 0 8px 24px rgba(3, 7, 18, 0.28);}
            .kpi-label {font-size: 0.73rem; color: var(--muted); margin-bottom: 0.28rem; text-transform: uppercase; letter-spacing: .05em;}
            .kpi-value {font-size: 1.5rem; line-height: 1.1; font-weight: 640; color: var(--text);}
            .kpi-hint {font-size: 0.72rem; color: var(--muted-2); margin-top: 0.28rem;}
            .pipeline-card {
              background: var(--bg-soft);
              border: 1px solid var(--border-soft);
              border-radius: 10px;
              padding: 0.58rem 0.72rem;
              margin-bottom: 0.48rem;
              box-shadow: 0 1px 8px rgba(2, 6, 16, 0.18);
            }
            .pipeline-company {font-weight: 620; margin-bottom: 0.15rem;}
            .pipeline-role {color: #cbd2dc; margin-bottom: 0.2rem; font-size: 0.92rem;}
            .pipeline-meta {font-size: 0.78rem; color: var(--muted);}
            .status-pill {
              display: inline-block;
              border-radius: 999px; padding: 0.12rem 0.5rem; border: 1px solid transparent; font-size: 0.72rem;
              font-weight: 520;
              background: #1a2231; color: #c8d2df;
            }
            .status-applied, .status-submitted {border-color: #344c66; color: #a6c0df; background: rgba(97, 133, 175, 0.14);}
            .status-interviewing, .status-offer {border-color: #325243; color: #a2ccb3; background: rgba(93, 149, 119, 0.14);}
            .status-rejected, .status-failed {border-color: #61414a; color: #d4adb4; background: rgba(163, 98, 114, 0.13);}
            .status-draft, .status-review-needed, .status-queued {border-color: #4f4d60; color: #c4bbcf; background: rgba(121, 112, 145, 0.12);}

            [data-testid="stDataFrame"], [data-testid="stDataEditor"], [data-testid="stTable"] {
              border: 1px solid var(--border-soft);
              border-radius: 10px;
              overflow: hidden;
              background: var(--panel);
            }
            [data-testid="stDataEditor"] [role="grid"],
            [data-testid="stDataFrame"] [role="grid"] {
              background: var(--panel) !important;
              color: var(--text) !important;
            }
            [data-testid="stDataEditor"] [role="columnheader"],
            [data-testid="stDataFrame"] [role="columnheader"] {
              background: var(--panel-3) !important;
              color: var(--muted) !important;
              border-bottom: 1px solid var(--border-soft) !important;
              font-size: 0.74rem !important;
              text-transform: uppercase;
              letter-spacing: .03em;
            }
            [data-testid="stDataEditor"] [role="gridcell"],
            [data-testid="stDataFrame"] [role="gridcell"] {
              background: var(--panel) !important;
              border-bottom: 1px solid rgba(255,255,255,0.04) !important;
              color: #d6dde8 !important;
              font-size: 0.86rem !important;
            }
            [data-testid="stDataEditor"] [role="row"]:hover [role="gridcell"],
            [data-testid="stDataFrame"] [role="row"]:hover [role="gridcell"] {
              background: #1a2332 !important;
            }
            [data-baseweb="select"] > div, [data-baseweb="input"] > div, .stTextInput > div > div {
              background: var(--panel) !important;
              border: 1px solid var(--border-soft) !important;
              border-radius: 9px !important;
              color: var(--text) !important;
            }
            [data-baseweb="tag"] {
              background: #233047 !important;
              border: 1px solid #2f415f !important;
              color: #bdd1eb !important;
              border-radius: 999px !important;
              font-size: 0.72rem !important;
            }
            [data-testid="stSidebar"] {background: #0f141d; border-right: 1px solid var(--border-soft);}
            [data-testid="stExpander"] {border: 1px solid var(--border-soft); border-radius: 10px; background: var(--panel);}
            hr {border-color: rgba(255,255,255,0.07);}
            div[data-testid="stVerticalBlock"] > div:has(> div > .kpi-card) {gap: 0.6rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    workspace_root = resolve_workspace()
    csv_path = workspace_root / "logs" / "applications_log.csv"

    st.markdown(
        f"""
        <div class="app-header">
          <div class="app-header-row">
            <div>
              <div class="brand-title">Apply<span class="accent">Chain</span></div>
              <div class="brand-subtitle">AI-Assisted Recruiting Workflow System</div>
              <div class="brand-meta">Created by ApplyChain User · Local-First Job Application Operations</div>
            </div>
            <div class="header-badges">
              <span class="header-pill ok">● Local Mode</span>
              <span class="header-pill">Workspace: {workspace_root}</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
