import requests
import os
import logging
import tempfile
import subprocess
import sys # Necessário para verificar se está rodando como executável
from typing import Tuple, Optional
from packaging.version import parse as parse_version 

logger = logging.getLogger('BlazeScan') 

# --- CONSTANTES DE ATUALIZAÇÃO ---
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/vhblaze/BlazeScan/main/version/version.txt"
GITHUB_RELEASE_DOWNLOAD_URL = "https://github.com/vhblaze/BlazeScan/releases/download/{version}/BlazeScan.exe"
EXECUTABLE_NAME = "BlazeScan.exe"
VERSION_FILE_REL_PATH = os.path.join("version", "version.txt")
# ---------------------------------

def get_project_root() -> str:
    # ... (função get_project_root permanece a mesma) ...
    """Calcula e retorna o caminho para a raiz do projeto (pasta BlazeScan)."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_local_version() -> Optional[str]:
    # ... (função get_local_version permanece a mesma) ...
    project_root = get_project_root()
    version_file = os.path.join(project_root, VERSION_FILE_REL_PATH)
    
    if not os.path.exists(version_file):
        # Tenta o caminho relativo ao executável (PyInstaller)
        # Usa o caminho onde o executável está
        version_file = os.path.join(os.path.dirname(sys.executable), VERSION_FILE_REL_PATH) 

    logger.debug(f"Verificando versão local em: {version_file}")
    
    try:
        with open(version_file, 'r', encoding='utf-8') as f:
            version = f.read().strip()
            logger.info(f"Versão local encontrada: {version}")
            return version
    except FileNotFoundError:
        logger.error(f"Arquivo de versão não encontrado em: {version_file}")
        return None
    except Exception as e:
        logger.error(f"Erro ao ler versão local: {e}")
        return None

def get_latest_version() -> Optional[str]:
    # ... (função get_latest_version permanece a mesma) ...
    logger.info("Buscando a versão mais recente no GitHub...")
    try:
        response = requests.get(GITHUB_VERSION_URL, timeout=10)
        if response.status_code == 200:
            latest_version = response.text.strip()
            logger.info(f"Versão remota encontrada: {latest_version}")
            return latest_version
        else:
            logger.warning(f"Falha na requisição. Status Code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Falha ao conectar ao GitHub para verificar versão. [Erro: {type(e).__name__}]")
        logger.debug(f"Detalhes do erro: {e}")
        return None

def is_update_available() -> Tuple[bool, Optional[str], Optional[str]]:
    # ... (função is_update_available permanece a mesma) ...
    local_version = get_local_version()
    latest_version = get_latest_version()
    
    if not local_version or not latest_version:
        logger.warning("Não foi possível comparar versões. Pulando checagem.")
        return False, local_version, latest_version
        
    logger.info(f"Comparando versões (Local: {local_version}, Remota: {latest_version})...")

    try:
        if parse_version(latest_version) > parse_version(local_version):
            logger.info("ATUALIZAÇÃO DISPONÍVEL! Versão Remota é mais recente.")
            return True, local_version, latest_version
        else:
            logger.info("Nenhuma atualização necessária. A versão local está atualizada.")
            return False, local_version, latest_version
            
    except Exception as e:
        logger.error(f"Erro na comparação de versões com 'packaging': {e}")
        if latest_version > local_version:
             return True, local_version, latest_version
        else:
             return False, local_version, latest_version

def launch_replacement_script(new_exe_path: str, old_exe_path: str) -> Tuple[bool, str]:
    """
    Cria e executa um script temporário (.bat) que fecha o programa atual,
    substitui o executável e reinicia a nova versão.
    O timeout foi reduzido para ser menos intrusivo.
    """
    old_exe_dir = os.path.dirname(old_exe_path)
    
    script_content = f"""
@echo off
echo Aguardando o BlazeScan atual fechar...
:: 🔑 CORREÇÃO PARA VOICEMOD: Reduz o tempo de espera para 3 segundos.
timeout /t 3 /nobreak > NUL

echo Substituindo executável...
ren "{old_exe_path}" "{EXECUTABLE_NAME}.old" > NUL 2>&1

:: Move o novo executável para o local do antigo
move /Y "{new_exe_path}" "{old_exe_path}"

:: Limpa o backup se o move for bem-sucedido
del "{old_exe_path}.old" > NUL 2>&1

echo Substituição concluída. Iniciando a nova versão...
start "" "{old_exe_path}"

:: Fecha este script temporário e a janela do CMD
del "%~f0"
exit
"""
    # Salva o script no diretório temporário
    bat_path = os.path.join(tempfile.gettempdir(), "update_blazescan.bat")
    try:
        with open(bat_path, 'w') as f:
            f.write(script_content)
        
        # Executa o script BAT de forma não bloqueante
        subprocess.Popen(['cmd', '/c', bat_path], close_fds=True, cwd=old_exe_dir)
        return True, "Script de substituição iniciado. Reinicie o programa para aplicar a atualização."

    except Exception as e:
        logger.error(f"Erro ao criar/executar script BAT: {e}")
        return False, str(e)


def download_update(latest_version: str, local_executable_path: str) -> Tuple[bool, str]:
    # ... (função download_update permanece a mesma) ...
    download_url = GITHUB_RELEASE_DOWNLOAD_URL.format(version=latest_version)
    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, f"{EXECUTABLE_NAME}.new")
    
    logger.info(f"Iniciando download da versão {latest_version} de: {download_url}")

    try:
        with requests.get(download_url, stream=True, timeout=60) as r:
            r.raise_for_status() 
            with open(temp_file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        logger.info(f"Download concluído. Arquivo salvo em {temp_file_path}.")

        success, message = launch_replacement_script(temp_file_path, local_executable_path)
        
        if success:
            # O programa principal deve fechar após esta chamada para o BAT agir
            return True, "Download concluído. O programa será reiniciado em breve para aplicar a atualização."
        else:
            return False, f"Falha ao iniciar o script de substituição: {message}"

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de rede/download ao baixar atualização: {e}")
        return False, f"Erro de rede ao baixar a atualização. Verifique sua conexão. Erro: {e}"
    except Exception as e:
        logger.error(f"Erro inesperado durante o download: {e}")
        return False, f"Erro inesperado no processo de download. Erro: {e}"