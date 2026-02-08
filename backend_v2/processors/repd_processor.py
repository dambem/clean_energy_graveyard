from pathlib import Path
import pandas as pd
from .base import BaseProcessor

REFUSED_STATUSES = [
    "Application Refused",
    "Abandoned",
    "Application Withdrawn",
    "Appeal Refused",
]

IN_PROGRESS_STATUSES = [
    "Application Submitted",
    "Revised",
    "Awaiting Construction",
    "No Application Required",
    "Under Construction",
]


class RepdProcessor(BaseProcessor):
    """Processor for UK Renewable Energy Planning Database CSV exports."""

    DATE_COLUMNS = [
        "Planning Application Submitted",
        "Planning Permission Refused",
        "Planning Application Withdrawn",
        "Appeal Refused",
        "Record Last Updated (dd/mm/yyyy)",
    ]

    def __init__(self, file_path: Path, encoding: str = "cp1252"):
        super().__init__(file_path, encoding)

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse dates, normalise capacity, fill NaN."""
        df = df.copy()
        for col in self.DATE_COLUMNS:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format="%d/%m/%Y", errors="coerce")
        df["Installed Capacity (MWelec)"] = (
            pd.to_numeric(df["Installed Capacity (MWelec)"], errors="coerce").fillna(0)
        )
        return df

    def get_refused(self, df: pd.DataFrame | None = None) -> pd.DataFrame:
        """Filter to refused/withdrawn/abandoned applications only."""
        df = df if df is not None else self.df
        return self.filter_by_column(df, "Development Status (short)", REFUSED_STATUSES)

    def get_in_progress(self, df: pd.DataFrame | None = None) -> pd.DataFrame:
        """Filter to applications still in progress."""
        df = df if df is not None else self.df
        return self.filter_by_column(df, "Development Status (short)", IN_PROGRESS_STATUSES)

    def filter_by_county(self, df: pd.DataFrame, county: str) -> pd.DataFrame:
        return self.filter_by_column(df, "County", [county])

    def filter_by_authority(self, df: pd.DataFrame, authorities: list[str]) -> pd.DataFrame:
        return self.filter_by_column(df, "Planning Authority", authorities)

    def calculate_processing_stats(self, df: pd.DataFrame) -> list[dict]:
        """Calculate average delay and time distribution grouped by year."""
        df = df.copy()
        submitted = "Planning Application Submitted"
        refused = "Planning Permission Refused"

        mask = df[submitted].notna() & df[refused].notna()
        df = df[mask]
        df["days_to_decision"] = (df[refused] - df[submitted]).dt.days
        df["year"] = df[submitted].dt.year

        buckets = [
            (0, 90), (90, 180), (180, 270), (270, 360),
            (360, 450), (450, 540), (540, 630), (630, 720),
            (720, 810), (810, 900),
        ]

        stats = []
        for year, group in df.groupby("year"):
            days = group["days_to_decision"]
            distribution = []
            for lo, hi in buckets:
                distribution.append({
                    "range": f"{lo}-{hi} days",
                    "count": int(((days >= lo) & (days < hi)).sum()),
                })
            distribution.append({
                "range": "Over 900 days",
                "count": int((days >= 900).sum()),
            })
            stats.append({
                "year": int(year),
                "avgDelay": round(days.mean(), 1),
                "distribution": distribution,
            })
        return stats
