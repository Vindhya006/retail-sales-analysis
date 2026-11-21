from pathlib import Path
import subprocess
import sys
import time

PROJECT_DIR = Path(__file__).resolve().parent

SCRIPTS = [
    "prepare_data.py",
    "load_database.py",
    "analyze_sales.py",
    "sql_analysis.py",
]


def main():
    start = time.perf_counter()

    for script in SCRIPTS:
        script_path = PROJECT_DIR / script

        if not script_path.is_file():
            print(f"Missing script: {script}", flush=True)
            return 1

    for script in SCRIPTS:
        print(f"\n--- Running {script} ---", flush=True)

        try:
            subprocess.run(
                [sys.executable, str(PROJECT_DIR / script)],
                cwd=PROJECT_DIR,
                check=True
            )
        except subprocess.CalledProcessError as error:
            print(
                f"\nPipeline stopped: {script} failed "
                f"with exit code {error.returncode}.",
                flush=True
            )
            return 1

    elapsed = time.perf_counter() - start
    print(f"\nPipeline completed successfully in {elapsed:.2f} seconds.")
    print("CSV reports were regenerated. Excel still needs a manual refresh.")
    return 0


if __name__ == "__main__":
    sys.exit(main())