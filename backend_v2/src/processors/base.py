from abc import ABC, abstractmethod
from pathlib import Path
import json
import pandas as pd


class BaseProcessor(ABC):
    """Base class for tabular data processors.

    Subclasses define how to load, clean, and filter a specific dataset.
    All filter/transform methods follow the pattern:
        take a DataFrame -> return a new DataFrame (no mutation)
    """

    def __init__(self, file_path: Path, encoding: str = "utf-8"):
        self.file_path = file_path
        self.encoding = encoding
        self._df: pd.DataFrame | None = None

    @property
    def df(self) -> pd.DataFrame:
        """Lazy-load: data isn't read until first access."""
        if self._df is None:
            self._df = self.load()
        return self._df

    def load(self) -> pd.DataFrame:
        """Default CSV loader. Override for other formats (parquet, API, etc.)."""
        return pd.read_csv(self.file_path, encoding=self.encoding)

    @abstractmethod
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Dataset-specific cleaning. Must be implemented by subclasses."""
        ...

    def filter_by_column(self, df: pd.DataFrame, column: str, values: list) -> pd.DataFrame:
        """Generic filter: keep rows where column value is in the given list."""
        return df[df[column].isin(values)]

    def filter_by_date(self, df: pd.DataFrame, column: str, after: str) -> pd.DataFrame:
        """Keep rows where date column is after the given date string."""
        df = df.copy()
        df[column] = pd.to_datetime(df[column], errors="coerce")
        return df[df[column] >= pd.to_datetime(after)]

    def drop_columns(self, df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        """Return df without the specified columns. Never mutates input."""
        return df.drop(columns=[c for c in columns if c in df.columns])

    def add_metadata_column(
        self, df: pd.DataFrame, keep_columns: list[str], meta_column: str = "metadata"
    ) -> pd.DataFrame:
        """Collapse all columns NOT in keep_columns into a single JSON metadata field."""
        other_cols = [c for c in df.columns if c not in keep_columns]
        df = df.copy()
        df[meta_column] = df.apply(
            lambda row: json.dumps(
                {col: row[col] for col in other_cols if pd.notna(row[col])},
                default=str,
            ),
            axis=1,
        )
        return df[keep_columns + [meta_column]]
