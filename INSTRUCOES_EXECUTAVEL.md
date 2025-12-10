# Instruções para Criar o Executável BlazeScan

Este documento fornece instruções detalhadas para criar um executável (.exe) do BlazeScan e configurar o sistema de atualização automática.

## 📦 Pré-requisitos

1. **Python 3.8+** instalado no Windows
2. **Todas as dependências** instaladas: `pip install -r requirements.txt`
3. **PyInstaller** instalado: `pip install pyinstaller`

## 🔨 Criando o Executável

### Método 1: Executável Simples (Com Console)

```bash
pyinstaller --onefile --name BlazeScan main.py
```

### Método 2: Executável GUI (Sem Console) - RECOMENDADO

```bash
pyinstaller --onefile --windowed --name BlazeScan main.py
```

### Método 3: Executável com Ícone Personalizado

Primeiro, crie ou obtenha um arquivo `.ico` (ícone) e salve como `icon.ico` na raiz do projeto.

```bash
pyinstaller --onefile --windowed --name BlazeScan --icon=icon.ico main.py
```

### Método 4: Configuração Avançada (Incluindo Arquivos de Versão)

Crie um arquivo `BlazeScan.spec` com o seguinte conteúdo:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('version/version.txt', 'version')],  # Inclui o arquivo de versão
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BlazeScan',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False = sem console, True = com console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # Opcional: adicione seu ícone aqui
)
```

Depois execute:

```bash
pyinstaller BlazeScan.spec
```

## 📂 Localização do Executável

Após a compilação, o executável estará em:

```
BlazeScan/
└── dist/
    └── BlazeScan.exe
```

## 🚀 Testando o Executável

1. Navegue até a pasta `dist/`
2. Execute `BlazeScan.exe` como **Administrador** (clique com o botão direito → Executar como administrador)
3. Teste todas as funcionalidades:
   - Limpeza de arquivos temporários
   - Otimização de energia
   - Verificação de atualização

## 🔄 Configurando o Sistema de Atualização

### Passo 1: Configurar o Repositório GitHub

1. Certifique-se de que o arquivo `version/version.txt` está no repositório
2. Faça commit e push:

```bash
git add .
git commit -m "Versão inicial 1.0.0"
git push origin main
```

### Passo 2: Criar uma Release no GitHub

1. Vá para o repositório no GitHub: https://github.com/vhblaze/BlazeScan
2. Clique em **Releases** → **Create a new release**
3. Preencha:
   - **Tag version:** `v1.0.0`
   - **Release title:** `BlazeScan v1.0.0`
   - **Description:** Descreva as funcionalidades da versão
4. Faça upload do executável `BlazeScan.exe` como um asset
5. Clique em **Publish release**

### Passo 3: Atualizar para uma Nova Versão

Quando quiser publicar uma atualização:

1. **Atualize o código** com as novas funcionalidades
2. **Atualize a versão** no arquivo `version/version.txt`:

```bash
echo "1.0.1" > version/version.txt
```

3. **Faça commit e push:**

```bash
git add .
git commit -m "Atualização para versão 1.0.1 - Novas funcionalidades"
git push origin main
```

4. **Crie uma nova Release** no GitHub com a nova versão
5. **Faça upload do novo executável**

### Passo 4: Como Funciona a Atualização Automática

Quando o usuário abrir o BlazeScan:

1. O programa lê a versão local (`version/version.txt`)
2. Busca a versão remota no GitHub: `https://raw.githubusercontent.com/vhblaze/BlazeScan/main/version/version.txt`
3. Compara as versões
4. Se houver uma versão mais recente, exibe um pop-up perguntando se o usuário deseja atualizar

**Nota:** Atualmente, o sistema apenas **notifica** sobre atualizações. Para implementar o download automático, você precisará adicionar lógica adicional na função `download_update()` em `src/update/updater.py`.

## 🔧 Implementando Download Automático de Atualização (Opcional)

Para implementar o download automático, edite o arquivo `src/update/updater.py`:

```python
def download_update(target_path: str) -> Tuple[bool, str]:
    """
    Baixa a nova versão do executável do GitHub.
    """
    import requests
    import os
    
    # URL do executável na última release
    GITHUB_RELEASE_URL = "https://github.com/vhblaze/BlazeScan/releases/latest/download/BlazeScan.exe"
    
    try:
        response = requests.get(GITHUB_RELEASE_URL, stream=True, timeout=30)
        if response.status_code == 200:
            # Salva o novo executável
            with open(target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True, "Atualização baixada com sucesso!"
        else:
            return False, f"Erro ao baixar: Status {response.status_code}"
    except Exception as e:
        return False, f"Erro ao baixar atualização: {e}"
```

## ⚠️ Considerações Importantes

### Permissões de Administrador

Para que o BlazeScan funcione completamente, ele precisa ser executado como **Administrador**, especialmente para:

- Alterar o plano de energia do Windows
- Limpar arquivos de sistema protegidos
- Modificar configurações do MSConfig

### Antivírus e Windows Defender

Executáveis criados com PyInstaller podem ser detectados como falsos positivos por antivírus. Para evitar isso:

1. **Assine digitalmente o executável** (requer certificado de assinatura de código)
2. **Adicione exceções** no Windows Defender
3. **Envie o executável para análise** nos principais antivírus (VirusTotal)

### Tamanho do Executável

O executável gerado pode ser grande (30-50 MB) porque inclui o interpretador Python e todas as dependências. Isso é normal para aplicações PyInstaller.

## 📝 Checklist de Distribuição

Antes de distribuir o BlazeScan:

- [ ] Testei o executável em uma máquina limpa (sem Python instalado)
- [ ] Testei como Administrador
- [ ] Verifiquei que o sistema de atualização funciona
- [ ] Criei uma Release no GitHub com o executável
- [ ] Atualizei o README.md com instruções de uso
- [ ] Adicionei um ícone personalizado (opcional)
- [ ] Testei em diferentes versões do Windows (10/11)

## 🎯 Próximos Passos

1. **Crie o executável** usando um dos métodos acima
2. **Teste completamente** em um ambiente Windows 11
3. **Publique no GitHub** como uma Release
4. **Compartilhe** com usuários

---

**Dúvidas?** Abra uma issue no repositório: https://github.com/vhblaze/BlazeScan/issues
