#!/usr/bin/env python3
"""
Exemplo de uso do sistema de monitoramento
Execute este arquivo para testar o sistema rapidamente
"""

import os
import json
from dotenv import load_dotenv
from main import MonitoringSystem

def setup_example():
    """Configura um exemplo básico para teste"""
    
    # Criar arquivo .env de exemplo se não existir
    if not os.path.exists('.env'):
        env_content = """# Configurações de E-mail (Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=seu_email@gmail.com
EMAIL_PASSWORD=sua_senha_app

# Telegram Bot (opcional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Twilio WhatsApp (opcional)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WHATSAPP_TO=whatsapp:+5511999999999

# Configurações de Monitoramento
CHECK_INTERVAL=60
RETRY_COUNT=2
TIMEOUT=15"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Arquivo .env criado - Configure suas credenciais!")
    
    # Criar sites.json de exemplo se não existir
    if not os.path.exists('sites.json'):
        sites_example = [
            {
                "name": "Google",
                "url": "https://www.google.com",
                "check_ssl": True,
                "expected_status": 200,
                "max_response_time": 3000,
                "auth": None
            },
            {
                "name": "GitHub",
                "url": "https://github.com",
                "check_ssl": True,
                "expected_status": 200,
                "max_response_time": 5000,
                "auth": None
            },
            {
                "name": "JSONPlaceholder API",
                "url": "https://jsonplaceholder.typicode.com/posts/1",
                "check_ssl": True,
                "expected_status": 200,
                "max_response_time": 2000,
                "auth": None
            }
        ]
        
        with open('sites.json', 'w', encoding='utf-8') as f:
            json.dump(sites_example, f, indent=2, ensure_ascii=False)
        print("✅ Arquivo sites.json criado com exemplos!")

def run_test():
    """Executa um teste básico do sistema"""
    print("🚀 Iniciando teste do sistema de monitoramento...")
    print("-" * 50)
    
    # Carregar configurações
    load_dotenv()
    
    # Criar instância do sistema
    system = MonitoringSystem()
    
    if not system.sites:
        print("❌ Nenhum site configurado para monitoramento!")
        return
    
    print(f"📊 Monitorando {len(system.sites)} sites:")
    for site in system.sites:
        print(f"  - {site['name']}: {site['url']}")
    
    print("\n🔍 Executando verificação única...")
    system.run_once()
    
    print("\n📈 Gerando estatísticas...")
    for site in system.sites:
        stats = system.report_generator.calculate_uptime_percentage(site['name'], days=1)
        print(f"  {site['name']}: {stats['uptime_percentage']:.1f}% uptime")
    
    print("\n✅ Teste concluído!")
    print("\nPara executar continuamente: python main.py")
    print("Para gerar relatórios: python main.py report 'Nome do Site'")
    print("Para gerar gráficos: python main.py chart 'Nome do Site'")

if __name__ == "__main__":
    print("🔧 Configurando ambiente de exemplo...")
    setup_example()
    print("\n" + "="*50)
    run_test()