#!/usr/bin/env python3
"""
Monitor básico de sites - apenas bibliotecas padrão do Python
"""

import json
import logging
import sqlite3
import time
import smtplib
import urllib.request
import urllib.error
import ssl
import socket
from datetime import datetime
from email.mime.text import MIMEText
from urllib.parse import urlparse

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring.log'),
        logging.StreamHandler()
    ]
)

class MonitorBasico:
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
    
    def load_sites(self):
        """Carrega sites do JSON ou usa padrões"""
        try:
            with open('sites.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            # Sites padrão se não conseguir carregar o JSON
            # Tentar carregar sites_exemplo.json
            try:
                with open('sites_exemplo.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return [
                    {"name": "Google", "url": "https://www.google.com", "expected_status": 200},
                    {"name": "GitHub", "url": "https://github.com", "expected_status": 200},
                    {"name": "Python.org", "url": "https://www.python.org", "expected_status": 200}
                ]
    
    def check_site(self, site):
        """Verifica um site usando urllib"""
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
            
            # Criar requisição
            req = urllib.request.Request(site['url'])
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Fazer requisição
            with urllib.request.urlopen(req, timeout=30) as response:
                end_time = time.time()
                
                result['status_code'] = response.getcode()
                result['response_time'] = (end_time - start_time) * 1000
                
                expected_status = site.get('expected_status', 200)
                if response.getcode() == expected_status:
                    result['is_up'] = True
                else:
                    result['error_message'] = f"Status {response.getcode()} (esperado {expected_status})"
                    
        except urllib.error.HTTPError as e:
            result['status_code'] = e.code
            result['error_message'] = f"HTTP Error {e.code}: {e.reason}"
        except urllib.error.URLError as e:
            result['error_message'] = f"URL Error: {e.reason}"
        except Exception as e:
            result['error_message'] = str(e)
        
        return result
    
    def save_result(self, result):
        """Salva resultado no banco"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO checks (site_name, url, status_code, response_time, is_up, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                result['name'], result['url'], result['status_code'],
                result['response_time'], result['is_up'], result['error_message']
            ))
    
    def check_all_sites(self):
        """Verifica todos os sites"""
        print(f"\nVerificando {len(self.sites)} sites...")
        print("-" * 50)
        
        for site in self.sites:
            result = self.check_site(site)
            self.save_result(result)
            
            status = "UP" if result['is_up'] else "DOWN"
            response_time = result['response_time'] or 0
            
            print(f"{result['name']:15} | {status:6} | {response_time:6.0f}ms")
            
            if result['error_message']:
                print(f"                  Erro: {result['error_message']}")
        
        print("-" * 50)
    
    def generate_report(self, site_name=None, limit=20):
        """Gera relatório"""
        with sqlite3.connect(self.db_path) as conn:
            if site_name:
                cursor = conn.execute('''
                    SELECT * FROM checks WHERE site_name = ? 
                    ORDER BY timestamp DESC LIMIT ?
                ''', (site_name, limit))
                print(f"\nRelatorio: {site_name}")
            else:
                cursor = conn.execute('''
                    SELECT * FROM checks ORDER BY timestamp DESC LIMIT ?
                ''', (limit,))
                print(f"\nRelatorio Geral")
            
            results = cursor.fetchall()
            
            if not results:
                print("Nenhum dado encontrado")
                return
            
            print("=" * 70)
            print(f"{'Timestamp':19} | {'Site':15} | {'Status':6} | {'Tempo':8} | Erro")
            print("-" * 70)
            
            for row in results:
                timestamp = row[7][:19]  # Apenas data e hora
                site_name = row[1][:15]
                status = "UP" if row[5] else "DOWN"
                response_time = f"{row[4] or 0:.0f}ms"
                error = row[6] or ""
                
                print(f"{timestamp} | {site_name:15} | {status:6} | {response_time:8} | {error[:30]}")
    
    def calculate_uptime(self, site_name, hours=24):
        """Calcula uptime de um site"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT COUNT(*) as total, SUM(is_up) as up_count
                FROM checks 
                WHERE site_name = ? AND timestamp > datetime('now', '-{} hours')
            '''.format(hours), (site_name,))
            
            result = cursor.fetchone()
            total, up_count = result[0], result[1] or 0
            
            if total == 0:
                return 0
            
            uptime = (up_count / total) * 100
            return round(uptime, 2)
    
    def show_status(self):
        """Mostra status atual de todos os sites"""
        print("\nStatus Atual dos Sites")
        print("=" * 50)
        
        for site in self.sites:
            uptime = self.calculate_uptime(site['name'])
            
            # Pegar último status
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT is_up, response_time, timestamp 
                    FROM checks 
                    WHERE site_name = ? 
                    ORDER BY timestamp DESC LIMIT 1
                ''', (site['name'],))
                
                last_check = cursor.fetchone()
                
                if last_check:
                    status = "UP" if last_check[0] else "DOWN"
                    response_time = last_check[1] or 0
                    last_time = last_check[2][:16]
                    
                    print(f"{site['name']:15} | {status:6} | {uptime:5.1f}% | {response_time:6.0f}ms | {last_time}")
                else:
                    print(f"{site['name']:15} | N/A  |   N/A  |    N/A   | Nunca verificado")
    
    def run_continuous(self, interval=300):
        """Executa monitoramento contínuo"""
        print(f"Iniciando monitoramento continuo (intervalo: {interval}s)")
        print("Pressione Ctrl+C para parar")
        
        try:
            while True:
                self.check_all_sites()
                print(f"Proxima verificacao em {interval} segundos...")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitoramento interrompido pelo usuario")

def main():
    """Função principal"""
    import sys
    
    monitor = MonitorBasico()
    
    print("Monitor Basico de Sites")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'check':
            monitor.check_all_sites()
        elif command == 'report':
            site_name = sys.argv[2] if len(sys.argv) > 2 else None
            monitor.generate_report(site_name)
        elif command == 'status':
            monitor.show_status()
        elif command == 'continuous':
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300
            monitor.run_continuous(interval)
        else:
            print("Comando invalido")
            print_help()
    else:
        print_help()
        print("\nExecutando verificacao unica...")
        monitor.check_all_sites()

def print_help():
    """Mostra ajuda"""
    print("\nComandos disponiveis:")
    print("  python monitor_basico.py check              - Verificação única")
    print("  python monitor_basico.py status             - Status e uptime")
    print("  python monitor_basico.py report             - Relatório geral")
    print("  python monitor_basico.py report Google      - Relatório de um site")
    print("  python monitor_basico.py continuous [300]   - Monitoramento contínuo")

if __name__ == "__main__":
    main()