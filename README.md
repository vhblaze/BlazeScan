# BlazeScan - Otimizador de Sistema para Windows 11

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%2011-lightgrey.svg)

**BlazeScan** é um otimizador de sistema completo para Windows 11 que realiza limpeza de arquivos temporários, otimização de energia e verificação automática de atualizações via GitHub.

## 🚀 Funcionalidades

- **Limpeza Completa de Sistema:**
  - Limpeza de cache do sistema
  - Remoção de arquivos temporários (`%TEMP%`)
  - Limpeza de arquivos do Windows Temp
  - Exibição do espaço liberado em MB/GB

- **Otimização de Desempenho:**
  - Alteração automática do plano de energia para "Desempenho Máximo" ou "Alto Desempenho"
  - Instruções para otimização manual do MSConfig (núcleos/threads)
  - Orientações para desfragmentação de disco

- **Sistema de Atualização Automática:**
  - Verificação de versão no GitHub
  - Pop-up de notificação quando há nova versão disponível
  - Comparação inteligente de versões usando `packaging`

- **Interface Gráfica Moderna:**
  - Interface construída com CustomTkinter
  - Design limpo e intuitivo
  - Área de log em tempo real
  - Execução assíncrona para não travar a interface

## 📋 Requisitos

- **Sistema Operacional:** Windows 11 (ou Windows 10)
- **Python:** 3.8 ou superior
- **Dependências:** Listadas em `requirements.txt`

## 🔧 Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/vhblaze/BlazeScan.git
cd BlazeScan
```

### 2. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 3. Execute a Aplicação

```bash
python main.py
```

**Importante:** Para funcionalidades completas (como alteração do plano de energia), execute como **Administrador**.

## 🏗️ Estrutura do Projeto

```
BlazeScan/
├── src/
│   ├── backend/
│   │   ├── __init__.py
│   │   └── cleanup.py          # Lógica de limpeza e otimização
│   ├── frontend/
│   │   ├── __init__.py
│   │   └── ui.py                # Interface gráfica (CustomTkinter)
│   ├── update/
│   │   ├── __init__.py
│   │   └── updater.py           # Sistema de atualização via GitHub
│   ├── utils/
│   │   ├── __init__.py
│   │   └── system.py            # Funções utilitárias de sistema
│   └── __init__.py
├── version/
│   └── version.txt              # Versão atual do projeto
├── main.py                      # Ponto de entrada principal
├── requirements.txt             # Dependências do projeto
└── README.md                    # Documentação
```

## 📦 Criando um Executável (.exe)

Para distribuir o BlazeScan como um executável independente, use o **PyInstaller**:

### 1. Instale o PyInstaller

```bash
pip install pyinstaller
```

### 2. Crie o Executável

```bash
pyinstaller --onefile --windowed --name BlazeScan --icon=icon.ico main.py
```

**Opções:**
- `--onefile`: Cria um único arquivo executável
- `--windowed`: Remove a janela do console (apenas GUI)
- `--name BlazeScan`: Nome do executável
- `--icon=icon.ico`: Ícone personalizado (opcional)

O executável será criado na pasta `dist/`.

## 🔄 Sistema de Atualização

O BlazeScan verifica automaticamente se há uma nova versão disponível no GitHub ao iniciar.

### Como Funciona:

1. O arquivo `version/version.txt` local contém a versão atual instalada.
2. Ao iniciar, o BlazeScan busca o arquivo `version.txt` no repositório GitHub.
3. Se a versão remota for maior, um pop-up é exibido perguntando se o usuário deseja atualizar.

### Para Publicar uma Nova Versão:

1. Atualize o arquivo `version/version.txt` no repositório com a nova versão (ex: `1.0.1`).
2. Faça commit e push das alterações.
3. (Opcional) Crie uma Release no GitHub com o executável atualizado.

```bash
git add version/version.txt
git commit -m "Atualização para versão 1.0.1"
git push origin main
```

## ⚠️ Avisos Importantes

- **Permissões de Administrador:** Algumas funcionalidades (como alteração do plano de energia) requerem privilégios de administrador.
- **Arquivos em Uso:** O programa não conseguirá deletar arquivos que estão sendo usados por outros processos.
- **Backup:** Recomenda-se fazer backup de dados importantes antes de executar limpezas de sistema.

## 🛠️ Desenvolvimento

### Tecnologias Utilizadas:

- **Frontend:** CustomTkinter (interface gráfica moderna)
- **Backend:** Python padrão (os, shutil, subprocess)
- **Atualização:** requests, packaging
- **Arquitetura:** Separação clara entre frontend e backend

### Contribuindo:

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

## 👤 Autor

**vhblaze**

- GitHub: [@vhblaze](https://github.com/vhblaze)
- Repositório: [BlazeScan](https://github.com/vhblaze/BlazeScan)

## 🙏 Agradecimentos

- Biblioteca [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) por fornecer uma interface moderna para Tkinter.
- Comunidade Python por todas as ferramentas incríveis.

---

**Nota:** Este software é fornecido "como está", sem garantias de qualquer tipo. Use por sua conta e risco.
