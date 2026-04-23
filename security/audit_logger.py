"""
Audit Logging System for Email Spam Detector.
Tracks all operations for security compliance and transparency.
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import os


class AuditLogger:
    """Comprehensive audit logging for security compliance."""

    def __init__(self, db_path: str = "audit_log.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize audit log database with tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Main audit log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                action TEXT NOT NULL,
                user_id TEXT,
                email_id TEXT,
                details TEXT,
                status TEXT,
                ip_address TEXT,
                session_id TEXT
            )
        """)

        # API calls tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                api_provider TEXT NOT NULL,
                model_name TEXT,
                email_id TEXT,
                tokens_used INTEGER,
                cost_estimate REAL,
                response_time REAL,
                status TEXT,
                error_message TEXT
            )
        """)

        # PII detection log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pii_detected (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                email_id TEXT,
                pii_type TEXT NOT NULL,
                pii_hash TEXT NOT NULL,
                anonymized BOOLEAN,
                context TEXT
            )
        """)

        # Data access log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_access (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                access_type TEXT NOT NULL,
                resource TEXT NOT NULL,
                action TEXT NOT NULL,
                user_id TEXT,
                success BOOLEAN,
                details TEXT
            )
        """)

        # Classification decisions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classification_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                email_id TEXT,
                classification TEXT NOT NULL,
                confidence REAL,
                reason TEXT,
                indicators TEXT,
                model_used TEXT,
                anonymized BOOLEAN
            )
        """)

        conn.commit()
        conn.close()

    def log_event(self, event_type: str, action: str, details: Dict = None,
                  status: str = "success", email_id: str = None) -> int:
        """
        Log a general audit event.

        Args:
            event_type: Type of event (e.g., 'email_scan', 'config_change')
            action: Specific action taken
            details: Additional details as dictionary
            status: Event status (success, failure, warning)
            email_id: Associated email ID if applicable

        Returns:
            Log entry ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO audit_log (timestamp, event_type, action, email_id, details, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            event_type,
            action,
            email_id,
            json.dumps(details) if details else None,
            status
        ))

        log_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return log_id

    def log_api_call(self, api_provider: str, model_name: str, email_id: str = None,
                     tokens_used: int = 0, response_time: float = 0,
                     status: str = "success", error_message: str = None) -> int:
        """Log API call for transparency and cost tracking."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Estimate cost (rough estimates)
        cost_per_1k_tokens = {
            'groq': 0.0001,  # Very cheap
            'openai': 0.002,
            'anthropic': 0.003
        }
        cost_estimate = (tokens_used / 1000) * cost_per_1k_tokens.get(api_provider.lower(), 0.001)

        cursor.execute("""
            INSERT INTO api_calls (timestamp, api_provider, model_name, email_id,
                                   tokens_used, cost_estimate, response_time, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            api_provider,
            model_name,
            email_id,
            tokens_used,
            cost_estimate,
            response_time,
            status,
            error_message
        ))

        log_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return log_id

    def log_pii_detection(self, email_id: str, pii_type: str, pii_hash: str,
                          anonymized: bool = True, context: str = None) -> int:
        """Log PII detection for privacy compliance."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO pii_detected (timestamp, email_id, pii_type, pii_hash, anonymized, context)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            email_id,
            pii_type,
            pii_hash,
            anonymized,
            context
        ))

        log_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return log_id

    def log_classification(self, email_id: str, classification: str, confidence: float,
                           reason: str, indicators: List[str], model_used: str,
                           anonymized: bool = False) -> int:
        """Log spam classification decision."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO classification_log (timestamp, email_id, classification, confidence,
                                            reason, indicators, model_used, anonymized)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            email_id,
            classification,
            confidence,
            reason,
            json.dumps(indicators),
            model_used,
            anonymized
        ))

        log_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return log_id

    def log_data_access(self, access_type: str, resource: str, action: str,
                        success: bool = True, details: Dict = None) -> int:
        """Log data access for security monitoring."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO data_access (timestamp, access_type, resource, action, success, details)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            access_type,
            resource,
            action,
            success,
            json.dumps(details) if details else None
        ))

        log_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return log_id

    def get_recent_events(self, limit: int = 50, event_type: str = None) -> List[Dict]:
        """Get recent audit events."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if event_type:
            cursor.execute("""
                SELECT * FROM audit_log
                WHERE event_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (event_type, limit))
        else:
            cursor.execute("""
                SELECT * FROM audit_log
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

        columns = [desc[0] for desc in cursor.description]
        events = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return events

    def get_api_usage_stats(self, days: int = 7) -> Dict:
        """Get API usage statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                api_provider,
                COUNT(*) as call_count,
                SUM(tokens_used) as total_tokens,
                SUM(cost_estimate) as total_cost,
                AVG(response_time) as avg_response_time
            FROM api_calls
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            GROUP BY api_provider
        """, (days,))

        columns = [desc[0] for desc in cursor.description]
        stats = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return stats

    def get_pii_summary(self, days: int = 7) -> Dict:
        """Get PII detection summary."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                pii_type,
                COUNT(*) as count,
                SUM(CASE WHEN anonymized THEN 1 ELSE 0 END) as anonymized_count
            FROM pii_detected
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            GROUP BY pii_type
        """, (days,))

        columns = [desc[0] for desc in cursor.description]
        summary = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return summary

    def export_audit_log(self, output_file: str, days: int = 30):
        """Export audit log to JSON file."""
        events = self.get_recent_events(limit=10000)

        # Filter by date
        cutoff = datetime.now().timestamp() - (days * 86400)
        filtered = [
            e for e in events
            if datetime.fromisoformat(e['timestamp']).timestamp() >= cutoff
        ]

        with open(output_file, 'w') as f:
            json.dump(filtered, f, indent=2)

        return len(filtered)


if __name__ == "__main__":
    # Test audit logger
    logger = AuditLogger("test_audit.db")

    # Test logging
    logger.log_event("email_scan", "scan_started", {"limit": 10})
    logger.log_api_call("groq", "llama-3.1-8b-instant", tokens_used=500, response_time=1.2)
    logger.log_pii_detection("email_123", "email", "abc123hash", anonymized=True)

    print("Audit log test completed")
    print("\nRecent events:")
    for event in logger.get_recent_events(limit=5):
        print(f"  {event['timestamp']} - {event['event_type']}: {event['action']}")
