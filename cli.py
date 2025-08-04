# cli.py
import argparse
from core.config import CovalyzerConfig, CoverageMode 
from pathlib import Path



def parse_args():
    parser = argparse.ArgumentParser(description="🧪 Covalyzer - Evaluate coverage from AFL++ runs!")

    parser.add_argument("--db", required=True, help="Path to the SQLite testcase database")
    parser.add_argument("--bin", required=True, help="Path to the coverage-enabled binary")
    parser.add_argument("--out", required=True, help="Directory to store temporary files and coverage results")
    parser.add_argument("--mode", choices=[m.value for m in CoverageMode], default="all",
                        help="Coverage mode: what input set and restart behavior to simulate")

    args = parser.parse_args()

    return CovalyzerConfig(
            db_path = Path(args.db),
            coverage_binary = Path(args.bin),
            output_dir = Path(args.out),
            mode = CoverageMode(args.mode)
            )
