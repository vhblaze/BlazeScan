import os
import subprocess
import logging
from typing import List, Tuple, Optional, Dict
import shutil # Importação necessária para clean_directory

logger = logging.getLogger('BlazeScan')

# ====================================================================
# CONSTANTES E VARIÁVEIS DE CONFIGURAÇÃO
# ====================================================================

POWER_PLAN_GUIDS = {
    "MAXIMUM_PERFORMANCE": "e9a42b02-d5df-448d-aa00-03f147498387",
    "HIGH_PERFORMANCE": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
    "BALANCED": "381b4222-f694-41f0-9685-ce5920ae7518",
    "POWER_SAVER": "a1841308-3541-4fab-bc81-f71556f20b4a"
}

OPT_PROCESSES_TO_KILL: List[str] = [
    "spotify.exe",
    "epicgameslauncher.exe", 
    "steamwebhelper.exe", 
    "teams.exe",     
    "zoom.exe",      
    "onedrive.exe",  
    "dropbox.exe", 
    "utorrent.exe", 
    "qbittorrent.exe",
    "AnyDesk.exe",     
    "TeamViewer.exe",      
    "chrome.exe",          
    "firefox.exe",             
    "msedge.exe", 
    "opera.exe" ,
    "copilot.exe",
]

# ====================================================================
# FUNÇÕES DE UTILIDADE GERAL
# ====================================================================

def format_bytes(size_in_bytes: int) -> str:
    """Formata um número de bytes para uma string legível."""
    if size_in_bytes == 0:
        return "0 Bytes"
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    size = float(size_in_bytes)
    while size >= 1024.0 and i < len(units) - 1:
        size /= 1024.0
        i += 1
    return f"{size:.2f} {units[i]}"

def execute_windows_command(command: List[str]) -> Tuple[bool, str]:
    """Executa um comando do Windows e retorna o status e a saída (stdout + stderr)."""
    command_str = " ".join(command)
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=True,
            check=False # Garante que não levante exceção em códigos de retorno diferentes de zero
        )
        
        stdout_output = result.stdout.strip()
        stderr_output = result.stderr.strip()
        
        if result.returncode == 0:
            logger.debug(f"Comando executado com sucesso: {command[0]}")
            return True, stdout_output
        
        else:
            # Taskkill pode retornar erro se o processo não for encontrado (tratamento específico)
            if "not found" in stderr_output.lower() or "não encontrado" in stderr_output.lower():
                logger.debug(f"Comando '{command[0]}' retornou erro esperado (Processo não encontrado).")
                return True, f"AVISO: {stderr_output}" 
            
            error_message = f"CÓDIGO {result.returncode}: {stderr_output}"
            logger.error(f"Falha ao executar '{command_str}'. Saída de Erro: {error_message}")
            return False, error_message
            
    except FileNotFoundError:
        logger.error(f"Comando não encontrado: {command[0]}")
        return False, f"Comando não encontrado: {command[0]}"
        
    except Exception as e:
        logger.error(f"Erro inesperado ao executar '{command_str}': {e}")
        return False, f"Erro inesperado: {e}"


# ====================================================================
# FUNÇÕES DE INTERAÇÃO COM O SISTEMA
# ====================================================================

def get_temp_paths() -> Dict[str, str]:
    """Retorna um dicionário de caminhos temporários a serem limpos."""
    user_temp = os.environ.get('TEMP')
    local_app_data = os.environ.get('LOCALAPPDATA')
    system_drive = os.environ.get('SystemDrive', 'C:')

    paths = {}
    if user_temp:
        paths['Temp Usuário'] = user_temp
    if local_app_data:
        paths['Temp/Cache Local'] = os.path.join(local_app_data, 'Temp')
        paths['Cache Edge'] = os.path.join(local_app_data, 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache')
        paths['Cache Chrome'] = os.path.join(local_app_data, 'Google', 'Chrome', 'User Data', 'Default', 'Cache')

    if system_drive:
        paths['Temp Sistema'] = os.path.join(system_drive, 'Windows', 'Temp')
        paths['Prefetch'] = os.path.join(system_drive, 'Windows', 'Prefetch')

    return paths

def set_power_plan(plan_key: str) -> Tuple[bool, str]:
    """Define o plano de energia do Windows."""
    
    plan_upper = plan_key.upper()
    guid = POWER_PLAN_GUIDS.get(plan_upper)
    
    if not guid:
        logger.warning(f"Plano de energia '{plan_key}' desconhecido.")
        return False, f"Plano de energia '{plan_key}' desconhecido."
    
    # 1. Tentar ativar o plano
    command = ["powercfg", "/setactive", guid]
    success, output = execute_windows_command(command)
    
    # 2. SE FALHAR E FOR O 'DESEMPENHO MÁXIMO', TENTAR CRIÁ-LO (Lógica robusta)
    if not success and plan_upper == "MAXIMUM_PERFORMANCE":
        logger.warning("Falha ao ativar Desempenho Máximo. Tentando criá-lo primeiro...")
        
        # Comando para duplicar o plano HIGH_PERFORMANCE (8c5...) para o MAXIMUM_PERFORMANCE (e9a...)
        creation_command = ["powercfg", "/duplicate scheme", 
                            POWER_PLAN_GUIDS["HIGH_PERFORMANCE"], 
                            POWER_PLAN_GUIDS["MAXIMUM_PERFORMANCE"]]
        
        create_success, create_output = execute_windows_command(creation_command)
        
        if create_success:
            logger.info("Plano 'Desempenho Máximo' criado com sucesso. Tentando ativar novamente.")
            success, output = execute_windows_command(command)
            
            if success:
                logger.info(f"Plano de energia definido para {plan_key.replace('_', ' ').title()}.")
                return True, f"Plano de energia definido para {plan_key.replace('_', ' ').title()}."
        else:
            logger.error(f"Falha na criação do plano Desempenho Máximo. Output: {create_output}")
            return False, f"Falha na criação e ativação do plano de energia: {create_output}"

    # 3. RETORNO FINAL
    if success:
        logger.info(f"Plano de energia definido para {plan_key.replace('_', ' ').title()}.")
        return True, f"Plano de energia definido para {plan_key.replace('_', ' ').title()}."
    else:
        logger.error(f"Falha ao definir plano de energia: {output}")
        return False, f"Falha ao definir plano de energia: {output}"

def optimize_disk(drive_letter: str = "C") -> Tuple[bool, str]:
    """
    Executa a otimização (desfragmentação/TRIM) no disco especificado.
    Requer privilégios de Administrador.
    """
    if not drive_letter or not drive_letter.isalpha() or len(drive_letter) != 1:
        return False, "Letra da unidade inválida."

    drive_letter = drive_letter.upper()
    
    # Comando nativo do Windows: /O = Otimizar (Aplica TRIM em SSDs, desfragmenta HDDs)
    command = ["defrag", f"{drive_letter}:", "/O", "/V"] 
    
    logger.info(f"Iniciando otimização do disco {drive_letter}: com 'defrag /O'...")
    
    success, output = execute_windows_command(command)
    
    if success:
        if "completed" in output.lower() or "concluída" in output.lower() or "êxito" in output.lower():
            msg = f"Otimização do disco {drive_letter}: concluída com sucesso."
            logger.info(msg)
            return True, msg
        else:
            msg = f"Otimização do disco {drive_letter}: finalizada, mas verifique o log para detalhes. {output.strip().splitlines()[-1]}"
            logger.warning(msg)
            return True, msg
    else:
        msg = f"Falha na otimização do disco {drive_letter}:. Erro: {output}"
        logger.error(msg)
        return False, msg
    
def terminate_processes(processes: List[str]) -> Tuple[bool, List[str]]:
    """Tenta encerrar uma lista de processos usando o taskkill."""
    terminated_list = []
    
    logger.info(f"Tentando encerrar {len(processes)} processos para otimização.")
    overall_success = True 
    
    for process_name in processes:
        command = ["taskkill", "/F", "/IM", process_name]
        success, output = execute_windows_command(command)
        
        if success:
            if "AVISO:" in output:
                logger.debug(f" - Processo '{process_name}' não estava rodando.")
            else:
                terminated_list.append(process_name)
                logger.info(f" - ENCERRADO: {process_name}")
                
        else:
            logger.warning(f" - FALHA crítica ao encerrar '{process_name}'. Output: {output.strip()}")

    return overall_success, terminated_list

# ====================================================================
# FUNÇÕES DE LIMPEZA E CÁLCULO DE TAMANHO (CORREÇÃO DE ERRO ANTERIOR)
# ====================================================================

def get_dir_size(start_path: str) -> int:
    """Calcula o tamanho total de todos os arquivos em um diretório, em bytes."""
    total_size = 0
    if not os.path.exists(start_path):
        return 0
    try:
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    try:
                        total_size += os.path.getsize(fp)
                    except OSError:
                        logger.debug(f"Permissão negada ou erro ao obter tamanho de: {fp}")
    except Exception as e:
        logger.debug(f"Erro ao calcular tamanho em {start_path}: {e}")
    return total_size

def clean_directory(path: str) -> int:
    """Remove todo o conteúdo de um diretório e retorna o tamanho liberado."""
    if not os.path.exists(path):
        return 0
        
    cleaned_size = get_dir_size(path)
        
    # 2. Tenta remover TUDO
    try:
        # Percorre o conteúdo do diretório de destino
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            try:
                if os.path.isdir(item_path):
                    # Remove pastas recursivamente (ignora erros de permissão/arquivo em uso)
                    shutil.rmtree(item_path, ignore_errors=True)
                else:
                    # Remove arquivos (ignora erros de permissão/arquivo em uso)
                    os.remove(item_path)
            except Exception as sub_e:
                # Loga o arquivo/pasta específico que não pôde ser removido
                logger.debug(f" - Falha ao remover '{item_path}': {sub_e}")
        
    except Exception as e:
        logger.warning(f"Falha na limpeza de {path} (erro principal): {e}. Itens que estavam em uso podem ter permanecido.")
        
    # 3. Garante que o diretório base existe (importante para o TEMP, etc.)
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        logger.error(f"Não foi possível recriar o diretório temporário {path}: {e}")
        
    return cleaned_size