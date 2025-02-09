import yaml
import logging
import argparse
from functools import partial
from pyspark.sql.functions import lit
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

parser = argparse.ArgumentParser(
    description="Extracts raw data from the source and stores it in the raw catalog."
)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

parser.add_argument("--owner", "-o", type=str, help="The owner of this pipeline.")
parser.add_argument(
    "--environment", "-e", type=str, help="Bundle target environment: dev or prod"
)
parser.add_argument(
    "--first_modified_date",
    "-d",
    type=str,
    default="",
    help="First modified date for extraction.",
)
parser.add_argument(
    "--lag", "-l", type=int, default=7, help="Number of past days for data extraction."
)

args = parser.parse_args()


def read_yaml_file(filepath: str) -> dict:
    """
    Read a yaml file and return a dictionary.

    Args:
        filepath (str): The path to acces the yaml file.

    Returns:
        dict : A dictionary with the content of the yaml file.
    """
    try:
        with open(filepath, "r") as f:
            yaml_data = yaml.safe_load(f)
            return yaml_data
    except FileNotFoundError:
        logging.error(f"Error: file not fount at {filepath}")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Error parsin YAML: {e}")
        raise


def extract_data(
    table_name: str,
    catalog: str,
    schema: str,
    first_modified_date: str,
    environment: str,
) -> None:
    """
    A function to extract data from a table.

    Args:
        table_name (str): The table name in the database.
        catalog (str): Databricks catalog for extracted data.
        schema (str): Schema to save the data.
        first_modified_date (str): First modified date for extraction.
        environment (str): Task execution environment: dev or prod
    """
    # Define the destination path
    delta_table_name = f"{catalog}.{environment}_raw_{schema}.raw_{table_name}"
    logging.info(f"Extracting data to: {table_name}")

    # Query to select data according with the ModifiedDate column
    query = f"(SELECT * FROM {schema}.{table_name} WHERE ModifiedDate >= '{first_modified_date}') AS subquery"

    # Read data from the database
    df = spark.read.jdbc(url=jdbc_url, table=query, properties=connection_properties)

    # Insert a column into the dataframe with the extraction date
    df = df.withColumn("extract_date", lit(datetime.today()))

    # Save the df into the destination path
    logging.info(f"Saving data into: {delta_table_name}")
    df.write.mode("overwrite").format("delta").saveAsTable(delta_table_name)
    logging.info("Successfully loaded raw data into destination table.")


if __name__ == "__main__":
    owner = args.owner
    environment = args.environment
    first_modified_date = args.first_modified_date
    lag_days = args.lag

    parameters = read_yaml_file("tables_mapping.yaml")

    if parameters:
        logging.info("Successfully loaded YAML data.")
        database = parameters["database"]
        schema = parameters["schema"]
        tables_list = list(parameters["tables"].keys())
        catalog = f"{owner}_raw"
        db_password = dbutils.secrets.get(scope=f"{owner}_adw", key="pswd_mssql")
        db_host = dbutils.secrets.get(scope=f"{owner}_adw", key="ip_mssql")
        db_port = dbutils.secrets.get(scope=f"{owner}_adw", key="port_mssql")
        db_user = dbutils.secrets.get(scope=f"{owner}_adw", key="user_mssql")

        if not len(first_modified_date):
            first_modified_date = datetime.today() - timedelta(days=lag_days)
            first_modified_date = first_modified_date.strftime("%Y-%m-%d 00:00:00")

        logging.info(f"First modified data to extraction: {first_modified_date}")

        jdbc_url = f"jdbc:sqlserver://{db_host}:{db_port};databaseName={database};encrypt=true;trustServerCertificate=true;"

        connection_properties = {
            "user": db_user,
            "password": db_password,
            "driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver",
        }

        extract_data_partial = partial(
            extract_data,
            catalog=catalog,
            schema=schema,
            first_modified_date=first_modified_date,
            environment=environment,
        )

        with ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(extract_data_partial, tables_list)

        logging.info("Extraction finished.")
