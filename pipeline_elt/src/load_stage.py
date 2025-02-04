import yaml 
import logging
import argparse
from pyspark.sql import DataFrame
from pyspark.sql.functions import lit
from delta.tables import DeltaTable
from functools import partial
from concurrent.futures import ThreadPoolExecutor

parser = argparse.ArgumentParser(description="Ingest stage data into the staging catalog.")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

parser.add_argument("--owner", "-o", type=str, help="The owner of this pipeline.")
parser.add_argument("--environment", "-e", type=str, help="Bundle target environment: dev or prod")

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


def read_df(catalog: str, schema: str, table_name: str, ) -> DataFrame:
    """
    Reads data from a specified table in a Databricks catalog and returns a PySpark DataFrame.

    This function retrieves data from a given table and loads it into a DataFrame for further analysis or processing.
    It assumes that the necessary SparkSession is already configured and accessible.

    Args:
        catalog (str): The name of the Databricks catalog.
        schema (str): The schema within the catalog where the table resides.
        table_name (str): The name of the table to read data from.

    Returns:
        A PySpark DataFrame containing the data from the specified table.
    """
    spark.sql(f"USE CATALOG {catalog}")
    df = spark.table(f"{catalog}.{schema}.{table_name}")
    return df

def load_stg_df(stg_df: DataFrame, catalog: str, schema: str, table_name: str) -> None:
    """
    Loads transformed data into a staging table in a Databricks catalog.

    This function takes a PySpark DataFrame (`stg_df`) containing transformed data and writes it 
    to a specified table in a staging schema within a Databricks catalog. 

    Args:
        stg_df (DataFrame): The PySpark DataFrame containing the transformed data to be loaded.
        catalog (str): The name of the Databricks catalog where the staging schema resides.
        schema (str): The name of the staging schema within the catalog.
        table_name (str): The name of the table within the staging schema to load the data into.
    """
    spark.sql(f"USE CATALOG {catalog}")
    stg_df.write.format("delta").mode("append").saveAsTable(f"{catalog}.{schema}.{table_name}_stg")


def rename_columns(df: DataFrame, columns_map: dict) -> DataFrame:
    """
    Renames columns in a PySpark DataFrame according to a provided mapping.
 
    This function takes a PySpark DataFrame and a dictionary that maps existing column names
    to new column names. It returns a new DataFrame with the columns renamed as specified.

    Args:
        df (DataFrame): The PySpark DataFrame whose columns need to be renamed.
        columns_map (dict): A dictionary where the keys are the current column names 
                            and the values are the new column names.

    Returns:
        df (DataFrame): A new PySpark DataFrame with the columns renamed according to the mapping.
    """
    df = df.select(list(columns_map.keys()))
    for original, alias in columns_map.items():
        df = df.withColumnRenamed(original, alias)
    
    return df

def insert_origin_columns(df: DataFrame, schema: str, database: str = "adventure_works") -> DataFrame:
    """
    Inserts source identification columns into a PySpark DataFrame.

    This function adds two new columns to the DataFrame to track the origin of the data. One to identify
    the source database, and another to identify the department reponsible for the data.

    Args:
        df (DataFrame): The PySpark DataFrame to which the source columns will be added.
        schema (str): The schema name of the data, used to infer the department.
        database (str): The name of the source database. Defaults to "adventure_works".
    """

    df = df.withColumn("source_name", lit(database))\
           .withColumn("source_departament", lit(schema))
    return df


def ingest_data(table_name:str, schema:str, raw_catalog:str, stg_catalog:str, tables_mapping: dict) -> None:
    """
    Ingests transformed data from the raw catalog to the staging catalog.

    This function orchestrates the process of extracting data from the raw catalog,
    applying transformations based on the provided mapping, and loading the 
    transformed data into the specified table within the staging catalog.

    Args:
        table_name (str): The name of the table, consistent across the raw and staging catalogs.
        schema (str): The name of the schema where the table resides in both catalogs.
        raw_catalog (str): The name of the catalog containing the raw data (source).
        stg_catalog (str): The name of the catalog where the transformed data will be stored (target).
        tables_mapping (str): A dictionary defining the column mappings and transformations.     
    """

    logging.info(f"Runing to table: {table_name}")
    raw_df = read_df(raw_catalog, schema, table_name, environment)

    if raw_df.count():
        columns_map = tables_mapping[table_name]["stg_columns"]
        stg_df = rename_columns(raw_df, columns_map)
        stg_df = insert_origin_columns(stg_df, schema)
        stg_table_name = f"{stg_catalog}.{environment}_stg_{schema}.{tables_mapping[table_name]['stg_name']}_stg"
    
        table_exists = spark.catalog.tableExists(stg_table_name)

        if table_exists:
            primary_key_columns = tables_mapping[table_name]["primary_key"]
            delta_table = DeltaTable.forName(spark, stg_table_name)
            
            merge_condition = " AND ".join([f"target.{col} = source.{col}" for col in primary_key_columns])
            
            # Perform the merge operation if the table exists
            delta_table.alias("target").merge(
                stg_df.alias("source"),
                merge_condition
            ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
        else:
            # Create the Delta table if it doesn't exist
            stg_df.write.format("delta").saveAsTable(stg_table_name)
    else:
        logging.info('Nothing to update')

if __name__ == "__main__":
    owner = args.owner
    environment = args.environment

    parameters = read_yaml_file("tables_mapping.yaml")

    if parameters:
        logging.info("Successfully loaded YAML data.")
        database =  parameters["database"]
        schema = parameters["schema"]
        raw_catalog = f"{owner}_raw"
        stg_catalog = f"{owner}_stg"
        tables_list = list(parameters["tables"].keys())
        tables_mapping = parameters["tables"]

        ingest_data_partial = partial(ingest_data,
                                      schema=schema,
                                      raw_catalog=raw_catalog,
                                      stg_catalog=stg_catalog,
                                      tables_mapping=tables_mapping,
                                      environment=environment)


        with ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(ingest_data_partial, tables_list)
        
        logging.info("Ingestion finished.")
