"""Article ID helpers."""

import re

_DB_ID_RE = re.compile(r"^\d+-\d+$")


def resolve_article_id(article_id: str, prefix: str | None) -> str:
    """Resolve a short article number to a full idReadable using the project prefix.

    Examples (prefix=XAC):
        "13"     -> "XAC-13"
        "XAC-13" -> "XAC-13" (unchanged)
        "226-0"  -> "226-0" (database id, unchanged)
        "NP-A-1" -> "NP-A-1" (other format, unchanged)
    """
    article_id = article_id.strip()
    if not prefix:
        return article_id

    prefix = prefix.strip()
    if article_id.upper().startswith(prefix.upper() + "-"):
        return article_id
    if _DB_ID_RE.fullmatch(article_id):
        return article_id
    if article_id.isdigit():
        return f"{prefix}-{article_id}"

    return article_id
