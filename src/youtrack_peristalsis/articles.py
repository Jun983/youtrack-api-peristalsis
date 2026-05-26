"""Article ID helpers."""

import re

_DB_ID_RE = re.compile(r"^\d+-\d+$")


def resolve_article_id(article_id: str, prefix: str | None) -> str:
    """Resolve a short article number to a full idReadable using the project prefix.

    YouTrack Knowledge Base article IDs use the format {prefix}-A-{number}.

    Examples (prefix=XAC):
        "13"       -> "XAC-A-13"  (number only)
        "XAC-13"   -> "XAC-A-13"  (missing -A-)
        "XAC-A-13" -> "XAC-A-13"  (already correct: unchanged)
        "226-0"    -> "226-0"     (database id: unchanged)
    """
    article_id = article_id.strip()
    if _DB_ID_RE.fullmatch(article_id):
        return article_id
    if not prefix:
        return article_id

    prefix = prefix.strip()
    upper_id = article_id.upper()
    upper_prefix = prefix.upper()

    # Already in correct format: {prefix}-A-{number}
    if re.fullmatch(re.escape(upper_prefix) + r"-A-\d+", upper_id):
        return article_id

    # Pure number
    if article_id.isdigit():
        return f"{prefix}-A-{article_id}"

    # {prefix}-{number} without -A- (e.g. XAC-13 -> XAC-A-13)
    m = re.fullmatch(re.escape(upper_prefix) + r"-(\d+)", upper_id)
    if m:
        return f"{prefix}-A-{m.group(1)}"

    return article_id
