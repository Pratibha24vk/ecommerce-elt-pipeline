# 🛒 E-commerce ELT Pipeline

A production-grade, end-to-end ELT pipeline built on the modern data stack. Ingests raw e-commerce data from the [Brazilian Olist dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), lands it in Snowflake, transforms it with dbt, and orchestrates everything with Apache Airflow.

---

## 🏗️ Architecture

```
[Olist CSV / API]
       │
       ▼
[Python Ingestion Layer]
       │   (raw files → cloud storage)
       ▼
[Snowflake — RAW schema]
       │
       ▼
[dbt — Staging → Intermediate → Marts]
       │
       ▼
[Snowflake — ANALYTICS schema]
       │
       ▼
[Power BI / Tableau Dashboard]
```

---

## 🧰 Tech Stack

| Layer | Tool |
|---|---|
| Orchestration | Apache Airflow 2.x |
| Ingestion | Python (pandas, boto3) |
| Data Warehouse | Snowflake |
| Transformation | dbt Core |
| Data Quality | dbt Tests + Great Expectations |
| Visualization | Power BI / Tableau |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions |

---

## 📁 Project Structure

```
ecommerce-elt-pipeline/
├── dags/
│   └── ecommerce_pipeline.py       # Airflow DAG definition
├── ingestion/
│   └── extract_olist.py            # Raw data ingestion script
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml.example
│   ├── macros/
│   │   └── generate_schema_name.sql
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_orders.sql
│   │   │   ├── stg_customers.sql
│   │   │   ├── stg_order_items.sql
│   │   │   └── stg_products.sql
│   │   └── marts/
│   │       ├── fct_orders.sql
│   │       ├── dim_customers.sql
│   │       └── rpt_customer_ltv.sql
│   ├── tests/
│   │   └── assert_positive_revenue.sql
│   └── schema.yml
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .github/
│   └── workflows/
│       └── dbt_ci.yml
├── requirements.txt
└── README.md
```

---

## 📊 Data Models

### Staging Layer
Cleans and standardizes raw source tables. One staging model per source table. No joins.

### Marts Layer
- **fct_orders** — Grain: one row per order. Includes revenue, status, timestamps, and delivery SLA flags.
- **dim_customers** — Customer attributes enriched with city/state geolocation.
- **rpt_customer_ltv** — Aggregated LTV, AOV, order frequency, and recency per customer (RFM model).

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Snowflake account (free trial works)
- Python 3.10+

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/ecommerce-elt-pipeline.git
cd ecommerce-elt-pipeline
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Fill in your Snowflake credentials, AWS keys, etc.
```

### 3. Start Airflow
```bash
docker-compose up -d
# Visit http://localhost:8080 — user: airflow / pass: airflow
```

### 4. Configure dbt
```bash
cp dbt/profiles.yml.example ~/.dbt/profiles.yml
# Edit with your Snowflake credentials
pip install -r requirements.txt
cd dbt && dbt debug
```

### 5. Run the pipeline
Trigger the `ecommerce_elt_pipeline` DAG in Airflow UI, or run manually:
```bash
cd dbt
dbt run
dbt test
dbt docs generate && dbt docs serve
```

---

## ✅ dbt Tests Included
- `not_null` and `unique` on all primary keys
- `accepted_values` on order status
- Custom test: `assert_positive_revenue` — ensures no negative revenue rows exist
- Relationship tests between fact and dimension tables

---

## 📈 Key Metrics Produced
| Metric | Description |
|---|---|
| GMV | Gross Merchandise Value by month |
| AOV | Average Order Value |
| Customer LTV | 12-month rolling LTV per customer |
| Delivery SLA % | % of orders delivered on time |
| Repeat Purchase Rate | % of customers with 2+ orders |

---

## 🔄 CI/CD
GitHub Actions runs `dbt compile`, `dbt test`, and linting on every pull request to `main`.

---

## 📚 Resources
- [dbt Documentation](https://docs.getdbt.com)
- [Olist Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- [Snowflake Free Trial](https://signup.snowflake.com/)
- [Airflow Docs](https://airflow.apache.org/docs/)
