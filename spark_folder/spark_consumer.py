from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, FloatType, IntegerType, StringType, ArrayType
from pyspark.sql.functions import from_json, col, explode
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import pandas as pd
import json
import os

# Carrega configurações do InfluxDB do arquivo JSON
config_path = os.path.join(os.path.dirname(__file__), 'influx_config.json')
with open(config_path) as config_file:
    influx_config = json.load(config_file)

# Configurações do InfluxDB
INFLUXDB_URL = influx_config['INFLUXDB_URL']
INFLUXDB_TOKEN = influx_config['INFLUXDB_TOKEN']
INFLUXDB_ORG = "projeto_f1_stream"
INFLUXDB_BUCKET = "weather_metrics"

def write_to_influxdb(df, epoch_id):
    try:
        print(f"\n=== Processando batch {epoch_id} ===")
        
        with InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG
        ) as client:
            write_api = client.write_api(write_options=SYNCHRONOUS)
            
            for row in df.collect():
                try:
                    timestamp = pd.to_datetime(row.date).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                    
                    point = Point("clima") \
                        .tag("corrida", str(row.meeting_key)) \
                        .tag("sessao", str(row.session_key)) \
                        .field("temperatura", float(row.air_temperature)) \
                        .field("umidade", float(row.humidity)) \
                        .field("pressao", float(row.pressure)) \
                        .field("chuva", float(row.rainfall)) \
                        .field("temp_pista", float(row.track_temperature)) \
                        .field("dir_vento", int(row.wind_direction)) \
                        .field("vel_vento", float(row.wind_speed)) \
                        .time(timestamp)
                    
                    write_api.write(bucket=INFLUXDB_BUCKET, record=point)
                except Exception as row_error:
                    print(f"Erro ao escrever ponto no InfluxDB: {row_error}")
        
        print(f"=== Batch {epoch_id} processado com sucesso ===")
        
    except Exception as e:
        print(f"Erro no processamento do batch {epoch_id}: {e}")


# Configuração do Spark
spark = SparkSession.builder \
    .appName("ClimaConsumer") \
    .master("spark://spark-master:7077") \
    .config("spark.executor.memory", "512m") \
    .config("spark.executor.cores", "1") \
    .config("spark.driver.memory", "512m") \
    .config("spark.cores.max", "1") \
    .config("spark.driver.host", "spark-master") \
    .config("spark.driver.bindAddress", "0.0.0.0") \
    .getOrCreate()

# Schema para um único registro
record_schema = StructType() \
    .add("air_temperature", FloatType()) \
    .add("date", StringType()) \
    .add("humidity", FloatType()) \
    .add("meeting_key", IntegerType()) \
    .add("pressure", FloatType()) \
    .add("rainfall", FloatType()) \
    .add("session_key", IntegerType()) \
    .add("track_temperature", FloatType()) \
    .add("wind_direction", IntegerType()) \
    .add("wind_speed", FloatType())

array_schema = ArrayType(record_schema)

# Ler do Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "weather_data") \
    .option("startingOffsets", "earliest") \
    .load()

# Processar os dados
parsed_df = df.selectExpr("CAST(value AS STRING) as json_string") \
    .select(from_json(col("json_string"), array_schema).alias("data")) \
    .select(explode(col("data")).alias("weather")) \
    .select("weather.*")

# Configurar o nível de log do Spark
spark.sparkContext.setLogLevel("WARN")

# Enviar para o InfluxDB
query = parsed_df \
    .writeStream \
    .foreachBatch(write_to_influxdb) \
    .outputMode("append") \
    .start()

print("Stream iniciado, aguardando dados...")

try:
    query.awaitTermination()
except KeyboardInterrupt:
    print("Stream interrompido pelo usuário.")
except Exception as stream_error:
    print(f"Erro no stream: {stream_error}")

