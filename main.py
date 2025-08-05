#!/usr/bin/env python3
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from monitor import SiteMonitor
from notifications import NotificationManager
from database import MonitoringDB
from reports import ReportGenerator

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring.log'),
        logging.StreamHandler()
    ]
)

class MonitoringSystem:
    def __init__(self):
        self.db = MonitoringDB()
        self.monitor = SiteMonitor(
            timeout=int(os.getenv('TIMEOUT', 30)),
            retry_count=int(os.getenv('RETRY_COUNT', 3))
        )
        self.notifier = NotificationManager()
        self.report_generator = ReportGenerator(self.db)
        self.sites = self.load_sites_config()
        self.site_states = {}  # Para rastrear mudanças de estado
        
    def load_sites_config(self) -> List[Dict]:
        """Carrega configuração dos sites do arquivo JSON"""
        try:
            with open('sites.json', 'r', encoding='utf-8') as f:
                sites = json.load(f)
            logging.info(f"Carregados {len(sites)} sites para monitoramento")
            return sites
        except FileNotFoundError:
            logging.error("Arquivo sites.json não encontrado")
            return []
        except json.JSONDecodeError as e:
            logging.error(f"Erro ao ler sites.json: {e}")
            return []
    
    def check_all_sites(self):
        """Verifica todos os sites configurados"""
        logging.info("Iniciando verificação de todos os sites...")
        
        for site_config in self.sites:
            try:
                result = self.monitor.check_site(site_config)
                
                # Salvar no banco de dados
                self.db.log_check(
                    site_name=result['name'],
                    url=result['url'],
                    status_code=result['status_code'],
                    response_time=result['response_time'],
                    ssl_days=result['ssl_days_remaining'],
                    is_up=result['is_up'],
                    error_message=result['error_message']
                )
                
                # Verificar se houve mudança de estado
                self.check_state_change(result)
                
                # Log do resultado
                status = "UP" if result['is_up'] else "DOWN"
                logging.info(f"{result['name']}: {status} - {result.get('response_time', 0):.0f}ms")
                
            except Exception as e:
                logging.error(f"Erro ao verificar {site_config['name']}: {e}")
    
    def check_state_change(self, current_result: Dict):
        """Verifica mudanças de estado e envia alertas"""
        site_name = current_result['name']
        current_status = current_result['is_up']
        
        # Obter último status do banco
        last_record = self.db.get_last_status(site_name)
        
        if last_record and len(self.db.get_site_history(site_name, limit=2)) > 1:
            # Pegar o penúltimo registro para comparar
            history = self.db.get_site_history(site_name, limit=2)
            if len(history) >= 2:
                previous_status = history[1]['is_up']
                
                # Site ficou indisponível
                if previous_status and not current_status:
                    self.send_alert(current_result, "down")
                
                # Site se recuperou
                elif not previous_status and current_status:
                    self.send_alert(current_result, "recovered")
        
        # Verificar alerta de SSL
        ssl_days = current_result.get('ssl_days_remaining')
        if ssl_days is not None and ssl_days <= 30 and current_status:
            # Verificar se já enviamos alerta de SSL recentemente
            if not self.recently_alerted_ssl(site_name):
                self.send_alert(current_result, "ssl_warning")
    
    def recently_alerted_ssl(self, site_name: str) -> bool:
        """Verifica se já foi enviado alerta de SSL nas últimas 24h"""
        # Implementação simplificada - em produção, verificar tabela de alertas
        return False
    
    def send_alert(self, result: Dict, alert_type: str):
        """Envia alerta e registra no banco"""
        try:
            sent_via = self.notifier.send_alert(result, alert_type)
            
            if sent_via:
                message = f"{alert_type.upper()}: {result['name']}"
                for channel in sent_via:
                    self.db.log_alert(result['name'], alert_type, message, channel)
                
                logging.info(f"Alerta enviado para {result['name']} via {', '.join(sent_via)}")
            else:
                logging.warning(f"Nenhum canal de notificação configurado para {result['name']}")
                
        except Exception as e:
            logging.error(f"Erro ao enviar alerta para {result['name']}: {e}")
    
    def generate_daily_report(self):
        """Gera relatório diário"""
        logging.info("Gerando relatório diário...")
        
        for site_config in self.sites:
            site_name = site_config['name']
            
            # Gerar estatísticas
            stats = self.report_generator.calculate_uptime_percentage(site_name, days=1)
            
            logging.info(f"Relatório {site_name}: {stats['uptime_percentage']:.1f}% uptime, "
                        f"{stats['avg_response_time']:.0f}ms médio")
    
    def run_once(self):
        """Executa uma verificação única"""
        self.check_all_sites()
    
    def run_scheduler(self):
        """Executa o sistema com agendamento"""
        scheduler = BlockingScheduler()
        
        # Verificação principal
        check_interval = int(os.getenv('CHECK_INTERVAL', 300))  # 5 minutos padrão
        scheduler.add_job(
            func=self.check_all_sites,
            trigger=IntervalTrigger(seconds=check_interval),
            id='check_sites',
            name='Verificar Sites',
            replace_existing=True
        )
        
        # Relatório diário às 8h
        scheduler.add_job(
            func=self.generate_daily_report,
            trigger='cron',
            hour=8,
            minute=0,
            id='daily_report',
            name='Relatório Diário'
        )
        
        logging.info(f"Agendador iniciado - Verificação a cada {check_interval} segundos")
        
        try:
            scheduler.start()
        except KeyboardInterrupt:
            logging.info("Sistema interrompido pelo usuário")
            scheduler.shutdown()

def main():
    """Função principal"""
    import sys
    
    system = MonitoringSystem()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'check':
            # Execução única
            system.run_once()
        elif command == 'report':
            # Gerar relatório
            if len(sys.argv) > 2:
                site_name = sys.argv[2]
                filename = system.report_generator.generate_csv_report(site_name)
                print(f"Relatório gerado: {filename}")
            else:
                print("Uso: python main.py report <nome_do_site>")
        elif command == 'chart':
            # Gerar gráfico
            if len(sys.argv) > 2:
                site_name = sys.argv[2]
                filename = system.report_generator.generate_uptime_chart(site_name)
                if filename:
                    print(f"Gráfico gerado: {filename}")
            else:
                print("Uso: python main.py chart <nome_do_site>")
        else:
            print("Comandos disponíveis: check, report, chart")
    else:
        # Execução contínua com agendamento
        system.run_scheduler()

if __name__ == "__main__":
    main()