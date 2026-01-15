# Prueba Airflow

Pequeno entorno de Airflow 2.10.3 basado en Docker Compose. Incluye PostgreSQL como base de metadatos, servicios de webserver y scheduler, y un DAG de ejemplo `hello_world`.

## Contenido del repositorio
- `docker-compose.yml`: orquestacion de Postgres y los servicios de Airflow.
- `dags/hello_world_dag.py`: DAG sencillo que imprime "Hello World!" a diario.
- `Dockerfile` y `requirements.txt`: definen la imagen personalizada de Airflow con librerias adicionales (por ejemplo scikit-learn).
- `.env.example`: plantilla con todas las variables que usa Docker Compose (copia a `.env` y edita si quieres otros valores).
- Directorios montados (`dags`, `logs`, `plugins`, `config`) para desarrollar desde el host.

## Requisitos previos
- Docker y Docker Compose Plug-in instalados.

## Como ejecutar
1. Crea tu archivo `.env` local:
   ```bash
   cp .env.example .env
   ```
   Ajusta los valores si necesitas distintos usuarios o puertos.
2. Construye la imagen personalizada con las dependencias declaradas en `requirements.txt`:
   ```bash
   docker compose build
   ```
3. Inicializa la base de datos y crea el usuario admin:
   ```bash
   docker compose up airflow-init
   ```
   Cuando termine correctamente puedes detenerlo con `Ctrl+C`.
4. Arranca el resto de servicios en segundo plano:
   ```bash
   docker compose up -d postgres airflow-webserver airflow-scheduler
   ```
5. Abre `http://localhost:8080`, inicia sesion con las credenciales definidas en `.env` (por defecto `admin / admin`) y activa el DAG `hello_world` para ver la salida en los logs.

## Detener servicios
```bash
docker compose down
```

Esto eliminara los contenedores pero mantendra el volumen `postgres-db-volume` para no perder datos.
