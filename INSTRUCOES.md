# 🚀 Monitor de Sites - Instruções de Uso

## ✅ Sistema Funcionando!

O monitor básico está funcionando perfeitamente usando apenas bibliotecas padrão do Python.

## 📋 Como Usar

### 1. Verificação Única
```bash
python monitor_basico.py check
```

### 2. Ver Status e Uptime
```bash
python monitor_basico.py status
```

### 3. Gerar Relatório
```bash
python monitor_basico.py report
python monitor_basico.py report Google
```

### 4. Monitoramento Contínuo
```bash
python monitor_basico.py continuous
python monitor_basico.py continuous 60  # a cada 60 segundos
```

## ⚙️ Configuração

### Editar Sites Monitorados
Edite o arquivo `sites.json` ou `sites_exemplo.json`:

```json
[
  {
    "name": "Meu Site",
    "url": "https://meusite.com",
    "expected_status": 200
  }
]
```

### Banco de Dados
- Arquivo: `monitoring.db` (SQLite)
- Logs: `monitoring.log`

## 🔧 Funcionalidades Implementadas

- ✅ Monitoramento HTTP com urllib (sem dependências externas)
- ✅ Banco SQLite para histórico
- ✅ Cálculo de uptime
- ✅ Relatórios detalhados
- ✅ Monitoramento contínuo
- ✅ Logs em arquivo
- ✅ Tratamento de erros

## 📊 Exemplo de Saída

```
Monitor Basico de Sites
========================================

Verificando 4 sites...
--------------------------------------------------
Google          | UP     |    275ms
GitHub          | UP     |     63ms
Python.org      | UP     |    156ms
Stack Overflow  | UP     |    234ms
--------------------------------------------------
```

## 🚀 Próximos Passos

Para funcionalidades avançadas (Telegram, WhatsApp, gráficos), instale as dependências:

```bash
pip install -r requirements.txt
python main.py
```

Mas o monitor básico já funciona perfeitamente para monitoramento essencial!