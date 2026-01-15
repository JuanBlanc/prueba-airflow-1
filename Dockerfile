FROM apache/airflow:slim-3.1.6-python3.12

USER root
COPY requirements.txt /tmp/requirements.txt
RUN chown airflow:root /tmp/requirements.txt

USER airflow
RUN pip install --no-cache-dir -r /tmp/requirements.txt
