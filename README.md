# Filaflow Totem

Aplicação desktop para totens de autoatendimento, com modo kiosk (tela cheia), configuração de URL e impressora local.

## Funcionalidades

- Tela de configuração (URL do sistema e impressora)
- Impressão de teste
- Modo kiosk em tela cheia
- Impressão automática de senhas via bridge com o Filaflow web
- Pressione `ESC` para voltar à tela de configuração

## Estrutura do projeto

```
filaflow-totem/
├── totem/                  # Pacote da aplicação
│   ├── app.py              # Janela principal
│   ├── config_screen.py    # Tela de configuração
│   ├── kiosk_screen.py     # Tela kiosk (WebEngine + QWebChannel)
│   ├── bridge.py           # Ponte JS ↔ Python para impressão
│   ├── printing.py         # Impressão térmica (Windows/Linux)
│   └── paths.py            # Caminhos (dev e executável)
├── scripts/
│   ├── build.sh            # Build Linux/macOS
│   └── build.bat           # Build Windows
├── totem.spec              # Configuração PyInstaller
├── run.py                  # Entrada para desenvolvimento
└── requirements.txt
```

## Desenvolvimento

Requisitos: Python 3.9+

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
# ou: python -m totem
```

### Dependências por plataforma

| Plataforma | Pacote extra |
|------------|--------------|
| Windows    | `pywin32`    |
| Linux      | `pycups`     |

## Gerar executável

O build usa [PyInstaller](https://pyinstaller.org/) em modo `onedir` (pasta com binário e dependências), recomendado para PyQt6 WebEngine.

### Windows

```bat
scripts\build.bat
```

Saída: `dist\FilaflowTotem\FilaflowTotem.exe`

### Linux / macOS

```bash
chmod +x scripts/build.sh
./scripts/build.sh
```

Saída:
- **Linux:** `dist/FilaflowTotem/FilaflowTotem`
- **macOS:** `dist/FilaflowTotem.app`

> O executável deve ser gerado **na mesma plataforma** onde será usado (Windows, Linux ou macOS).

### Build manual

```bash
pip install -r requirements-build.txt
pyinstaller --clean --noconfirm totem.spec
```

## Deploy

1. Copie a pasta `dist/FilaflowTotem/` (ou `FilaflowTotem.app` no macOS) para o totem.
2. Execute o binário. Na primeira execução, configure URL e impressora.
3. O arquivo `config.json` é criado **ao lado do executável** e persiste entre reinícios.

## Integração com Filaflow

O app expõe `window.totemBridge` via QWebChannel para a página `/totem` do Filaflow. Quando o paciente escolhe um serviço:

1. O Filaflow emite a senha no servidor
2. A página chama `totemBridge.printTicket(...)` automaticamente
3. O desktop imprime na impressora configurada em `config.json` (layout térmico 58/80mm)
4. A tela volta ao início após alguns segundos

Configure a URL do totem apontando para `https://seu-dominio/totem`.

## Notas

- Impressão no Linux usa CUPS (`pycups`).
- Impressão no Windows usa `pywin32`.
- No macOS, instale `pycups` manualmente se precisar testar impressão local.
