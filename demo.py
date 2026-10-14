"""Offline quote-quality demonstration using fictional data only."""

from collections import Counter
from datetime import datetime, timezone
import json
import math


def _timestamp(value):
    if not isinstance(value, str):
        return None
    # Z denotes UTC only when it is the final character.
    if "Z" in value[:-1]:
        return None
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
        if parsed.utcoffset() is None:
            return None
        return parsed.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        return None


def _price(value):
    if isinstance(value, bool):
        return None
    try:
        parsed = float(value)
        return parsed if math.isfinite(parsed) and parsed > 0 else None
    except (TypeError, ValueError, OverflowError):
        return None


def audit(records):
    """Report observed issues without changing or repairing the supplied rows."""
    seen = set()
    previous = {}
    issues = []
    counts = Counter()
    clean_rows = 0
    total_rows = 0
    for row_number, record in enumerate(records, start=1):
        total_rows += 1
        reasons = []
        symbol = record.get("symbol")
        event_id = record.get("event_id")
        valid_identity = all(
            isinstance(value, str) and value.strip() for value in (symbol, event_id)
        )
        if not valid_identity:
            reasons.append("INVALID_IDENTITY")
        else:
            key = (symbol, event_id)
            if key in seen:
                reasons.append("DUPLICATE_EVENT")
            seen.add(key)

        timestamp = _timestamp(record.get("timestamp"))
        if timestamp is None:
            reasons.append("INVALID_TIMESTAMP")
        elif valid_identity:
            if symbol in previous and timestamp < previous[symbol]:
                reasons.append("TIMESTAMP_REGRESSION")
            previous[symbol] = max(previous.get(symbol, timestamp), timestamp)

        bid, ask = _price(record.get("bid")), _price(record.get("ask"))
        if bid is None or ask is None:
            reasons.append("INVALID_PRICE")
        elif bid > ask:
            reasons.append("CROSSED_QUOTE")

        if reasons:
            counts.update(reasons)
            issues.append({"row": row_number, "issue_codes": reasons})
        else:
            clean_rows += 1
    return {
        "total_rows": total_rows,
        "rows_without_detected_issues": clean_rows,
        "rows_with_detected_issues": len(issues),
        "issue_counts": dict(sorted(counts.items())),
        "issues": issues,
    }


def synthetic_quotes():
    def quote(symbol, event_id, timestamp, bid, ask):
        return dict(symbol=symbol, event_id=event_id, timestamp=timestamp,
                    bid=bid, ask=ask)

    first = quote("DEMO_A", "event-1", "2024-01-02T12:00:00Z", 100, 100.02)
    second = quote("DEMO_A", "event-2", "2024-01-02T12:00:01Z", 100.01, 100.03)
    return [
        first,
        second,
        dict(second),
        quote("DEMO_A", "event-3", "2024-01-02T12:00:00.500Z", 100.02, 100.04),
        quote("DEMO_B", "event-4", "2024-01-02T12:00:01Z", 50.02, 50),
        quote("DEMO_B", "event-5", "2024-01-02T12:00:02Z", None, 50.01),
    ]


if __name__ == "__main__":
    print(json.dumps(audit(synthetic_quotes()), indent=2, allow_nan=False))
