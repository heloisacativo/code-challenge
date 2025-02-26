from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.hooks.postgres_hook import PostgresHook
import os
import csv
import shutil
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 28),
    'retries': 1,
}

def export_orders(**kwargs):
    execution_date = kwargs['ds']
    table_name = 'orders'

    hook = PostgresHook(postgres_conn_id='northwind_conn')
    conn = hook.get_conn()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]

    execution_date_formatted = datetime.strptime(execution_date, "%Y-%m-%d").strftime('%Y-%m-%d')
    dir_path = f"/opt/airflow/data/postgres/{table_name}/{execution_date_formatted}"


    file_path = f"{dir_path}/{table_name}_{execution_date_formatted}.csv"

    os.makedirs(dir_path, exist_ok=True)
    if os.path.exists(file_path):
        print(f"[INFO] File already exists: {file_path} nothing has changed")
        return

    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(colnames)
        writer.writerows(rows)

    cursor.close()
    conn.close()


def copy_order_details(**kwargs):
    execution_date = kwargs['ds']

    source_path = "data/order_details.csv"
    dest_dir = f"data/csv/{execution_date}"
    os.makedirs(dest_dir, exist_ok=True)

    dest_path = f"{dest_dir}/order_details_{execution_date}.csv"

    if os.path.exists(dest_path):
        print(f"[INFO] File already exists: {dest_path} nothing has changed")
        return

    if not os.path.exists(source_path):
        raise FileNotFoundError(
            f"[ERROR] The source file {source_path} was not found!"
        )

    shutil.copy(source_path, dest_path)
    print(f"[INFO] File copied to: {dest_path}.")


with DAG(
        'extract_dag',
        default_args=default_args,
        schedule_interval='@daily',
        catchup=False
) as dag:
    export_orders_task = PythonOperator(
        task_id='export_orders',
        python_callable=export_orders,
    )

    copy_order_details_task = PythonOperator(
        task_id='copy_order_details',
        python_callable=copy_order_details,
    )

    export_orders_task >> copy_order_details_task
