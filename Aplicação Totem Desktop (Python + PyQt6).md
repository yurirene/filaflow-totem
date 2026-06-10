# Aplicação Totem Desktop (Python + PyQt6)

Esta é uma aplicação desenvolvida para rodar em totens, com suporte a modo Kiosk (tela cheia) e configuração de impressora local.

## Funcionalidades
- **Tela de Configuração**: Defina a URL do sistema e escolha a impressora.
- **Impressão de Teste**: Verifique se a comunicação com a impressora está funcionando.
- **Modo Kiosk**: Abre o sistema em tela cheia sem bordas.
- **Atalho de Saída**: Pressione `ESC` para voltar à tela de configuração.

## Requisitos
- Python 3.9 ou superior.

## Instalação (Windows)

1. Abra o terminal (PowerShell ou CMD) e instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Execute a aplicação:
   ```bash
   python run.py
   ```

## Instalação (Linux/macOS)

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Execute a aplicação:
   ```bash
   python run.py
   ```

## Gerar executável

Consulte o [README.md](README.md) para instruções completas de build com PyInstaller.

---
*Desenvolvido para uso em totens de autoatendimento.*
