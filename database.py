import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Dict

class MonitoringDB:
    def __init__(self, db_path: str = "monitoring.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    status_code INTEGER,
                    response_time REAL,
                    ssl_days_remaining INTEGER,
                    is_up BOOLEAN,
                    error_message TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_name TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    sent_via TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    def log_check(self, site_name: str, url: str, status_code: Optional[int], 
                  response_time: Optional[float], ssl_days: Optional[int], 
                  is_up: bool, error_message: Optional[str] = None):
        """Registra o resultado de uma verificação"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO monitoring_logs 
                (site_name, url, status_code, response_time, ssl_days_remaining, is_up, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (site_name, url, status_code, response_time, ssl_days, is_up, error_message))
    
    def log_alert(self, site_name: str, alert_type: str, message: str, sent_via: str):
        """Registra um alerta enviado"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO alerts (site_name, alert_type, message, sent_via)
                VALUES (?, ?, ?, ?)
            ''', (site_name, alert_type, message, sent_via))
    
    def get_site_history(self, site_name: str, limit: int = 100) -> List[Dict]:
        """Obtém o histórico de um site específico"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM monitoring_logs 
                WHERE site_name = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (site_name, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_last_status(self, site_name: str) -> Optional[Dict]:
        """Obtém o último status de um site"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM monitoring_logs 
                WHERE site_name = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (site_name,))
            row = cursor.fetchone()
            return dict(row) if row else None