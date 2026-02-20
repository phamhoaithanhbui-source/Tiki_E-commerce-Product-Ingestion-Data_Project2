# Tiki E-commerce Product Ingestion Data Pipeline

High-throughput asynchronous data ingestion pipeline designed to process 200,000 product records from Tiki's public API using a modular ETL architecture.
## Project Overview

This project demonstrates a scalable API ingestion system built with:

* Asynchronous I/O (`aiohttp`, `asyncio`)
* Configurable concurrency control
* Batch-oriented storage
* Retry strategy with exponential backoff
* Clean ETL separation (Extract–Transform–Load)

The pipeline reads 200,000 product IDs, fetches product details, cleans descriptions, and stores results into structured JSON batches.

---

# System Architecture

```
Input CSV (200k IDs)
        ↓
Async Extract Layer (aiohttp + concurrency control)
        ↓
Transform Layer (HTML cleaning & normalization)
        ↓
Batch Storage (JSON)
        ↓
Error Segregation
        ↓
Retry Stage (Optional)
```

---

## Architectural Principles

### 1️) Separation of Concerns

* `fetcher.py` → API ingestion
* `transformer.py` → Data normalization
* `writer.py` → Storage handling
* `main.py` → Orchestration
* `retry.py` → Reprocess failed records
* `config.py` → Centralized configuration

---

### 2) Asynchronous I/O

* Built with `aiohttp` + `asyncio`
* Non-blocking requests
* Semaphore-controlled concurrency (`CONCURRENCY_LIMIT = 40`)
* Chunk-based task scheduling (`CHUNK_SIZE = 100`)
* Exponential backoff for rate limiting (HTTP 429)

---

### 3️) Batch Writing

* 1000 records per JSON file (`BATCH_SIZE = 1000`)
* Prevents memory overload
* Avoids single large file risk
* Enables easier downstream processing
* Does not generate empty output files

---

### 4️) Error Handling Strategy

* Timeout protection (`REQUEST_TIMEOUT = 5`)
* Configurable retries (`MAX_RETRIES = 3`)
* Exponential backoff (`2^attempt`)
* HTTP status-based error handling
* Failed IDs stored separately for retry

---

# Project Structure

```
tiki-data-pipeline/
│
├── data/
│   ├── input/
│   │   └── product_ids.csv
│   │
│   └── processed/
│       ├── jsonfile/
│       │   ├── products_001.json
│       │   └── retry_001.json
│       │
│       └── errorfile/
│           ├── errors_001.json
│           └── retry_001.json
│
├── logs/
│   └── pipeline.log
│
├── src/
│   ├── config.py
│   ├── fetcher.py
│   ├── transformer.py
│   ├── writer.py
│   ├── __main__.py
│   └── __retry_errors__.py
│
├── requirements.txt
└── README.md
```

---

# Configuration

All parameters are centralized in `config.py`:

* API endpoint
* Concurrency limit
* Retry attempts
* Timeout
* Batch size
* File paths

This allows tuning system performance without modifying logic.

---

# Estimated Runtime (200,000 Records)

| Method                 | Estimated Time |
| ---------------------- | -------------- |
| Sequential requests    | ~2–4 hours     |
| Async (concurrency=40) | ~30–45 minutes |

> Actual performance depends on network latency and API throttling.

---

# Installation

### 1️) Clone repository

```
git clone https://github.com/yourusername/tiki-data-pipeline.git
cd tiki-data-pipeline
```

---

### 2️) Install dependencies

```
pip install -r requirements.txt
```

---

### 3️) Run pipeline

```
python src/__main__.py
```

---

### 4️) Retry failed records (optional)

```
python src/__retry_erorrs__.py
```

---

# Future Improvements

* Parquet output format
* S3 integration
* Database loading stage
* Airflow orchestration
* Distributed ingestion scaling
* Monitoring dashboard
* Resume checkpoint support

---

# Author

Pham Hoai Thanh Bui-
Data Engineering Enthusiast
