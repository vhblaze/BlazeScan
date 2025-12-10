import os
import subprocess
import logging # <-- Novo: Importa a biblioteca de log
from typing import List, Tuple

# Configura o logger para ser usado neste módulo
logger = logging.getLogger(__name__)

def get_temp_paths() -> List[str]:
    """
    Retorna uma lista de caminhos comuns de diretórios temporários no Windows.
    """
    paths = []
    
    # %TEMP% - Variável de ambiente do usuário
    user_temp = os.environ.get('TEMP')
    if user_temp and os.path.isdir(user_temp):
        paths.append(user_temp)
        
    # C:\Windows\Temp - Diretório temporário do sistema
    system_temp = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp')
    if os.path.isdir(system_temp):
        paths.append(system_temp)
        
    # Limpar caminhos duplicados e garantir que existam
    final_paths = list(set(p for p in paths if os.path.exists(p)))
    logger.debug(f"Caminhos temporários encontrados: {final_paths}") # Log para debug
    return final_paths

def execute_windows_command(command: List[str]) -> Tuple[bool, str]:
    """
    Executa um comando do Windows e retorna o status e a saída.
    """
    command_str = " ".join(command) # Converte a lista para string para log
    logger.debug(f"Executando comando: {command_str}")
    
    try:
        # Usar shell=True pode ser perigoso, mas é necessário para alguns comandos do Windows.
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            shell=True
        )
        # Sucesso: Loga a execução, mas não mostra o output inteiro
        logger.info(f"Comando executado com sucesso: {command[0]}")
        return True, result.stdout.strip()
    
    except subprocess.CalledProcessError as e:
        # Falha: Loga o erro de execução do comando
        logger.error(f"Erro ao executar '{command_str}': {e.stderr.strip()}")
        return False, f"Erro ao executar comando: {e.stderr.strip()}"
        
    except FileNotFoundError:
        # Falha: Comando não existe no PATH
        logger.error(f"Comando não encontrado: {command[0]}")
        return False, "Comando não encontrado."
        
    except Exception as e:
        # Falha: Loga outros erros inesperados
        logger.error(f"Erro inesperado ao executar '{command_str}': {e}")
        return False, f"Erro inesperado: {e}"

# Constantes para planos de energia do Windows (GUIDs)
# GUIDs comuns para Windows 10/11
POWER_PLAN_GUIDS = {
    "MAXIMUM_PERFORMANCE": "e9a42b02-d5df-448d-aa00-03f147498387", # Desempenho Máximo
    "HIGH_PERFORMANCE": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c", # Alto Desempenho
    "BALANCED": "381b4222-f694-41f0-9685-ce5920ae7518", # Equilibrado
    "POWER_SAVER": "a1841308-3541-4fab-bc81-f71556f20b4a" # Economia de Energia
}

def set_power_plan(plan_key: str) -> Tuple[bool, str]:
    """
    Define o plano de energia do Windows.
    plan_key deve ser uma chave de POWER_PLAN_GUIDS.
    """
    guid = POWER_PLAN_GUIDS.get(plan_key.upper())
    
    if not guid:
        logger.warning(f"Plano de energia '{plan_key}' desconhecido. Verifique as chaves em POWER_PLAN_GUIDS.")
        return False, f"Plano de energia '{plan_key}' desconhecido."

    # Comando: powercfg /setactive <GUID>
    command = ["powercfg", "/setactive", guid]
    
    success, output = execute_windows_command(command) # execute_windows_command já faz o logging

    if success:
        logger.info(f"Plano de energia definido para {plan_key.replace('_', ' ').title()}.") # <-- Log de Sucesso
        return True, f"Plano de energia definido para {plan_key.replace('_', ' ').title()}."
    else:
        # Se falhar, o log de erro já foi gerado por execute_windows_command
        return False, f"Falha ao definir plano de energia: {output}"

def format_bytes(size_in_bytes: int) -> str:
    """
    Formata um número de bytes para uma string legível (KB, MB, GB, etc.).
    """
    if size_in_bytes == 0:
        return "0 Bytes"
    
    # A fórmula para cálculo do tamanho está correta
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    size = float(size_in_bytes)
    
    while size >= 1024.0 and i < len(units) - 1:
        size /= 1024.0
        i += 1
        
    return f"{size:.2f} {units[i]}"

if __name__ == '__main__':
    # Configuração de teste de log para rodar o arquivo individualmente
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    print("--- Teste de get_temp_paths ---")
    print(get_temp_paths())
    
    print("\n--- Teste de set_power_plan ---")
    # Este teste só funcionará corretamente se for rodado como Administrador.
    set_power_plan("BALANCED") 
    
    print("\n--- Teste de format_bytes ---")
    print("Bytes formatados:", format_bytes(1024 * 1024 * 500)) # 500 MB
    print("Bytes formatados:", format_bytes(2 * 1024**4)) # 2 TB