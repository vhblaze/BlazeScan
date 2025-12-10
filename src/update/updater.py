import requests
import os
import logging # <-- Novo: Importa a biblioteca de log
from typing import Tuple, Optional

# Configura o logger para ser usado neste módulo
logger = logging.getLogger(__name__)

# URL do arquivo de versão no GitHub
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/vhblaze/BlazeScan/main/version/version.txt"

# Constante para o caminho relativo do arquivo de versão, a partir da raiz do projeto.
# O caminho é: [Raiz]/version/version.txt
VERSION_FILE_REL_PATH = os.path.join("version", "version.txt")

def get_project_root() -> str:
    """Calcula e retorna o caminho para a raiz do projeto (pasta BlazeScan)."""
    # Navega de src/update/updater.py (3 níveis para cima)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_local_version() -> Optional[str]:
    """
    Lê a versão atual do executável a partir do arquivo local.
    """
    project_root = get_project_root()
    version_file = os.path.join(project_root, VERSION_FILE_REL_PATH)
    
    logger.debug(f"Verificando versão local em: {version_file}")
    
    try:
        with open(version_file, 'r', encoding='utf-8') as f: # Adicionado encoding='utf-8' para segurança
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
    """
    Busca a versão mais recente no GitHub.
    """
    logger.info("Buscando a versão mais recente no GitHub...")
    try:
        response = requests.get(GITHUB_VERSION_URL, timeout=5)
        if response.status_code == 200:
            latest_version = response.text.strip()
            logger.info(f"Versão remota encontrada: {latest_version}")
            return latest_version
        else:
            logger.warning(f"Falha na requisição. Status Code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Falha ao conectar ao GitHub para verificar versão: {e}")
        return None

def is_update_available() -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Compara a versão local com a versão do GitHub.
    Retorna (disponível, local_version, latest_version).
    """
    local_version = get_local_version()
    latest_version = get_latest_version()
    
    if not local_version:
        logger.warning("Não foi possível determinar a versão local. Pulando checagem de atualização.")
        return False, None, latest_version
    
    if not latest_version:
        logger.warning("Não foi possível obter a versão remota. Pulando checagem de atualização.")
        return False, local_version, None
        
    logger.info(f"Comparando versões (Local: {local_version}, Remota: {latest_version})...")

    # Para comparação robusta de versões (ex: 1.0.9 < 1.0.10)
    try:
        from packaging.version import parse as parse_version
        
        # A biblioteca 'packaging' é mais confiável para semântica de versão
        if parse_version(latest_version) > parse_version(local_version):
            logger.info("ATUALIZAÇÃO DISPONÍVEL! Versão Remota é mais recente.")
            return True, local_version, latest_version
        else:
            logger.info("Nenhuma atualização necessária. A versão local está atualizada.")
            return False, local_version, latest_version
            
    except ImportError:
        logger.warning("Biblioteca 'packaging' não instalada. Usando comparação de string (menos confiável).")
        # Fallback para comparação de string
        if latest_version > local_version:
            return True, local_version, latest_version
        else:
            return False, local_version, latest_version
            
    except Exception as e:
        logger.error(f"Erro na comparação de versões: {e}")
        return False, local_version, latest_version

def download_update(target_path: str = None) -> Tuple[bool, str]:
    """
    Função PLACEHOLDER para download da atualização.
    Esta função DEVE ser implementada para um sistema de update real.
    """
    logger.warning("A função download_update foi chamada, mas A LÓGICA DE DOWNLOAD AINDA É UM PLACEHOLDER.")
    logger.warning("Você precisa implementar o download e a substituição do executável.")
    
    return False, "Download e substituição do executável/scripts não implementados."

if __name__ == '__main__':
    # Teste (simulado)
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logger.info("-" * 30)
    available, local, latest = is_update_available()
    logger.info(f"Resultado Final: Atualização disponível: {available} (Local: {local}, Remota: {latest})")
    download_update()
    logger.info("-" * 30)