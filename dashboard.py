import argparse
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st


STATUSES = ["applied", "interviewing", "rejected", "offer"]
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

    df = pd.read_csv(path)
    for col in ["date", "company", "role", "status", "match_score", "notes", "jd_url", "resume_file"]:
        if col not in df.columns:
            df[col] = pd.NA

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["match_score"] = pd.to_numeric(df["match_score"], errors="coerce")
    df["status"] = df["status"].astype("string").str.lower().fillna("applied")
    return df


def save_status_updates(df: pd.DataFrame, csv_path: Path) -> None:
    if "date" in df.columns:
        out = df.copy()
        out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    else:
        out = df
    out.to_csv(csv_path, index=False)


def render_stats(df: pd.DataFrame) -> None:
    total = len(df)
    responded = df["status"].isin(["interviewing", "offer"]).sum() if total else 0
    response_rate = (responded / total * 100) if total else 0
    avg_match = df["match_score"].mean() if total else 0

    last_applied_days = None
    if total and df["date"].notna().any():
        last_date = df["date"].max()
        last_applied_days = (pd.Timestamp.now().normalize() - last_date.normalize()).days

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Applied", f"{total}")
    c2.metric("Response Rate", f"{response_rate:.1f}%")
    c3.metric("Avg Match Score", f"{avg_match:.1f}")
    c4.metric("Days Since Last Application", "N/A" if last_applied_days is None else str(last_applied_days))


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
                    f"<div style='padding:0.5rem;border:1px solid #333;border-radius:8px;margin-bottom:0.5rem'>"
                    f"<div><b>{row.get('company', '')}</b></div>"
                    f"<div>{row.get('role', '')}</div>"
                    f"<div style='font-size:0.85rem;color:#9aa0a6'>{date_str} · Match: {score}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )


def render_log_table(df: pd.DataFrame, csv_path: Path) -> pd.DataFrame:
    st.subheader("Application Log")
    filter_status = st.multiselect("Filter by status", options=STATUSES, default=STATUSES)
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
            "status": st.column_config.SelectboxColumn("status", options=STATUSES, required=True),
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
    st.markdown(f"**Status:** {row.get('status', '')}")
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
            .stApp {background-color: #0f1117; color: #e6e6e6;}
            [data-testid="stMetricValue"] {color: #f1f3f4;}
            [data-testid="stMetricLabel"] {color: #aab0b6;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    workspace_root = resolve_workspace()
    csv_path = workspace_root / "logs" / "applications_log.csv"

    st.title("Job Applications Dashboard")
    st.caption(f"Workspace root: {workspace_root}")

    df = load_applications(str(csv_path))

    render_stats(df)
    st.divider()
    render_pipeline(df)
    st.divider()
    filtered = render_log_table(df, csv_path)
    st.divider()
    render_detail_drawer(filtered, workspace_root)


if __name__ == "__main__":
    main()
