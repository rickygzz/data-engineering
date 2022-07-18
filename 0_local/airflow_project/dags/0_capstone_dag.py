# Capstone Project
# Data Engineering bootcamp Jun 2022 - Aug. 2022
#
# GOAL: Create and end-to-end solution.
#   Data Engineer must configure the environment and resources, integrate the
#   data from external sources and clean the data and process it for their
#   further analysis. When the data is ready, transform it to reflect business
#   rules and deliver knowledge in the form of insights.
#
# Project stack:
#   - Cloud service:    AWS
#   - Orchestration:    Airflow
#   - Data processing:  EMR
#   - Storage:          S3, RDS, Redshift
#   - Intermediate steps: Athena
#   - CI/CD:            Bash shell / Terraform
#   - Serverless:       Glue / Athena / Lambda
#   - Streaming:        Kafka / Kinesis

# VARIABLES

POSTGRES_CONN_ID = "postgres_conn_id"
POSTGRES_USER_PURCHASE_TABLE = "public.user_purchase"

# Use urlopen in case you want to download from URL
# from urllib.request import urlopen

import pandas as pd


def sqlescape(text: str):
    return text.replace("'", "''").replace("\\", "\\\\")

def load_user_purchase_data(
    url: str,
    postgres_conn_id: str,
    iFrom: int,
    iCount: int
):
    """Ingest data from a CSV into a postgres table.

    Args:
        url (str):              An URL pointing to a CSV file.
        postgres_conn_id (str): Name of the postgres connection ID.
        iFrom (int):            From which row index. Starts from 0.
        iCount (int):           How many rows to ingest from iFrom.
    """    
    # local_filename = urlopen(file).read()
    df = pd.read_csv(url)

    # TODO: check if CSV has the required columns and datatypes
    # df.info ()

    if (iFrom > len(df)):
        return
    elif (iFrom + iCount > len(df)):
        iCount = len(df) - iFrom

    sSql = f"INSERT INTO {POSTGRES_USER_PURCHASE_TABLE} (invoice_number, stock_code, detail, quantity, invoice_date, unit_price, customer_id, country) VALUES "

    for x in range(iFrom, iFrom + iCount):
        sSql = sSql + f"('{sqlescape(df.loc[x, 'InvoiceNo'])}', '{sqlescape(df.loc[x, 'StockCode'])}', '{sqlescape(df.loc[x, 'Description'])}', {df.loc[x, 'Quantity']}, '{df.loc[x, 'InvoiceDate']}', {df.loc[x, 'UnitPrice']}, {df.loc[x, 'CustomerID']}, '{sqlescape(df.loc[x, 'Country'])}'), "

    # Remove last 2 characters if needed
    if (sSql.endswith(", ")):
        sSql = sSql[:-2]

    print(sSql)

    psql_hook = PostgresHook(postgres_conn_id)
    
    psql_hook.run(sql = sSql)

    # TODO: Check if it is possible to ingest with .to_sql()
    # df.to_sql(name = POSTGRES_USER_PURCHASE_TABLE, con = psql_hook.get_conn(), chunksize = 1000)

    # This returns a psycopg2.connect() object
    # conn = psql_hook.get_conn()



# def ingest_data_from_s3(
#     s3_bucket: str,
#     s3_key: str,
#     postgres_table: str,
#     aws_conn_id: str = "aws_default",
#     postgres_conn_id: str = "postgres_default",
# ):
#     """Ingest data from an S3 location into a postgres table.
#
#     Args:
#         s3_bucket (str): Name of the s3 bucket.
#         s3_key (str): Name of the s3 key.
#         postgres_table (str): Name of the postgres table.
#         aws_conn_id (str): Name of the aws connection ID.
#         postgres_conn_id (str): Name of the postgres connection ID.
#     """
#     s3_hook = S3Hook(aws_conn_id=aws_conn_id)
#     psql_hook = PostgresHook(postgres_conn_id)
#     local_filename = s3_hook.download_file(key=s3_key, bucket_name=s3_bucket)
#     psql_hook.bulk_load(table=postgres_table, tmp_file=local_filename)


from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# PostgresOperator and PostgresHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator

with DAG(
    dag_id='0_capstone_project',
    schedule_interval='0 0 * * *',
    start_date=datetime(2022, 7, 9, 2),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=['CAPSTONE'],
    #params={"example_key": "example_value"},
) as dag:
    capstone_start = EmptyOperator(
        task_id='capstone_start',
    )

    # Validate data is located where is expected to be
    capstone_validate = EmptyOperator(
        task_id='capstone_validate',
    )

    # Prepare our database to have the necessary tables
    capstone_prepare = EmptyOperator(
        task_id='capstone_prepare',
    )

    # DAG
    # 1. Import CSV user_purchase.csv -> user_purchase table in PostgreSQL
    # 1b. Create a PostgreSQL table with the following columns:
    #       InvoiceNo   -> invoice_number
    #       StockCode   -> stock_code
    #       Description -> detail
    #       Quantity    -> quantity
    #       InvoiceDate -> invoice_date
    #       UnitPrice   -> unit_price
    #       CustomerID  -> customer_id
    #       Country     -> country
    create_table_user_purchase = PostgresOperator(
        task_id = "create_table_user_purchase",
        postgres_conn_id = POSTGRES_CONN_ID,
        sql = "sql/user_purchase_schema.sql",
    )

    # Clear all user_purchase records.
    clear_table_user_purchase = PostgresOperator(
        task_id = "clear_table_user_purchase",
        postgres_conn_id = POSTGRES_CONN_ID,
        sql = f"DELETE FROM {POSTGRES_USER_PURCHASE_TABLE}",
    )

    # Load the data into the DB.
    capstone_load = EmptyOperator(
        task_id='capstone_load',
    )

    ingest_data_user_purchase = PythonOperator(
        task_id="ingest_data_user_purchase",
        python_callable = load_user_purchase_data,
        op_kwargs = {
            "url": "http://5vertice.com/capstone/user_purchase_1000.csv",
            "postgres_conn_id": POSTGRES_CONN_ID,
            "iFrom": 0,
            "iCount": 10,
            "postgres_table": POSTGRES_USER_PURCHASE_TABLE,
        },
        # python_callable=ingest_data_from_s3,
        # op_kwargs={
        #     "aws_conn_id": AWS_CONN_ID,
        #     "postgres_conn_id": POSTGRES_CONN_ID,
        #     "s3_bucket": S3_BUCKET_NAME,
        #     "s3_key": S3_KEY_NAME,
        #     "postgres_table": POSTGRES_TABLE_NAME,
        # },
        # trigger_rule=TriggerRule.ONE_SUCCESS,
    )

    capstone_end = EmptyOperator(
        task_id='capston_end',
    )

    (
        capstone_start >> capstone_validate >>
        capstone_prepare >> create_table_user_purchase >>
        clear_table_user_purchase >>
        capstone_load >> ingest_data_user_purchase >>
        capstone_end
    )

    # Airflow variables
# https://www.astronomer.io/blog/secrets-management-airflow-2/
# https://github.com/astronomer/webinar-secrets-management/tree/master

# String de conección

# Crear una bucket S3 para los CSV
# Editar el terraform para que suba los 3 CSV  -- se pueden subir manualmente
# Airflow corre a spark

# DAG
# 2. Import CSV movie_review.csv -> classified_movie_review table in PostgreSQL
# 2b. Use AI to detect if comment is possitive or not. 
# 2c. Create a PostgreSQL table with the following columns:
#       cid         -> customer_id
#                   -> is_possitive (check transform)
#       id_review   -> review_id

# DAG
# 3. Import CSV log_reviews.csv -> review_logs table in PostgreSQL
# 3b. Parse XML data
# 3c. Create a PostgreSQL table with the following columns:
#   **  id_review                     -> log_id
#       log_data                      -> log_data
#       xml:reviewlog/log/device      -> device
#       xml:reviewlog/log/os          -> os
#       xml:reviewlog/log/location    -> location
#   **  xml:reviewlog/log/            -> browser**
#       xml:reviewlog/log/ipAddress   -> ip
#       xml:reviewlog/log/phoneNumber -> phone_number

# DATawarehouse separado

# Build a data pipeline to populate the fact_movie_analytics table (OLAP table)
# This table is useful for analysts and tools like dashboard software.


