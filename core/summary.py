# summary.py
import re
from typing import Dict


def parse_coverage_summary(summary_text: str) -> Dict[str, float]:
    """
    Parses `llvm-cov report` output and returns a dict with key coverage metrics.
    """
    metrics = {}
    lines = summary_text.splitlines()
    for line in lines:
        # Match coverage lines like:
        # "TOTAL                             243     40    83.52%       231       37    83.14%"
        if line.startswith("TOTAL"):
            parts = re.split(r"\s+", line)
            if len(parts) >= 7:
                try:
                    metrics["functions"] = float(parts[3].replace('%', ''))
                    metrics["lines"] = float(parts[6].replace('%', ''))
                except ValueError:
                    pass
    return metrics
