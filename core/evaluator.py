import subprocess
from pathlib import Path 

class CoverageEvaluator:
    def __init__(self, profraw_dir: Path, coverage_binary: Path, output_dir: Path):
        self.profraw_dir = profraw_dir 
        self.coverage_binary = coverage_binary 
        self.output_dir = output_dir

    def merge_profiles(self):
        profraw_files = list(self.profraw_dir.glob("*.profraw"))
        if not profraw_files:
            raise RuntimeError("No .profraw files found!")

        merged_path = self.output_dir / "merged.profdata"
        cmd = ["llvm-profdata", "merge", "-sparse", "-o", str(merged_path)] + [str(p) for p in profraw_files]
        subprocess.run(cmd, check=True)
        return merged_path 

    def generate_report(self, merge_profdata: Path):
        cmd = [
                "llvm-cov", "report", 
                str(self.coverage_binary),
                f"-instr-profile={merge_profdata}"
                ] 
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout 

    def extract_line_coverage(self, report_output: str) -> float:
        for line in report_output.splitlines():
            if "TOTAL" in line:
                #ex TOTAL 188 65 34.5%
                parts = line.split()
                if len(parts) >= 4:
                    return float(parts[3].strip('%'))
        return 0.0

    def evaluate(self):
        print("Merging coverage profiles...")
        merged = self.merge_profiles()
        print("Generating coverage report...")
        report  = self.generate_report(merged)
        coverage = self.extract_line_coverage(report)
        print(f"[DONE] Line coverage: {coverage:.2f}%")
        return coverage 

    
