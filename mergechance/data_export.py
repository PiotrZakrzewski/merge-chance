

from typing import List
from typing import List
from mergechance.analysis import ANALYSIS_FIELDS


def prep_tsv(prs:List) -> str:
    """Create a tsv content with pr data."""
    rows = [
        ['author'] + ANALYSIS_FIELDS,
        ]
    for pr in prs:
        author_login = pr['author']['login'] if pr['author'] else ''
        row = [author_login]
        fields = [str(pr.get(field, '')) for field in ANALYSIS_FIELDS]
        row.extend(fields)
        rows.append(row)
    lines = ["\t".join(row) for row in rows]
    return "\n".join(lines)
