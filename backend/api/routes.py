"""
FastAPI Routes for POMABuster REST API.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional, Dict, Any
from backend.config import system_config, SystemConfig
from backend.models.schema import (
    TransferLog, Trade, POMAIncident, DetectionStats, TokenInfo
)
from backend.models.database import Database
from backend.engine.pipeline import POMABusterPipeline
from backend.data_loader.token_registry import get_token_registry
from backend.data_loader.benchmark_data import get_benchmark_transfer_logs

router = APIRouter(prefix="/api")

db = Database(system_config.db_path)
token_registry = get_token_registry()
pipeline = POMABusterPipeline(token_registry)

# Initialize database with tokens and benchmark logs on startup
def initialize_system():
    db.insert_tokens(token_registry)
    # Check if transfer logs are populated
    existing_logs = db.get_transfer_logs(limit=10)
    if not existing_logs:
        bench_logs = get_benchmark_transfer_logs()
        db.insert_transfer_logs(bench_logs)
        # Run initial detection
        trades, poms, arbs, incidents, stats = pipeline.execute(
            logs=bench_logs,
            sigma=system_config.sigma,
            block_window_n=system_config.block_window_n,
            strike_pct=system_config.strike_percentage
        )
        db.insert_trades(trades)
        db.insert_incidents(incidents)

initialize_system()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "POMABuster Detection Engine",
        "paper": "POMABuster: Detecting Price Oracle Manipulation Attacks in Decentralized Finance (IEEE S&P 2024)",
        "config": system_config.model_dump()
    }

@router.get("/config", response_model=SystemConfig)
def get_config():
    return system_config

@router.post("/config", response_model=SystemConfig)
def update_config(config_update: SystemConfig):
    global system_config
    system_config = config_update
    return system_config

@router.get("/tokens", response_model=List[TokenInfo])
def list_tokens():
    return db.get_all_tokens()

@router.get("/logs", response_model=List[TransferLog])
def list_transfer_logs(limit: int = Query(500, ge=1, le=5000)):
    return db.get_transfer_logs(limit=limit)

@router.get("/trades", response_model=List[Trade])
def list_trades(limit: int = Query(200, ge=1, le=2000)):
    return db.get_trades(limit=limit)

@router.get("/incidents", response_model=List[POMAIncident])
def list_incidents(
    attack_type: Optional[str] = Query(None, description="MARKET_DOMINATION or WASH_SALE"),
    is_multi_tx: Optional[bool] = Query(None, description="Filter multi-tx vs single-tx"),
    limit: int = Query(100, ge=1, le=1000)
):
    return db.get_incidents(attack_type=attack_type, is_multi_tx=is_multi_tx, limit=limit)

@router.get("/incidents/{incident_id}", response_model=POMAIncident)
def get_incident(incident_id: str):
    inc = db.get_incident_by_id(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc

@router.post("/detect")
def run_detection(
    sigma: Optional[float] = Body(None, description="Supply percentage threshold"),
    block_window_n: Optional[int] = Body(None, description="Block time window n"),
    strike_percentage: Optional[float] = Body(None, description="Strike price impact threshold")
):
    current_sigma = sigma if sigma is not None else system_config.sigma
    current_n = block_window_n if block_window_n is not None else system_config.block_window_n
    current_strike = strike_percentage if strike_percentage is not None else system_config.strike_percentage

    # Fetch all stored transfer logs
    logs = db.get_transfer_logs(limit=10000)
    
    # Run pipeline
    trades, poms, arbs, incidents, stats = pipeline.execute(
        logs=logs,
        sigma=current_sigma,
        block_window_n=current_n,
        strike_pct=current_strike
    )

    # Save reconstructed trades and updated incidents
    db.insert_trades(trades)
    db.clear_incidents()
    db.insert_incidents(incidents)

    return {
        "status": "success",
        "parameters_used": {
            "sigma": current_sigma,
            "block_window_n": current_n,
            "strike_percentage": current_strike
        },
        "stats": stats,
        "incidents_count": len(incidents),
        "incidents": incidents
    }

@router.get("/stats", response_model=DetectionStats)
def get_detection_statistics():
    logs = db.get_transfer_logs(limit=10000)
    trades, poms, arbs, incidents, stats = pipeline.execute(
        logs=logs,
        sigma=system_config.sigma,
        block_window_n=system_config.block_window_n,
        strike_pct=system_config.strike_percentage
    )
    return stats

@router.post("/reset-demo")
def reset_to_benchmark():
    """Resets database and reloads canonical paper benchmark datasets."""
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transfer_logs;")
        cursor.execute("DELETE FROM trades;")
        cursor.execute("DELETE FROM poma_incidents;")
        conn.commit()

    bench_logs = get_benchmark_transfer_logs()
    db.insert_transfer_logs(bench_logs)
    db.insert_tokens(token_registry)

    trades, poms, arbs, incidents, stats = pipeline.execute(
        logs=bench_logs,
        sigma=system_config.sigma,
        block_window_n=system_config.block_window_n,
        strike_pct=system_config.strike_percentage
    )
    db.insert_trades(trades)
    db.insert_incidents(incidents)

    return {
        "status": "reset_complete",
        "logs_loaded": len(bench_logs),
        "incidents_detected": len(incidents)
    }

@router.post("/logs/ingest")
def ingest_logs(logs: List[TransferLog]):
    """Ingests external ERC-20 transfer logs."""
    db.insert_transfer_logs(logs)
    return {
        "status": "success",
        "ingested_count": len(logs)
    }
