import requests
import ssl
import socket
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

class SiteMonitor:
    def __init__(self, timeout: int = 30, retry_count: int = 3):
        self.timeout = timeout
        self.retry_count = retry_count
        self.session = requests.Session()
        
    def check_site(self, site_config: Dict) -> Dict:
        """Verifica um site e retorna o status completo"""
        result = {
            'name': site_config['name'],
            'url': site_config['url'],
            'is_up': False,
            'status_code': None,
            'response_time': None,
            'ssl_days_remaining': None,
            'error_message': None,
            'timestamp': datetime.now()
        }
        
        for attempt in range(self.retry_count):
            try:
                # Preparar headers de autenticação se necessário
                headers = {}
                if site_config.get('auth'):
                    auth = site_config['auth']
                    if auth['type'] == 'bearer':
                        headers['Authorization'] = f"Bearer {auth['token']}"
                    elif auth['type'] == 'basic':
                        # Para basic auth, usar requests.auth.HTTPBasicAuth
                        pass
                
                # Fazer a requisição
                start_time = datetime.now()
                response = self.session.get(
                    site_config['url'], 
                    timeout=self.timeout,
                    headers=headers,
                    verify=True
                )
                end_time = datetime.now()
                
                # Calcular tempo de resposta
                response_time = (end_time - start_time).total_seconds() * 1000
                result['response_time'] = response_time
                result['status_code'] = response.status_code
                
                # Verificar se o status é o esperado
                expected_status = site_config.get('expected_status', 200)
                max_response_time = site_config.get('max_response_time', 5000)
                
                if response.status_code == expected_status and response_time <= max_response_time:
                    result['is_up'] = True
                else:
                    result['error_message'] = f"Status: {response.status_code}, Tempo: {response_time:.0f}ms"
                
                # Verificar SSL se solicitado
                if site_config.get('check_ssl', False):
                    ssl_days = self._check_ssl_expiry(site_config['url'])
                    result['ssl_days_remaining'] = ssl_days
                    
                    if ssl_days is not None and ssl_days < 30:
                        if result['is_up']:
                            result['error_message'] = f"SSL expira em {ssl_days} dias"
                        else:
                            result['error_message'] += f", SSL expira em {ssl_days} dias"
                
                break  # Sucesso, sair do loop de retry
                
            except requests.exceptions.RequestException as e:
                result['error_message'] = str(e)
                if attempt == self.retry_count - 1:  # Última tentativa
                    logging.error(f"Falha ao verificar {site_config['name']} após {self.retry_count} tentativas: {e}")
                else:
                    logging.warning(f"Tentativa {attempt + 1} falhou para {site_config['name']}: {e}")
        
        return result
    
    def _check_ssl_expiry(self, url: str) -> Optional[int]:
        """Verifica quantos dias restam para o certificado SSL expirar"""
        try:
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
            
            if parsed_url.scheme != 'https':
                return None
            
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
            # Converter data de expiração
            expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            days_remaining = (expiry_date - datetime.now()).days
            
            return days_remaining
            
        except Exception as e:
            logging.error(f"Erro ao verificar SSL para {url}: {e}")
            return None