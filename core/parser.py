# parser.py
import os
import subprocess
from pathlib import Path


def convert_profraw_to_profdata(profraw_path: Path, profdata_path: Path):
    subprocess.run([
        "llvm-profdata", "merge",
        "-sparse", str(profraw_path),
        "-o", str(profdata_path)
    ], check=True)


def show_coverage_report(target_binary: Path, profdata_path: Path, output_path: Path = None):
    command = [
        "llvm-cov", "show",
        str(target_binary),
        f"-instr-profile={profdata_path}"
    ]
    if output_path:
        with open(output_path, 'w') as f:
            subprocess.run(command, stdout=f, check=True)
    else:
        subprocess.run(command, check=True)


def export_coverage_summary(target_binary: Path, profdata_path: Path) -> str:
    command = [
        "llvm-cov", "report",
        str(target_binary),
        f"-instr-profile={profdata_path}"
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, check=True, text=True)
    return result.stdout
