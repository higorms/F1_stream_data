# Use uma imagem base oficial do Spark com Hadoop e Java
FROM bitnami/spark:3.4.0

# Copiar o script consumidor para o contêiner
COPY spark_folder/spark_consumer.py /app/

# Instalar dependências do sistema
USER root
RUN apt-get update && apt-get install -y wget \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Instalar o PySpark
RUN pip3 install pyspark

# Adicionar os conectores Kafka necessários
RUN wget -P /opt/bitnami/spark/jars/ https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.4.0/spark-sql-kafka-0-10_2.12-3.4.0.jar \
    && wget -P /opt/bitnami/spark/jars/ https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.4.0/spark-token-provider-kafka-0-10_2.12-3.4.0.jar \
    && wget -P /opt/bitnami/spark/jars/ https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.4.0/kafka-clients-3.4.0.jar \
    && wget -P /opt/bitnami/spark/jars/ https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar

# Configurar variáveis de ambiente do Spark
ENV SPARK_HOME=/opt/bitnami/spark
ENV PATH=$SPARK_HOME/bin:$PATH
ENV PYSPARK_PYTHON=python3