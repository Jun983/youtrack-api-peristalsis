"""Issue ID helpers."""

import re

_DB_ID_RE = re.compile(r"^\d+-\d+$")


def resolve_issue_id(issue_id: str, prefix: str | None) -> str:
    """Resolve a short issue number to a full idReadable using the project prefix.

    YouTrack issue IDs use the format {prefix}-{number} (no -A- segment).

    Examples (prefix=XAC):
        "42"       -> "XAC-42"   (number only)
        "XAC-42"   -> "XAC-42"   (already correct: unchanged)
        "226-0"    -> "226-0"    (database id: unchanged)
    """
    issue_id = issue_id.strip()
    if _DB_ID_RE.fullmatch(issue_id):
        return issue_id
    if not prefix:
        return issue_id

    prefix = prefix.strip()
    upper_id = issue_id.upper()
    upper_prefix = prefix.upper()

    # Already in correct format: {prefix}-{number}
    if re.fullmatch(re.escape(upper_prefix) + r"-\d+", upper_id):
        return issue_id

    # Pure number
    if issue_id.isdigit():
        return f"{prefix}-{issue_id}"

    return issue_id
