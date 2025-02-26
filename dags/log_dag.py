from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.hooks.postgres_hook import PostgresHook
import csv
import os

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
}


def load_order_details(**kwargs):
    execution_date = kwargs['ds']
    table_name = 'order_details'
    file_path = f"data/csv/{execution_date}/order_details_{execution_date}.csv"

    hook = PostgresHook(postgres_conn_id='northwind_conn')
    conn = hook.get_conn()
    cursor = conn.cursor()

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS order_details (
        order_id INT,
        product_id INT,
        unit_price DECIMAL,
        quantity INT,
        discount DECIMAL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
    );
    """
    cursor.execute(create_table_sql)

    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            placeholders = ', '.join(['%s'] * len(row))
            insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
            cursor.execute(insert_sql, row)

    conn.commit()
    cursor.close()
    conn.close()


with DAG(
        'log_dag',
        default_args=default_args,
        schedule_interval='@daily',
        catchup=False,
) as dag:
    load_order_details_task = PythonOperator(
        task_id='load_order_details',
        python_callable=load_order_details,
    )

    load_order_details_task
