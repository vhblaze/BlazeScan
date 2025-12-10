# -*- mode: python ; coding: utf-8 -*-
import sys
import os # Importa a biblioteca os

# --- CORREÇÃO DE ERRO: Removida a dependência de Path(__file__).parent ---
# Assumimos que o comando é rodado na raiz do projeto
sys.path.append('src') # Adiciona a pasta src ao path para que os imports funcionem

# 1. Obter a estrutura do Python (caminhos dos módulos e dependências)
block_cipher = None
a = Analysis(
    ['main.py'],
    pathex=['.'], # Usa o diretório atual como base para a análise
    binaries=[],
    datas=[
        # Caminhos relativos ao root do projeto
        ('version\\version.txt', 'version'), # Inclui o arquivo de versão
        ('blazescan_logo.ico', '.') # Inclui o ícone
    ],
    hiddenimports=[
        'pkg_resources.py2_warn' 
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 2. Configurações do Executável (EXE)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='BlazeScan',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, 
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    
    # CRÍTICO: Anexa o manifesto para UAC
    manifest='blazescan_manifest.xml',
    
    # CRÍTICO: Define o ícone do executável
    icon='blazescan_logo.ico'
)

# 3. Configurações do Arquivo (COLLECT)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BlazeScan'
)