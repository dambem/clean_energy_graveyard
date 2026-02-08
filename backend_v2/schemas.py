from pydantic import BaseModel


class NimbyScore(BaseModel):
    header: str
    nimby_score: int
    accuracy_score: int
    petty_score: int
    organized_score: int
    political_leaning: int
    interesting_tidbits: list[str]
    snide_commentary: str


class ProjectScore(NimbyScore):
    """NimbyScore attached to a specific REPD project."""
    refid: str
    article_url: str
