k# Anime Watchlist ETL Pipeline

End-to-end data pipeline: CSV → Docker → AWS S3 Data Lake

## Architecture

CSV Files (raw data)
↓
Docker ETL Container (pandas + psycopg2)
↓
PostgreSQL Container (local development)
↓
AWS S3 Bronze Layer (raw storage)
↓ (Glue ETL — coming soon)
AWS S3 Silver Layer (cleaned Parquet)
↓ (dbt — coming soon)
AWS S3 Gold Layer (aggregated analytics)
↓ (Tableau — coming soon)
Dashboard

## Pipeline Steps

**Extract** — Reads 3 CSV files (anime, genre, anime_genre)

**Transform** — Cleans data:
- Type conversions (numeric, float, int)
- Whitespace stripping and lowercase normalization
- NULL handling with None replacement
- Duplicate removal
- Range validation (episodes > 0)

**Load** — Inserts into PostgreSQL in foreign key order:
1. genre (no dependencies)
2. anime (no dependencies)
3. anime_genre (depends on both)

## Docker Setup

Multi-stage Dockerfile — builder installs dependencies,
runner copies only what's needed. Reduces image size.

```bash
docker compose up --build
```

Two services:
- postgres (official image, named volume for persistence)
- etl (custom multi-stage image, bind mount for CSV access)

## AWS Data Lake

Bucket: shivaram-data-pipeline-001

IAM: data-pipeline-user (least privilege — S3 + Glue + RDS only)

## Tech Stack

- Python, Pandas, psycopg2
- PostgreSQL
- Docker, Docker Compose (multi-stage builds)
- AWS S3, AWS IAM
- AWS Glue, Athena, Tableau (coming soon)

## Run Locally

```bash
docker compose up --build
```

## Run on AWS

```bash
aws s3 cp anime_data.csv s3://shivaram-data-pipeline-001/bronze/anime/anime_data.csv
aws s3 cp genre_data.csv s3://shivaram-data-pipeline-001/bronze/anime/genre_data.csv
aws s3 cp anime_genre_data.csv s3://shivaram-data-pipeline-001/bronze/anime/anime_genre_data.csv
```
