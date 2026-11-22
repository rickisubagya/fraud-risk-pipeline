from datetime import timedelta

import pendulum
from airflow.sdk import dag, task


@dag(
    dag_id="fx_rate_pipeline",
    schedule="0 8 * * *",
    start_date=pendulum.datetime(2026, 11, 14, tz="Asia/Jakarta"),
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=2)},
    tags=["fraud-risk", "fx"],
)
def fx_rate_pipeline():
    @task
    def fetch():
        from src.extract.fetch_fx_rate import fetch_fx_rate

        return fetch_fx_rate()

    @task
    def validate_rate(data: dict):
        from src.load.load_fx_rate import validate

        validate(data)
        return data

    @task
    def save(data: dict):
        from src.load.load_fx_rate import save_fx_rate

        save_fx_rate(data)

    save(validate_rate(fetch()))


fx_rate_pipeline()