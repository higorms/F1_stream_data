from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, FloatType, IntegerType, StringType, ArrayType
from pyspark.sql.functions import from_json, col, explode

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

# Schema para o array de registros
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

# Saída final com as colunas renomeadas
query = parsed_df \
    .select(
        col("air_temperature").alias("Temperatura_do_Ar"),
        col("date").alias("Data"),
        col("humidity").alias("Umidade"),
        col("pressure").alias("Pressao"),
        col("rainfall").alias("Chuva"),
        col("track_temperature").alias("Temperatura_da_Pista"),
        col("wind_direction").alias("Direcao_do_Vento"),
        col("wind_speed").alias("Velocidade_do_Vento")
    ) \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

# Aguardar o término
query.awaitTermination()
