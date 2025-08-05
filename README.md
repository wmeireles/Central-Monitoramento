# 🖥️ Monitor de Sites e APIs

Sistema completo em Python para monitoramento de disponibilidade de sites e APIs com alertas inteligentes e relatórios detalhados.

## 🚀 Funcionalidades

- ✅ **Monitoramento HTTP** - Status codes e tempo de resposta
- 🔒 **Verificação SSL** - Dias restantes para expiração
- 📧 **Alertas Múltiplos** - E-mail, Telegram e WhatsApp
- 📊 **Relatórios** - CSV, Excel e gráficos
- 🗄️ **Histórico SQLite** - Armazenamento persistente
- ⏰ **Agendamento** - Verificações automáticas
- 🔄 **Sistema de Retry** - Tolerância a falhas temporárias

## 🎯 Duas Versões Disponíveis

### 1. **Monitor Básico** (Recomendado para início)
- ✅ **Zero dependências externas** - Apenas bibliotecas padrão do Python
- ✅ **Funciona imediatamente** - Sem problemas de instalação
- ✅ **Completo** - Monitoramento, relatórios e histórico

### 2. **Monitor Avançado** 
- 📧 Notificações por e-mail, Telegram e WhatsApp
- 📈 Gráficos com matplotlib
- 🔄 Agendamento com APScheduler

## 🚀 Início Rápido

### Monitor Básico (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/monitor-sites.git
cd monitor-sites

# Execute imediatamente (sem instalações)
python monitor_basico.py
```

### Monitor Avançado

```bash
# Instale as dependências
pip install -r requirements.txt

# Configure as credenciais
cp .env.example .env
# Edite o .env com suas credenciais

# Execute o sistema completo
python main.py
```

## 📋 Comandos Disponíveis

### Monitor Básico
```bash
python monitor_basico.py check              # Verificação única
python monitor_basico.py status             # Status e uptime
python monitor_basico.py report             # Relatório geral
python monitor_basico.py report Google      # Relatório específico
python monitor_basico.py continuous [300]   # Monitoramento contínuo
```

### Monitor Avançado
```bash
python main.py                              # Execução contínua
python main.py check                        # Verificação única
python main.py report "Site"                # Gerar relatório
python main.py chart "Site"                 # Gerar gráfico
```

## ⚙️ Configuração

### Sites para Monitorar
Edite `sites.json`:

```json
[
  {
    "name": "Meu Site",
    "url": "https://meusite.com",
    "check_ssl": true,
    "expected_status": 200,
    "max_response_time": 5000,
    "auth": null
  }
]
```

### Autenticação para APIs
```json
{
  "name": "API Protegida",
  "url": "https://api.exemplo.com/health",
  "auth": {
    "type": "bearer",
    "token": "seu_token_aqui"
  }
}
```

## 📊 Exemplo de Saída

```
Monitor Basico de Sites
========================================

Verificando 4 sites...
--------------------------------------------------
Google          | UP     |    275ms
GitHub          | UP     |     63ms
Python.org      | UP     |    156ms
Stack Overflow  | DOWN   |      0ms
                  Erro: HTTP Error 503: Service Unavailable
--------------------------------------------------

Status Atual dos Sites
==================================================
Google          | UP     | 100.0% |    275ms | 2025-01-15 14:30
GitHub          | UP     |  99.2% |     63ms | 2025-01-15 14:30
Python.org      | UP     |  98.5% |    156ms | 2025-01-15 14:30
Stack Overflow  | DOWN   |  95.1% |      0ms | 2025-01-15 14:30
```

## 🗄️ Estrutura de Dados

### Banco SQLite (`monitoring.db`)
- **checks** - Histórico de verificações
- **alerts** - Log de alertas enviados

### Logs (`monitoring.log`)
- Eventos em tempo real
- Erros e alertas
- Estatísticas de execução

## 🔧 Tecnologias

### Monitor Básico
- **Python 3.7+** - Linguagem principal
- **urllib** - Requisições HTTP
- **sqlite3** - Banco de dados
- **smtplib** - E-mail (opcional)

### Monitor Avançado
- **requests** - Requisições HTTP avançadas
- **APScheduler** - Agendamento de tarefas
- **python-telegram-bot** - Notificações Telegram
- **twilio** - Notificações WhatsApp
- **matplotlib** - Gráficos
- **openpyxl** - Relatórios Excel

## 📈 Funcionalidades Avançadas

### Alertas Inteligentes
- 🔴 **Site Down** - Quando site fica indisponível
- 🟢 **Recuperação** - Quando site volta ao ar
- ⚠️ **SSL Expirando** - Certificado expira em < 30 dias
- 📊 **Relatórios Diários** - Resumo automático

### Relatórios
- **CSV/Excel** - Dados estruturados para análise
- **Gráficos PNG** - Visualização de uptime e performance
- **Estatísticas** - Uptime, tempo médio de resposta
- **Histórico** - Dados persistentes no SQLite

## 🚀 Extensões Futuras

- [ ] Dashboard web (Flask/FastAPI)
- [ ] Integração Slack/Discord
- [ ] Monitoramento de bancos de dados
- [ ] Métricas Prometheus
- [ ] Container Docker
- [ ] API REST

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'Adiciona nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

**Seu Nome**
- LinkedIn: [seu-perfil](https://linkedin.com/in/seu-perfil)
- GitHub: [@seu-usuario](https://github.com/seu-usuario)

---

⭐ **Se este projeto foi útil, deixe uma estrela!**