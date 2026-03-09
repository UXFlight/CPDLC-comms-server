import os
from typing import Any

from app.classes.logging import log_error, log_user_action
from app.classes.logging.telegram_notifier import send_telegram_message_sync
from app.services.analytics_event_store import clear_events
from app.services.analytics_service import AnalyticsService
from app.services.google_analytics_service import get_weekly_web_stats


def _format_percentage(value: Any) -> str:
    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return "0.00%"


def _format_duration(seconds: Any) -> str:
    try:
        total = int(float(seconds))
    except (TypeError, ValueError):
        return "0s"
    minutes, sec = divmod(max(total, 0), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {sec}s"
    return f"{sec}s"


def format_weekly_report(stats: dict[str, Any], web_stats: dict[str, int] | None = None) -> str:
    lines = [
        "Weekly CPDLC System Report",
        "",
        f"Users this week: {stats.get('users_this_week', 0)}",
        f"Routes started: {stats.get('routes_started', 0)}",
        f"Routes completed: {stats.get('routes_completed', 0)}",
        f"Completion rate: {_format_percentage(stats.get('route_completion_rate', 0))}",
        "",
        f"Average route completion: {_format_percentage(stats.get('average_route_completion_pct', 0))}",
        "",
        f"Events processed: {stats.get('events_processed', 0)}",
        f"Errors: {stats.get('errors', 0)}",
        f"Error rate: {_format_percentage(stats.get('error_rate', 0))}",
        "",
        "Top Countries",
    ]

    top_countries = stats.get("top_countries") or []
    if not top_countries:
        lines.append("🌍 Unknown -- 0")
    else:
        for entry in top_countries:
            flag = entry.get("flag") or "🌍"
            name = entry.get("name") or "Unknown"
            users = entry.get("users", 0)
            lines.append(f"{flag} {name} -- {users}")

    lines.extend(
        [
            "",
            "Operational Health",
            f"Average events/hour: {stats.get('average_events_per_hour', 0)}",
            f"Active sessions: {stats.get('active_sessions', 0)}",
            f"Peak active sessions: {stats.get('peak_active_sessions', 0)}",
            f"CPDLC events: {stats.get('cpdlc_events', 0)}",
            f"Failed operations: {stats.get('failed_operations', 0)}",
            f"Reconnections: {stats.get('reconnections', 0)}",
            f"Average session duration: {_format_duration(stats.get('average_session_duration_sec', 0))}",
        ]
    )

    if web_stats:
        lines.extend(
            [
                "",
                "Web Analytics (Google Analytics)",
                f"Web users: {web_stats.get('users', 0)}",
                f"Sessions: {web_stats.get('sessions', 0)}",
                f"Pageviews: {web_stats.get('pageviews', 0)}",
            ]
        )

    return "\n".join(lines)


def generate_and_send_weekly_report() -> bool:
    log_user_action("-", "analytics_report_job_started")
    try:
        stats = AnalyticsService().compute_weekly_stats()
    except Exception as e:
        log_error(None, "analytics_computation_error", e)
        return False

    web_stats = get_weekly_web_stats()
    log_user_action(
        "-",
        "analytics_report_computed",
        users=stats.get("users_this_week", 0),
        events=stats.get("events_processed", 0),
        errors=stats.get("errors", 0),
        has_ga=bool(web_stats),
    )
    report_text = format_weekly_report(stats, web_stats=web_stats)

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    channel_id = os.getenv("TELEGRAM_CHANNEL_ID", "").strip()
    if not token or not channel_id:
        log_error(None, "analytics_report_failed", "telegram_not_configured")
        return False

    ok, reason = send_telegram_message_sync(report_text)
    if not ok:
        log_error(
            None,
            "analytics_report_failed",
            reason or "telegram_send_failed",
            channel_id=channel_id,
        )
        return False

    try:
        log_user_action(
            "-",
            "analytics_report_sent",
            users=stats.get("users_this_week", 0),
            events=stats.get("events_processed", 0),
            errors=stats.get("errors", 0),
            channel_id=channel_id,
        )
        clear_events()
        return True
    except Exception as e:
        log_error(None, "analytics_report_failed", e)
        return False
