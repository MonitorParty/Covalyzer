import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple

from core.config import CovalyzerConfig 
from core.database import DatabaseConnector
from core.modes import CoverageMode


class CoverageRunner:
    def __init__(self, config: CovalyzerConfig):
        self.config = config
        self.db = DatabaseConnector(str(config.db_path))
        self.output_dir = Path(config.output_dir) 
        self.coverage_bin = str(config.coverage_binary)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _write_testcases_to_tempdir(self, testcases: List[Tuple[int, bytes]]): 
        """Write TCs inputs to individual files in a temp dir"""
        tempdir = tempfile.TemporaryDirectory(dir="/dev/shm")
        temp_path = Path(tempdir.name)

        for idx, (tc_id, data) in enumerate(testcases):
            with open(temp_path / f"id_{tc_id}", "wb") as f:
                f.write(data)

        return temp_path, tempdir

    def _run_coverage_binary(self, input_dir: Path, output_profraw: Path):
        """Run the covbin in libFuzzer-style mode"""
        env = os.environ.copy()
        env["LLVM_PROFILE_FILE"] = str(output_profraw)

        cmd = [
                self.coverage_bin,
                "-merge=1",
                "-dump_coverage=1",
                str(input_dir),
                str(input_dir)
                ]
        try:
            subprocess.run(cmd, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f"Error during coverage run: {e.stderr.decode()}")

    def run_all_testcases_stateless(self, batch_size: int = 1000):
        """Runs all TCs from DB in batches (stateless)"""
        print(f"Running coverage mode in: {self.config.mode}")
        offset = 0
        while True:
            print(" Fetching from db...")
            testcases = self.db.fetch_testcases(offset, batch_size, only_queue=False)
            if not testcases:
                break 

            print(f"Running batch: {offset} » {offset +len(testcases) - 1}")
            print(" Writing to RAM...")
            #write to ram 
            input_dir, tmp = self._write_testcases_to_tempdir(testcases)

            print(" Running binary...")
            #run binary
            profraw_path = self.output_dir / f"batch_{offset}.profraw"
            self._run_coverage_binary(input_dir, profraw_path)

            print(" Cleaning...")
            tmp.cleanup()
            offset += len(testcases)

        print("Finished cov run! :)")

    def run_fuzzbench_mode(self):
        snapshot_data = self.db.fetch_queue_snapshots()
        output_dir  = self.output_dir 
        coverage_bin = self.coverage_bin 

        for bucket, tcs in sorted(snapshot_data.items()):
            print(f"Running snapshot bucket {bucket} with {len(tcs)} testcases")

            #write to RAM 
            print(" Writing to RAM...")
            input_dir, tmp = self._write_testcases_to_tempdir(tcs)

            #2 run cov bin 
            profraw_path = self.output_dir / f"snapshot_{bucket}.profraw"
            print(" Running binary...")
            self._run_coverage_binary(input_dir, profraw_path)

            #3 clean clean clean 
            print(" Cleaning....")
            tmp.cleanup()

        print("Finished with FuzzBench-Mode! :)")

        #write files to snapshot dir 

    def run(self):
        print(f"🧪 Starting coverage run in mode: {self.config.mode.name}")
        if "RESTART" in self.config.mode.name.upper():
            self._run_with_restarts()
        else:
            self._run_flat()

    def _run_with_restarts(self):
        restart_ids = self.db.fetch_restarts()


        #we assume ids are logged after restart, so prepend 0 as first start
        boundaries = [0] + restart_ids
        boundaries.append(float("inf")) #marker for end


        for i in range(len(boundaries) - 1):
            start_id = boundaries[i]
            end_id = boundaries[i + 1]

            testcases = self.db.fetch_testcases(start_id, end_id, only_queue=self._queue_only())
            if not testcases:
                continue

            profraw_path = self.profraw_dir / f"segment_{i}.profraw"
            print(f"⚙️  Running segment {i}: IDs {start_id} → {end_id} ({len(testcases)} TCs)")

            env = os.environ.copy()
            env["LLVM_PROFILE_FILE"] = str(profraw_path)

            # Start the binary and stream testcases via stdin
            proc = subprocess.Popen(
                [str(self.config.coverage_binary)],
                stdin=subprocess.PIPE,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            for tid, value in testcases:
                try:
                    proc.stdin.write(value)
                except Exception as e:
                    print(f"⚠️ Error writing input {tid}: {e}")

            proc.stdin.close()
            proc.wait()

        print("✅ Finished restart-segmented coverage run")

    def _run_flat(self):
        offset = 0
        batch_size = 1000

        while True:
            testcases = self.db.fetch_testcases(offset, batch_size, only_queue=self._queue_only())
            if not testcases:
                break

            for tid, value in testcases:
                profraw_path = self.profraw_dir / f"input_{tid}.profraw"
                env = os.environ.copy()
                env["LLVM_PROFILE_FILE"] = str(profraw_path)

                subprocess.run(
                    [str(self.config.coverage_binary)],
                    input=value,
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            offset += batch_size

        print(f"✅ Finished flat coverage run")

    def _queue_only(self):
        return self.config.mode in [CoverageMode.QUEUE_ONLY, CoverageMode.QUEUE_WITH_RESTARTS]

    def close(self):
        self.db.close()

