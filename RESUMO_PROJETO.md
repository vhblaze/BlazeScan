# 📋 Resumo do Projeto BlazeScan

## 🎯 Objetivo

Criar um otimizador de sistema completo para Windows 11 com interface gráfica moderna, sistema de limpeza automática e atualização via GitHub.

## 📁 Estrutura de Arquivos Criados

```
BlazeScan/
├── src/
│   ├── __init__.py
│   ├── backend/
│   │   ├── __init__.py
│   │   └── cleanup.py          # Lógica de limpeza e otimização
│   ├── frontend/
│   │   ├── __init__.py
│   │   └── ui.py                # Interface gráfica com CustomTkinter
│   ├── update/
│   │   ├── __init__.py
│   │   └── updater.py           # Sistema de atualização via GitHub
│   └── utils/
│       ├── __init__.py
│       └── system.py            # Funções utilitárias
├── version/
│   └── version.txt              # Versão atual: 1.0.0
├── main.py                      # Ponto de entrada principal
├── requirements.txt             # Dependências do projeto
├── README.md                    # Documentação completa
├── INSTRUCOES_EXECUTAVEL.md    # Guia para criar o .exe
├── LICENSE                      # Licença MIT
└── .gitignore                   # Arquivos a serem ignorados pelo Git
```

## 🔧 Funcionalidades Implementadas

### 1. Backend (src/backend/cleanup.py)

- ✅ Limpeza de arquivos temporários (`%TEMP%`)
- ✅ Limpeza de cache do Windows (`C:\Windows\Temp`)
- ✅ Cálculo do espaço liberado em MB/GB
- ✅ Otimização do plano de energia (Desempenho Máximo/Alto)
- ✅ Instruções para otimização manual do MSConfig
- ✅ Tratamento de erros para arquivos em uso

### 2. Frontend (src/frontend/ui.py)

- ✅ Interface gráfica moderna com CustomTkinter
- ✅ Área de log em tempo real
- ✅ Exibição do espaço limpo
- ✅ Execução assíncrona (não trava a interface)
- ✅ Pop-up de notificação de atualização

### 3. Sistema de Atualização (src/update/updater.py)

- ✅ Verificação de versão no GitHub
- ✅ Comparação inteligente de versões (usando `packaging`)
- ✅ Pop-up perguntando se o usuário quer atualizar
- ✅ URL configurada para o repositório: `https://github.com/vhblaze/BlazeScan`

### 4. Utilitários (src/utils/system.py)

- ✅ Função para obter caminhos temporários do Windows
- ✅ Função para executar comandos do Windows
- ✅ Função para alterar plano de energia
- ✅ Função para formatar bytes (KB, MB, GB)

## 📦 Dependências

```
customtkinter>=5.2.0    # Interface gráfica moderna
requests>=2.31.0        # Requisições HTTP para verificar atualizações
packaging>=23.0         # Comparação de versões
```

## 🚀 Como Usar

### 1. Instalação das Dependências

```bash
pip install -r requirements.txt
```

### 2. Executar o Programa

```bash
python main.py
```

**Importante:** Execute como **Administrador** para funcionalidades completas.

### 3. Criar o Executável (.exe)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name BlazeScan main.py
```

O executável estará em `dist/BlazeScan.exe`.

## 🔄 Sistema de Atualização

### Como Funciona:

1. O arquivo `version/version.txt` local contém a versão atual (1.0.0)
2. Ao iniciar, o programa busca a versão no GitHub:
   ```
   https://raw.githubusercontent.com/vhblaze/BlazeScan/main/version/version.txt
   ```
3. Se a versão remota for maior, exibe um pop-up

### Para Publicar uma Nova Versão:

1. Atualize o arquivo `version/version.txt` no repositório
2. Faça commit e push:
   ```bash
   echo "1.0.1" > version/version.txt
   git add version/version.txt
   git commit -m "Atualização para versão 1.0.1"
   git push origin main
   ```
3. Crie uma Release no GitHub com o novo executável

## ⚠️ Considerações Importantes

### Permissões de Administrador

O programa precisa ser executado como **Administrador** para:

- Alterar o plano de energia do Windows
- Limpar arquivos de sistema protegidos
- Acessar diretórios com permissões restritas

### Arquivos em Uso

O programa **não conseguirá deletar** arquivos que estão sendo usados por outros processos. Isso é esperado e tratado silenciosamente.

### Antivírus

Executáveis criados com PyInstaller podem ser detectados como falsos positivos. Considere:

- Assinar digitalmente o executável
- Adicionar exceções no Windows Defender
- Enviar para análise no VirusTotal

## 🎨 Customização

### Alterar Planos de Energia

Edite `src/utils/system.py` e modifique o dicionário `POWER_PLAN_GUIDS` para adicionar ou remover planos.

### Adicionar Mais Caminhos de Limpeza

Edite `src/utils/system.py` na função `get_temp_paths()` para adicionar mais diretórios.

### Personalizar a Interface

Edite `src/frontend/ui.py` para alterar:

- Cores: `ctk.set_default_color_theme("blue")`
- Tamanho da janela: `self.geometry("500x400")`
- Textos e labels

## 📝 Próximos Passos

1. **Testar o programa** em um ambiente Windows 11
2. **Criar o executável** usando PyInstaller
3. **Publicar no GitHub** como uma Release
4. **Testar o sistema de atualização** alterando a versão no repositório

## 🔗 Links Úteis

- **Repositório GitHub:** https://github.com/vhblaze/BlazeScan
- **CustomTkinter Docs:** https://github.com/TomSchimansky/CustomTkinter
- **PyInstaller Docs:** https://pyinstaller.org/en/stable/

## 🐛 Solução de Problemas

### Erro: "ModuleNotFoundError: No module named 'customtkinter'"

**Solução:** Instale as dependências:
```bash
pip install -r requirements.txt
```

### Erro: "PermissionError: [WinError 5] Access is denied"

**Solução:** Execute o programa como Administrador.

### O executável não funciona em outra máquina

**Solução:** Certifique-se de que:
- O executável foi criado com `--onefile`
- A máquina de destino tem Windows 10/11
- O Windows Defender não está bloqueando o arquivo

## 📞 Suporte

Para dúvidas ou problemas, abra uma issue no GitHub:
https://github.com/vhblaze/BlazeScan/issues

---

**Desenvolvido por vhblaze** | **Licença MIT** | **2025**
