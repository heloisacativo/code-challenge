import argparse
import subprocess


def run_extract_dag():
    print("[INFO] Triggering the extract DAG ('extract_dag')")
    result = subprocess.run(["airflow", "dags", "trigger", "extract_dag"],
                            capture_output=True, text=True)
    if result.returncode == 0:
        print("[INFO] extract_dag triggered successfully")
    else:
        print("[ERROR] Failed to trigger extract_dag")
        print(result.stderr)


def run_log_dag():
    print("[INFO] Triggering the log DAG ('log_dag')")
    result = subprocess.run(["airflow", "dags", "trigger", "log_dag"],
                            capture_output=True, text=True)
    if result.returncode == 0:
        print("[INFO] log_dag triggered successfully")
    else:
        print("[ERROR] Failed to trigger log_dag")
        print(result.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="ETL Pipeline: Data Extraction, File Copying, and Data Logging Orchestrated by Airflow"
    )

    parser.add_argument('-a', '--all', action='store_true', help="Run the entire pipeline (extraction and logging).")
    parser.add_argument('-e', '--extract', action='store_true', help="Trigger only the extraction DAG ('extract_dag').")
    parser.add_argument('-l', '--log', action='store_true',
                        help="Trigger only the logging DAG ('log_dag').")

    args = parser.parse_args()

    if args.all:
        print("[INFO] Starting the entire pipeline...")
        run_extract_dag()
        run_log_dag()
    elif args.extract:
        run_extract_dag()
    elif args.log:
        run_log_dag()
    else:
        print("No operation specified. Use the '-h' option for more details.")


if __name__ == '__main__':
    main()
