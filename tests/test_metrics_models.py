from __future__ import annotations

import json
from dataclasses import asdict

from llm_observability_analytics.metrics.models import AnalyticsSummary, MetricRecord


def test_metric_record_basic():
    mr = MetricRecord(
        metric_name="latency", metric_value=12.5, dimension_key="service", dimension_value="svc-a"
    )
    assert mr.metric_name == "latency"
    assert mr.metric_value == 12.5


def test_analytics_summary_roundtrip():
    s = AnalyticsSummary(
        request_count=10,
        retrieval_trace_count=4,
        latency_mean_ms=100.0,
        latency_p50_ms=90.0,
        latency_p95_ms=150.0,
        total_tokens=1234,
        average_tokens_per_request=123.4,
        retrieval_hit_count=3,
        grounded_response_count=7,
        ungrounded_response_count=3,
        feedback_count=2,
    )
    d = s.to_dict()
    assert d["request_count"] == 10
    # JSON roundtrip
    j = s.to_json()
    parsed = json.loads(j)
    assert parsed == asdict(s)
