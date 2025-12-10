import os
import subprocess
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger('BlazeScan') # Usando o logger principal

# ====================================================================
# 🆕 NOVO: Lista de processos a serem encerrados para otimização
# ====================================================================
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
    "copilot.exe"
]

def get_temp_paths() -> List[str]:
    """Retorna uma lista de caminhos comuns de diretórios temporários no Windows."""
    paths = []
    user_temp = os.environ.get('TEMP')
    if user_temp and os.path.isdir(user_temp):
        paths.append(user_temp)
    system_root = os.environ.get('SystemRoot', 'C:\\Windows')
    system_temp = os.path.join(system_root, 'Temp')
    if os.path.isdir(system_temp):
        paths.append(system_temp)
    return list(set(p for p in paths if os.path.exists(p)))

def execute_windows_command(command: List[str]) -> Tuple[bool, str]:
    """Executa um comando do Windows e retorna o status e a saída."""
    command_str = " ".join(command)
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=True # Necessário para comandos como powercfg e taskkill
        )
        # Verifica se o comando foi bem-sucedido ou se foi um erro esperado (e.g., processo não encontrado)
        if result.returncode == 0:
            logger.debug(f"Comando executado com sucesso: {command[0]}")
            return True, result.stdout.strip()
        else:
            # Taskkill pode retornar erro mesmo se for apenas "processo não encontrado"
            stderr_output = result.stderr.strip()
            if "not found" in stderr_output.lower() or "não encontrado" in stderr_output.lower():
                 logger.debug(f"Comando '{command[0]}' retornou erro (Processo não encontrado/esperado).")
                 return True, stderr_output # Consideramos como sucesso para Taskkill
            
            logger.error(f"Erro ao executar '{command_str}': {stderr_output}")
            return False, stderr_output
        
    except FileNotFoundError:
        logger.error(f"Comando não encontrado: {command[0]}")
        return False, "Comando não encontrado."
        
    except Exception as e:
        logger.error(f"Erro inesperado ao executar '{command_str}': {e}")
        return False, f"Erro inesperado: {e}"

POWER_PLAN_GUIDS = {
    "MAXIMUM_PERFORMANCE": "e9a42b02-d5df-448d-aa00-03f147498387",
    "HIGH_PERFORMANCE": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
    "BALANCED": "381b4222-f694-41f0-9685-ce5920ae7518",
    "POWER_SAVER": "a1841308-3541-4fab-bc81-f71556f20b4a"
}

def set_power_plan(plan_key: str) -> Tuple[bool, str]:
    """Define o plano de energia do Windows."""
    guid = POWER_PLAN_GUIDS.get(plan_key.upper())
    if not guid:
        logger.warning(f"Plano de energia '{plan_key}' desconhecido.")
        return False, f"Plano de energia '{plan_key}' desconhecido."
    command = ["powercfg", "/setactive", guid]
    success, output = execute_windows_command(command)
    if success:
        logger.info(f"Plano de energia definido para {plan_key.replace('_', ' ').title()}.")
        return True, f"Plano de energia definido para {plan_key.replace('_', ' ').title()}."
    else:
        return False, f"Falha ao definir plano de energia: {output}"

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

# ====================================================================
# 🆕 NOVA FUNÇÃO: Termina processos em segundo plano
# ====================================================================
def terminate_processes(processes: List[str]) -> Tuple[bool, List[str]]:
    """Tenta encerrar uma lista de processos usando o taskkill."""
    terminated_list = []
    
    logger.info(f"Tentando encerrar {len(processes)} processos para otimização.")
    
    for process_name in processes:
        # taskkill /F /IM <nome_do_processo>
        command = ["taskkill", "/F", "/IM", process_name]
        
        success, output = execute_windows_command(command)
        
        # taskkill retorna sucesso se for terminado ou se não for encontrado (assumindo que o erro não é fatal)
        if success and ("SUCESSO" in output.upper() or "SUCCESS" in output.upper() or "TERMINATED" in output.upper()):
            terminated_list.append(process_name)
        elif not success:
            logger.warning(f" - FALHA ao encerrar '{process_name}'. Verifique as permissões. Output: {output.strip()}")
        else:
            logger.debug(f" - Processo '{process_name}' não estava rodando (ou falha silenciosa).")
            
    return True, terminated_list # O retorno geral é True, pois o não-encerramento não é um erro fatal.