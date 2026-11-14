"""
Analysis History management module.
Stores, retrieves, and clears resume analysis records with summary statistics.
"""
import os
import json
import pandas as pd
from datetime import datetime

HISTORY_FILE = os.path.join("data", "history.csv")
HISTORY_DETAILS_FILE = os.path.join("data", "history_details.json")


def save_history(filename, ats_score, job_score, matching_skills="", missing_skills="", analysis_raw=""):
    """
    Save an analysis record to CSV and detailed archive.

    Parameters:
        filename (str): Resume filename.
        ats_score (int): ATS Compatibility Score.
        job_score (int): Job Match Score.
        matching_skills (str): Matching skills list/string.
        missing_skills (str): Missing skills list/string.
        analysis_raw (str): Full text analysis.
    """
    os.makedirs("data", exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    new_record = {
        "Date": date_str,
        "Resume": filename,
        "ATS Score": int(ats_score),
        "Job Match Score": int(job_score)
    }

    # Save to history.csv for table display
    if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 0:
        try:
            history_df = pd.read_csv(HISTORY_FILE)
        except Exception:
            history_df = pd.DataFrame(columns=["Date", "Resume", "ATS Score", "Job Match Score"])
    else:
        history_df = pd.DataFrame(columns=["Date", "Resume", "ATS Score", "Job Match Score"])

    history_df = pd.concat([history_df, pd.DataFrame([new_record])], ignore_index=True)
    history_df.to_csv(HISTORY_FILE, index=False)

    # Save detailed payload to json archive
    details = []
    if os.path.exists(HISTORY_DETAILS_FILE) and os.path.getsize(HISTORY_DETAILS_FILE) > 0:
        try:
            with open(HISTORY_DETAILS_FILE, "r", encoding="utf-8") as f:
                details = json.load(f)
        except Exception:
            details = []

    details.append({
        "id": len(details) + 1,
        "date": date_str,
        "resume": filename,
        "ats_score": int(ats_score),
        "job_score": int(job_score),
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "raw_analysis": analysis_raw
    })

    try:
        with open(HISTORY_DETAILS_FILE, "w", encoding="utf-8") as f:
            json.dump(details, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save detailed history json: {e}")


def get_history():
    """
    Load analysis history as a pandas DataFrame.

    Returns:
        pd.DataFrame: DataFrame containing history records, or empty DataFrame.
    """
    if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 0:
        try:
            df = pd.read_csv(HISTORY_FILE)
            if not df.empty:
                # Ensure numeric types
                df["ATS Score"] = pd.to_numeric(df["ATS Score"], errors="coerce").fillna(0).astype(int)
                df["Job Match Score"] = pd.to_numeric(df["Job Match Score"], errors="coerce").fillna(0).astype(int)
            return df
        except Exception:
            return pd.DataFrame(columns=["Date", "Resume", "ATS Score", "Job Match Score"])
    return pd.DataFrame(columns=["Date", "Resume", "ATS Score", "Job Match Score"])


def get_history_stats():
    """
    Calculate summary statistics from the history records.

    Returns:
        dict: Total count, average ATS score, average Job Match score, highest ATS score.
    """
    df = get_history()
    if df.empty:
        return {
            "total_count": 0,
            "avg_ats": 0,
            "avg_job_match": 0,
            "highest_ats": 0,
            "highest_job_match": 0
        }

    return {
        "total_count": len(df),
        "avg_ats": int(round(df["ATS Score"].mean())),
        "avg_job_match": int(round(df["Job Match Score"].mean())),
        "highest_ats": int(df["ATS Score"].max()),
        "highest_job_match": int(df["Job Match Score"].max())
    }


def get_detailed_history():
    """
    Retrieve full detailed history list from JSON storage.
    """
    if os.path.exists(HISTORY_DETAILS_FILE) and os.path.getsize(HISTORY_DETAILS_FILE) > 0:
        try:
            with open(HISTORY_DETAILS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def clear_history():
    """
    Delete all stored history records.
    """
    for file_path in [HISTORY_FILE, HISTORY_DETAILS_FILE]:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
