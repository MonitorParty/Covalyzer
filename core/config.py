#hi
from dataclasses import dataclass 
from enum import Enum 
from pathlib import Path 
from core.modes import CoverageMode

@dataclass 
class CovalyzerConfig:
    db_path: Path 
    output_dir: Path 
    coverage_binary: Path 
    mode: CoverageMode 


