from datetime import timedelta

import pendulum
from airflow.sdk import dag, task


def notify_failure(context):
    from src.notify import ping_heartbeat, send_telegram

    ti = context.get("task_instance")
    task_id = getattr(ti, "task_id", "unknown")
    send_telegram(
        f"Airflow FAILED: task '{task_id}' in fx_rate_pipeline. Check the Airflow UI."
    )
    ping_heartbeat("/fail")


@dag(
    dag_id="fx_rate_pipeline",
    schedule="0 8 * * *",
    start_date=pendulum.datetime(2026, 11, 14, tz="Asia/Jakarta"),
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
        "on_failure_callback": notify_failure,
    },
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
        return data

    @task
    def report(data: dict):
        from src.notify import ping_heartbeat, send_telegram

        send_telegram(
            f"Airflow OK: 1 USD = {data['rate']} IDR on {data['date']}"
        )
        ping_heartbeat()

    @task
    def quality_check(data: dict):
        from src.quality import check_fx_quality

        check_fx_quality()
        return data

    report(quality_check(save(validate_rate(fetch()))))


fx_rate_pipeline()