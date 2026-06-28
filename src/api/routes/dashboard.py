"""
Dashboard Routes — /v1/stats and /v1/logs

Aggregated statistics and paginated log access for the dashboard.
"""

import logging
import math
from datetime import datetime, timezone, timedelta
from typing import Optional
from bson import ObjectId

from fastapi import APIRouter, Depends, Query, HTTPException, Request

from src.api.middleware import validate_api_key, optional_api_key
from src.db import mongo

logger = logging.getLogger("llm_firewall.routes.dashboard")

router = APIRouter(prefix="/v1", tags=["dashboard"])


@router.get("/stats")
async def get_stats(key_doc: Optional[dict] = Depends(optional_api_key)):
    """
    Get aggregated statistics for the dashboard.
    Works without auth for demo purposes.
    """
    logs = mongo.get_logs_collection()
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    thirty_days_ago = now - timedelta(days=30)

    # Total counts
    total_checks = await logs.count_documents({})
    flagged_count = await logs.count_documents({"safe": False})
    blocked_count = await logs.count_documents({"blocked": True})

    # Today counts
    requests_today = await logs.count_documents({"timestamp": {"$gte": today_start}})
    requests_this_month = await logs.count_documents({"timestamp": {"$gte": month_start}})

    # Attack breakdown
    attack_pipeline = [
        {"$match": {"safe": False, "attack_type": {"$ne": None}}},
        {"$group": {"_id": "$attack_type", "count": {"$sum": 1}}},
    ]
    attack_breakdown = {}
    async for doc in logs.aggregate(attack_pipeline):
        attack_breakdown[doc["_id"]] = doc["count"]

    # Average processing time
    avg_pipeline = [
        {"$group": {"_id": None, "avg_time": {"$avg": "$processing_time_ms"}}},
    ]
    avg_time = 0.0
    async for doc in logs.aggregate(avg_pipeline):
        avg_time = round(doc.get("avg_time", 0.0), 2)

    # Top flagged patterns
    pattern_pipeline = [
        {"$match": {"flagged_pattern": {"$ne": None}}},
        {"$group": {"_id": "$flagged_pattern", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    top_patterns = []
    async for doc in logs.aggregate(pattern_pipeline):
        top_patterns.append({"pattern": doc["_id"], "count": doc["count"]})

    # Layer effectiveness
    layer_pipeline = [
        {"$match": {"safe": False, "flagged_layer": {"$ne": None}}},
        {"$group": {"_id": "$flagged_layer", "count": {"$sum": 1}}},
    ]
    layer_counts = {}
    async for doc in logs.aggregate(layer_pipeline):
        layer_counts[doc["_id"]] = doc["count"]

    total_flagged = sum(layer_counts.values()) or 1
    layer_effectiveness = {
        "canary_pct": round(layer_counts.get("canary", 0) / total_flagged * 100, 1),
        "rule_based_pct": round(layer_counts.get("rule_based", 0) / total_flagged * 100, 1),
        "heuristic_pct": round(layer_counts.get("heuristic", 0) / total_flagged * 100, 1),
        "embedding_pct": round(layer_counts.get("embedding_similarity", 0) / total_flagged * 100, 1),
        "ml_pct": round(layer_counts.get("ml_classifier", 0) / total_flagged * 100, 1),
        "context_pct": round(layer_counts.get("context_policy", 0) / total_flagged * 100, 1),
    }

    flag_rate = round(flagged_count / total_checks * 100, 2) if total_checks > 0 else 0.0
    block_rate = round(blocked_count / total_checks * 100, 2) if total_checks > 0 else 0.0

    # ── ADVANCED ANALYTICS (Stacked bar, Heatmap, Histogram) ──

    # 1. 30-Day Trend (Safe vs Blocked vs Specific attack types)
    trend_pipeline = [
        {"$match": {"timestamp": {"$gte": thirty_days_ago}}},
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$timestamp"},
                    "month": {"$month": "$timestamp"},
                    "day": {"$dayOfMonth": "$timestamp"}
                },
                "total": {"$sum": 1},
                "safe": {"$sum": {"$cond": [{"$eq": ["$safe", True]}, 1, 0]}},
                "role_override": {"$sum": {"$cond": [{"$eq": ["$attack_type", "role_override"]}, 1, 0]}},
                "goal_hijacking": {"$sum": {"$cond": [{"$eq": ["$attack_type", "goal_hijacking"]}, 1, 0]}},
                "context_poisoning": {"$sum": {"$cond": [{"$eq": ["$attack_type", "context_poisoning"]}, 1, 0]}},
                "tool_manipulation": {"$sum": {"$cond": [{"$eq": ["$attack_type", "tool_manipulation"]}, 1, 0]}},
                "cascading_amplification": {"$sum": {"$cond": [{"$eq": ["$attack_type", "cascading_amplification"]}, 1, 0]}},
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}}
    ]

    attack_over_time = []
    async for doc in logs.aggregate(trend_pipeline):
        dt = f"{doc['_id']['year']}-{doc['_id']['month']:02d}-{doc['_id']['day']:02d}"
        attack_over_time.append({
            "date": dt,
            "total": doc["total"],
            "safe": doc["safe"],
            "role_override": doc["role_override"],
            "goal_hijacking": doc["goal_hijacking"],
            "context_poisoning": doc["context_poisoning"],
            "tool_manipulation": doc["tool_manipulation"],
            "cascading_amplification": doc["cascading_amplification"],
        })

    # If no database logs exist yet, generate empty 30-day stats
    if not attack_over_time:
        for i in range(29, -1, -1):
            d = (now - timedelta(days=i)).strftime("%Y-%m-%d")
            attack_over_time.append({
                "date": d,
                "total": 0,
                "safe": 0,
                "role_override": 0,
                "goal_hijacking": 0,
                "context_poisoning": 0,
                "tool_manipulation": 0,
                "cascading_amplification": 0,
            })

    # 2. Hourly Heatmap (Actual counts by day and hour)
    heatmap_pipeline = [
        {"$match": {"safe": False}},  # Only malicious payloads
        {
            "$group": {
                "_id": {
                    "day": {"$dayOfWeek": "$timestamp"},
                    "hour": {"$hour": "$timestamp"}
                },
                "count": {"$sum": 1}
            }
        }
    ]
    
    # Initialize 7x24 grid with 0
    heatmap_data = [{"day": d, "hour": h, "count": 0} for d in range(7) for h in range(24)]
    
    async for doc in logs.aggregate(heatmap_pipeline):
        # mongo $dayOfWeek: 1 (Sun) to 7 (Sat)
        # frontend DAYS array: 0 (Mon) to 6 (Sun)
        mongo_day = doc["_id"]["day"]
        mapped_day = (mongo_day + 5) % 7
        hour = doc["_id"]["hour"]
        
        for cell in heatmap_data:
            if cell["day"] == mapped_day and cell["hour"] == hour:
                cell["count"] += doc["count"]
                break

    # 3. Risk Score Distribution (Histogram data)
    histo_pipeline = [
        {
            "$bucket": {
                "groupBy": "$risk_score",
                "boundaries": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.01],
                "default": "Other",
                "output": {"count": {"$sum": 1}}
            }
        }
    ]
    
    risk_distribution = []
    bucket_counts = {}
    async for doc in logs.aggregate(histo_pipeline):
        lower_bound = doc["_id"]
        if isinstance(lower_bound, float):
            bucket_counts[lower_bound] = doc["count"]

    boundaries = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    for b in boundaries:
        label = f"{b:.1f}-{b+0.1:.1f}"
        count = bucket_counts.get(b, 0)
        # If no real data, seed with 0
        if not total_checks:
            count = 0
        
        risk_distribution.append({
            "range": label,
            "count": count
        })

    return {
        "total_checks": total_checks,
        "flagged_count": flagged_count,
        "blocked_count": blocked_count,
        "flag_rate": flag_rate,
        "block_rate": block_rate,
        "attack_breakdown": attack_breakdown,
        "requests_today": requests_today,
        "requests_this_month": requests_this_month,
        "avg_processing_time_ms": avg_time,
        "top_flagged_patterns": top_patterns,
        "layer_effectiveness": layer_effectiveness,
        "attack_over_time": attack_over_time,
        "hourly_heatmap": heatmap_data,
        "risk_distribution": risk_distribution
    }


@router.get("/logs")
async def get_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    flagged_only: bool = Query(False),
    blocked_only: bool = Query(False),
    attack_type: Optional[str] = Query(None),
    provider: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    key_doc: Optional[dict] = Depends(optional_api_key),
):
    """Get paginated log entries with filters."""
    logs = mongo.get_logs_collection()

    # Build filter
    query: dict = {}
    if flagged_only:
        query["safe"] = False
    if blocked_only:
        query["blocked"] = True
    if attack_type:
        query["attack_type"] = attack_type
    if provider:
        query["provider"] = provider
    if start_date:
        try:
            query.setdefault("timestamp", {})["$gte"] = datetime.fromisoformat(start_date)
        except ValueError:
            pass
    if end_date:
        try:
            query.setdefault("timestamp", {})["$lte"] = datetime.fromisoformat(end_date)
        except ValueError:
            pass

    # Paginate
    skip = (page - 1) * limit
    total = await logs.count_documents(query)
    cursor = logs.find(query).sort("timestamp", -1).skip(skip).limit(limit)

    entries = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["api_key_id"] = str(doc.get("api_key_id", ""))
        if isinstance(doc.get("timestamp"), datetime):
            doc["timestamp"] = doc["timestamp"].isoformat()
        entries.append(doc)

    return {
        "logs": entries,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.get("/logs/{request_id}")
async def get_log_detail(
    request_id: str,
    key_doc: Optional[dict] = Depends(optional_api_key),
):
    """Get full detail for a specific log entry."""
    logs = mongo.get_logs_collection()
    doc = await logs.find_one({"request_id": request_id})

    if not doc:
        raise HTTPException(status_code=404, detail="Log entry not found")

    doc["_id"] = str(doc["_id"])
    doc["api_key_id"] = str(doc.get("api_key_id", ""))
    if isinstance(doc.get("timestamp"), datetime):
        doc["timestamp"] = doc["timestamp"].isoformat()

    return doc
