import os
from typing import Any


def get_weekly_web_stats() -> dict[str, int] | None:
    property_id = os.getenv("GA4_PROPERTY_ID", "").strip()
    if not property_id:
        return None

    private_key = os.getenv("GOOGLE_PRIVATE_KEY", "").strip()
    client_email = os.getenv("GOOGLE_CLIENT_EMAIL", "").strip()

    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import DateRange, Metric, RunReportRequest
        from google.oauth2 import service_account
    except Exception:
        return None

    try:
        if private_key and client_email:
            info = {
                "type": "service_account",
                "private_key": private_key.replace("\\n", "\n"),
                "client_email": client_email,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            credentials = service_account.Credentials.from_service_account_info(
                info,
                scopes=["https://www.googleapis.com/auth/analytics.readonly"],
            )
            client = BetaAnalyticsDataClient(credentials=credentials)
        else:
            client = BetaAnalyticsDataClient()
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
            metrics=[
                Metric(name="totalUsers"),
                Metric(name="sessions"),
                Metric(name="screenPageViews"),
            ],
        )
        response = client.run_report(request)
    except Exception:
        return None

    if not response.rows:
        return {"users": 0, "sessions": 0, "pageviews": 0}

    values: list[Any] = response.rows[0].metric_values
    try:
        users = int(values[0].value)
        sessions = int(values[1].value)
        pageviews = int(values[2].value)
    except Exception:
        return None

    return {"users": users, "sessions": sessions, "pageviews": pageviews}
