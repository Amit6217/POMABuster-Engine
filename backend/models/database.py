"""
SQLite Database Layer for POMABuster using standard sqlite3.
Stores tokens, transfer logs, reconstructed trades, and detected POMA incidents.
"""

import sqlite3
import json
from typing import List, Dict, Optional, Any
from backend.models.schema import TransferLog, Trade, POMAIncident, TokenInfo, POMType

class Database:
    def __init__(self, db_path: str = "pomabuster.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Tokens Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tokens (
                    address TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    name TEXT NOT NULL,
                    decimals INTEGER DEFAULT 18,
                    total_supply REAL NOT NULL,
                    price_usd REAL DEFAULT 0.0,
                    market_cap_usd REAL DEFAULT 0.0,
                    is_valuable INTEGER DEFAULT 1
                );
            """)

            # 2. Transfer Logs Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transfer_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tx_hash TEXT NOT NULL,
                    block_number INTEGER NOT NULL,
                    log_index INTEGER NOT NULL,
                    sender TEXT NOT NULL,
                    receiver TEXT NOT NULL,
                    token_address TEXT NOT NULL,
                    token_symbol TEXT NOT NULL,
                    amount REAL NOT NULL,
                    timestamp INTEGER NOT NULL,
                    UNIQUE(tx_hash, log_index)
                );
            """)

            # 3. Trades Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    trade_id TEXT PRIMARY KEY,
                    tx_hash TEXT NOT NULL,
                    block_number INTEGER NOT NULL,
                    operator TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    token_in TEXT NOT NULL,
                    token_in_symbol TEXT NOT NULL,
                    token_out TEXT NOT NULL,
                    token_out_symbol TEXT NOT NULL,
                    amount_in REAL NOT NULL,
                    amount_out REAL NOT NULL,
                    pool_address TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    in_log_index INTEGER,
                    out_log_index INTEGER
                );
            """)

            # 4. POMA Incidents Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS poma_incidents (
                    incident_id TEXT PRIMARY KEY,
                    attack_type TEXT NOT NULL,
                    is_multi_tx INTEGER NOT NULL,
                    block_distance INTEGER NOT NULL,
                    pom_tx_hash TEXT NOT NULL,
                    pom_block INTEGER NOT NULL,
                    pom_operator TEXT NOT NULL,
                    pom_token_address TEXT NOT NULL,
                    pom_token_symbol TEXT NOT NULL,
                    pom_amount REAL NOT NULL,
                    pom_supply_percentage REAL NOT NULL,
                    arb_tx_hash TEXT NOT NULL,
                    arb_block INTEGER NOT NULL,
                    arb_operator TEXT NOT NULL,
                    arb_profit_token TEXT NOT NULL,
                    arb_profit_amount REAL NOT NULL,
                    arb_profit_usd REAL NOT NULL,
                    manipulated_tokens_json TEXT,
                    intermediate_tokens_json TEXT,
                    shared_tokens_json TEXT,
                    estimated_price_impact_pct REAL,
                    is_true_positive INTEGER DEFAULT 1,
                    flagged_timestamp INTEGER NOT NULL,
                    explanation TEXT NOT NULL,
                    raw_json TEXT
                );
            """)

            # Create indices for query performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_tx ON transfer_logs(tx_hash);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_block ON transfer_logs(block_number);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_tx ON trades(tx_hash);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_type ON poma_incidents(attack_type);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_multi ON poma_incidents(is_multi_tx);")
            
            conn.commit()

    def insert_tokens(self, tokens: Dict[str, TokenInfo]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for t in tokens.values():
                cursor.execute("""
                    INSERT OR REPLACE INTO tokens (
                        address, symbol, name, decimals, total_supply, price_usd, market_cap_usd, is_valuable
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    t.address.lower(), t.symbol, t.name, t.decimals, t.total_supply,
                    t.price_usd, t.market_cap_usd, 1 if t.is_valuable else 0
                ))
            conn.commit()

    def get_all_tokens(self) -> List[TokenInfo]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tokens ORDER BY market_cap_usd DESC")
            rows = cursor.fetchall()
            return [
                TokenInfo(
                    address=r["address"],
                    symbol=r["symbol"],
                    name=r["name"],
                    decimals=r["decimals"],
                    total_supply=r["total_supply"],
                    price_usd=r["price_usd"],
                    market_cap_usd=r["market_cap_usd"],
                    is_valuable=bool(r["is_valuable"])
                )
                for r in rows
            ]

    def insert_transfer_logs(self, logs: List[TransferLog]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for l in logs:
                cursor.execute("""
                    INSERT OR IGNORE INTO transfer_logs (
                        tx_hash, block_number, log_index, sender, receiver,
                        token_address, token_symbol, amount, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    l.tx_hash, l.block_number, l.log_index, l.sender.lower(), l.receiver.lower(),
                    l.token_address.lower(), l.token_symbol, l.amount, l.timestamp
                ))
            conn.commit()

    def get_transfer_logs(self, limit: int = 1000) -> List[TransferLog]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transfer_logs ORDER BY block_number, log_index LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [
                TransferLog(
                    log_id=str(r["id"]),
                    tx_hash=r["tx_hash"],
                    block_number=r["block_number"],
                    log_index=r["log_index"],
                    sender=r["sender"],
                    receiver=r["receiver"],
                    token_address=r["token_address"],
                    token_symbol=r["token_symbol"],
                    amount=r["amount"],
                    timestamp=r["timestamp"]
                )
                for r in rows
            ]

    def insert_trades(self, trades: List[Trade]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for t in trades:
                cursor.execute("""
                    INSERT OR REPLACE INTO trades (
                        trade_id, tx_hash, block_number, operator, recipient,
                        token_in, token_in_symbol, token_out, token_out_symbol,
                        amount_in, amount_out, pool_address, timestamp, in_log_index, out_log_index
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    t.trade_id, t.tx_hash, t.block_number, t.operator, t.recipient,
                    t.token_in, t.token_in_symbol, t.token_out, t.token_out_symbol,
                    t.amount_in, t.amount_out, t.pool_address, t.timestamp,
                    t.in_log_index, t.out_log_index
                ))
            conn.commit()

    def get_trades(self, limit: int = 100) -> List[Trade]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trades ORDER BY block_number, in_log_index LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [
                Trade(
                    trade_id=r["trade_id"],
                    tx_hash=r["tx_hash"],
                    block_number=r["block_number"],
                    operator=r["operator"],
                    recipient=r["recipient"],
                    token_in=r["token_in"],
                    token_in_symbol=r["token_in_symbol"],
                    token_out=r["token_out"],
                    token_out_symbol=r["token_out_symbol"],
                    amount_in=r["amount_in"],
                    amount_out=r["amount_out"],
                    pool_address=r["pool_address"],
                    timestamp=r["timestamp"],
                    in_log_index=r["in_log_index"],
                    out_log_index=r["out_log_index"]
                )
                for r in rows
            ]

    def clear_incidents(self):
        with self._get_connection() as conn:
            conn.cursor().execute("DELETE FROM poma_incidents;")
            conn.commit()

    def insert_incidents(self, incidents: List[POMAIncident]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for inc in incidents:
                cursor.execute("""
                    INSERT OR REPLACE INTO poma_incidents (
                        incident_id, attack_type, is_multi_tx, block_distance,
                        pom_tx_hash, pom_block, pom_operator, pom_token_address,
                        pom_token_symbol, pom_amount, pom_supply_percentage,
                        arb_tx_hash, arb_block, arb_operator, arb_profit_token,
                        arb_profit_amount, arb_profit_usd, manipulated_tokens_json,
                        intermediate_tokens_json, shared_tokens_json, estimated_price_impact_pct,
                        is_true_positive, flagged_timestamp, explanation, raw_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    inc.incident_id, inc.attack_type.value, 1 if inc.is_multi_tx else 0, inc.block_distance,
                    inc.pom_tx_hash, inc.pom_block, inc.pom_operator, inc.pom_token_address,
                    inc.pom_token_symbol, inc.pom_amount, inc.pom_supply_percentage,
                    inc.arb_tx_hash, inc.arb_block, inc.arb_operator, inc.arb_profit_token,
                    inc.arb_profit_amount, inc.arb_profit_usd,
                    json.dumps(inc.manipulated_tokens),
                    json.dumps(inc.intermediate_tokens),
                    json.dumps(inc.shared_tokens),
                    inc.estimated_price_impact_pct,
                    1 if inc.is_true_positive else 0,
                    inc.flagged_timestamp,
                    inc.explanation,
                    inc.model_dump_json()
                ))
            conn.commit()

    def get_incidents(
        self,
        attack_type: Optional[str] = None,
        is_multi_tx: Optional[bool] = None,
        limit: int = 100
    ) -> List[POMAIncident]:
        query = "SELECT raw_json FROM poma_incidents WHERE 1=1"
        params = []
        if attack_type:
            query += " AND attack_type = ?"
            params.append(attack_type)
        if is_multi_tx is not None:
            query += " AND is_multi_tx = ?"
            params.append(1 if is_multi_tx else 0)
        query += " ORDER BY pom_block DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [POMAIncident.model_validate_json(r["raw_json"]) for r in rows]

    def get_incident_by_id(self, incident_id: str) -> Optional[POMAIncident]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT raw_json FROM poma_incidents WHERE incident_id = ?", (incident_id,))
            row = cursor.fetchone()
            if row:
                return POMAIncident.model_validate_json(row["raw_json"])
            return None
