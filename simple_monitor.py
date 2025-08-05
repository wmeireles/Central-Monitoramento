#!/usr/bin/env python3
"""
Versão simplificada do monitor sem dependências externas complexas
"""

import json
import logging
import os
import time
import smtplib
import sqlite3
import requests
import ssl
import socket
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from urllib.parse import urlparse
from typing import Dict, List, Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring.log'),
        logging.StreamHandler()
    ]
)

class SimpleMonitor:
    def __init__(self):
        self.db_path = "monitoring.db"
        self.init_db()
        self.sites = self.load_sites()
        
    def init_db(self):
        """Inicializa banco SQLite"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_name TEXT,
                    url TEXT,
                    status_code INTEGER,
                    response_time REAL,
                    is_up BOOLEAN,
                    error_message TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    def load_sites(self) -> List[Dict]:
        """Carrega sites do JSON"""
        try:
            with open('sites.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return [
                {"name": "Google", "url": "https://www.google.com", "expected_status": 200},
                {"name": "GitHub", "url": "https://github.com", "expected_status": 200}
            ]
    
    def check_site(self, site: Dict) -> Dict:
        """Verifica um site"""
        result = {
            'name': site['name'],
            'url': site['url'],
            'is_up': False,
            'status_code': None,
            'response_time': None,
            'error_message': None,
            'timestamp': datetime.now()
        }
        
        try:
            start_time = time.time()
            response = requests.get(site['url'], timeout=30)
            end_time = time.time()
            
            result['status_code'] = response.status_code
            result['response_time'] = (end_time - start_time) * 1000
            
            expected_status = site.get('expected_status', 200)
            if response.status_code == expected_status:
                result['is_up'] = True
            else:
                result['error_message'] = f"Status {response.status_code} (esperado {expected_status})"
                
        except Exception as e:
            result['error_message'] = str(e)
        
        return result
    
    def save_result(self, result: Dict):
        """Salva resultado no banco"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO checks (site_name, url, status_code, response_time, is_up, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                result['name'], result['url'], result['status_code'],
                result['response_time'], result['is_up'], result['error_message']
            ))
    
    def send_email_alert(self, result: Dict):
        """Envia alerta por email (configurar SMTP)"""
        try:
            # Configurações básicas - ajustar conforme necessário
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            email_user = "seu_email@gmail.com"  # Configurar
            email_password = "sua_senha"  # Configurar
            
            if email_user == "seu_email@gmail.com":
                return  # Não configurado
            
            message = f"""
            ALERTA: {result['name']} está indisponível!
            
            URL: {result['url']}
            Status: {result['status_code']}
            Erro: {result['error_message']}
            Timestamp: {result['timestamp']}
            """
            
            msg = MIMEText(message)
            msg['Subject'] = f"[ALERTA] {result['name']} indisponível"
            msg['From'] = email_user
            msg['To'] = email_user
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(email_user, email_password)
                server.send_message(msg)
                
            logging.info(f"Email enviado para {result['name']}")
            
        except Exception as e:
            logging.error(f"Erro ao enviar email: {e}")
    
    def check_all_sites(self):
        """Verifica todos os sites"""
        logging.info("Iniciando verificação...")
        
        for site in self.sites:
            result = self.check_site(site)
            self.save_result(result)
            
            status = "UP" if result['is_up'] else "DOWN"
            response_time = result['response_time'] or 0
            
            logging.info(f"{result['name']}: {status} - {response_time:.0f}ms")
            
            # Enviar alerta se site estiver down
            if not result['is_up']:
                self.send_email_alert(result)
    
    def generate_report(self, site_name: str = None):
        """Gera relatório simples"""
        with sqlite3.connect(self.db_path) as conn:
            if site_name:
                cursor = conn.execute('''
                    SELECT * FROM checks WHERE site_name = ? 
                    ORDER BY timestamp DESC LIMIT 50
                ''', (site_name,))
            else:
                cursor = conn.execute('''
                    SELECT * FROM checks ORDER BY timestamp DESC LIMIT 100
                ''')
            
            results = cursor.fetchall()
            
            if not results:
                print("Nenhum dado encontrado")
                return
            
            print(f"\n{'='*60}")
            print(f"RELATÓRIO DE MONITORAMENTO")
            print(f"{'='*60}")
            
            for row in results:
                timestamp = row[7]
                site_name = row[1]
                status = "UP" if row[5] else "DOWN"
                response_time = row[4] or 0
                
                print(f"{timestamp} | {site_name:15} | {status:4} | {response_time:6.0f}ms")
    
    def run_continuous(self, interval: int = 300):
        """Executa monitoramento contínuo"""
        logging.info(f"Iniciando monitoramento contínuo (intervalo: {interval}s)")
        
        try:
            while True:
                self.check_all_sites()
                time.sleep(interval)
        except KeyboardInterrupt:
            logging.info("Monitoramento interrompido pelo usuário")

def main():
    """Função principal"""
    import sys
    
    monitor = SimpleMonitor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'check':
            monitor.check_all_sites()
        elif command == 'report':
            site_name = sys.argv[2] if len(sys.argv) > 2 else None
            monitor.generate_report(site_name)
        elif command == 'continuous':
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300
            monitor.run_continuous(interval)
        else:
            print("Comandos: check, report [site], continuous [intervalo]")
    else:
        print("Monitor Simples de Sites")
        print("Comandos disponíveis:")
        print("  python simple_monitor.py check          - Verificação única")
        print("  python simple_monitor.py report         - Relatório geral")
        print("  python simple_monitor.py report Google  - Relatório de um site")
        print("  python simple_monitor.py continuous     - Monitoramento contínuo")

if __name__ == "__main__":
    main()