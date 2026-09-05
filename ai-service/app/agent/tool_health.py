"""
tool_health.py — Tool Health Check for NETRA Investigation Agent (Phase A)

Provides run_health_check() which probes all 8 investigation tools with
minimal, safe inputs and reports their status and latency.

Rules:
  - Never raises: catches all exceptions internally.
  - A tool is "ok" if it returns any non-exception value (including empty
    results or structured tool_error dicts from the service adapter).
  - A tool is "error" only if it raises an uncaught exception.
  - Overall status:
      "healthy"  — all 8 tools ok
      "degraded" — 1–3 tools errored
      "critical" — 4+ tools errored
"""

import time
import logging
from app.agent.tool_service import InvestigationService, get_session

logger = logging.getLogger(__name__)

_TOOL_PROBES = [
    # (label, lambda svc: svc.method(safe_args))
    ("search_cases",        lambda svc: svc.search_cases("test")),
    ("search_entities",     lambda svc: svc.search_entities("test")),
    ("get_entity",          lambda svc: svc.get_entity("ent_001")),
    ("explore_graph",       lambda svc: svc.explore_graph("C-001", "ent_001", 1)),
    ("get_relationship",    lambda svc: svc.get_relationship("rel_001")),
    ("get_findings",        lambda svc: svc.get_findings("C-001")),
    ("get_evidence",        lambda svc: svc.get_evidence("ev_001")),
    ("run_network_analysis",lambda svc: svc.run_network_analysis("C-001")),
]


def run_health_check() -> dict:
    """
    Test all 8 investigation tools with safe minimal inputs.

    Returns:
        {
            "status": "healthy" | "degraded" | "critical",
            "tools": {
                "<tool_name>": {
                    "status": "ok" | "error",
                    "latency_ms": <float>,
                    "error": null | "<message>"
                }
            }
        }
    """
    tool_results = {}
    error_count = 0

    for label, probe in _TOOL_PROBES:
        t0 = time.perf_counter()
        tool_error = None
        try:
            with get_session() as db:
                svc = InvestigationService(db)
                probe(svc)
            status = "ok"
        except Exception as exc:
            status = "error"
            tool_error = str(exc)
            error_count += 1
            logger.error("Health check failed for tool '%s': %s", label, exc, exc_info=True)
        finally:
            latency_ms = (time.perf_counter() - t0) * 1000

        tool_results[label] = {
            "status": status,
            "latency_ms": round(latency_ms, 2),
            "error": tool_error,
        }

    if error_count == 0:
        overall = "healthy"
    elif error_count <= 3:
        overall = "degraded"
    else:
        overall = "critical"

    return {"status": overall, "tools": tool_results}
