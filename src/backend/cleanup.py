import os
import logging
import sys
from typing import Tuple, List, Dict, Any

# Importa as funções e constantes dos utilitários
from src.utils.system import (
    get_temp_paths, 
    set_power_plan, 
    optimize_disk, 
    terminate_processes, 
    format_bytes,
    
    # 🚨 CORREÇÃO: clean_directory precisa ser importado do system.py 🚨
    clean_directory, 
    
    OPT_PROCESSES_TO_KILL
)

logger = logging.getLogger('BlazeScan')


# ====================================================================
# FUNÇÕES DE EXECUÇÃO ESPECÍFICA (Responsabilidade Única)
# ====================================================================

def cleanup_temp_files(messages: List[str]) -> int:
    """Executa a limpeza de arquivos temporários."""
    total_cleaned_bytes = 0
    logger.info("--- 1. Limpeza de Arquivos Temporários ---")
    messages.append("--- 1. Limpeza de Arquivos Temporários ---")
    
    # Assumindo que get_temp_paths retorna Dict[str, str] (Nome: Caminho)
    temp_paths_map = get_temp_paths() 
    
    for name, path in temp_paths_map.items():
        if os.path.exists(path):
            # clean_directory AGORA ESTÁ IMPORTADO
            try:
                cleaned_size = clean_directory(path) 
                total_cleaned_bytes += cleaned_size
                messages.append(f"Limpeza em '{name}' concluída. Liberado: {format_bytes(cleaned_size)}")
            except Exception as e:
                 # Adiciona um tratamento de erro mais robusto caso a limpeza falhe
                 logger.error(f"Falha crítica ao limpar '{name}' ({path}): {e}")
                 messages.append(f"Limpeza em '{name}' falhou. Erro: {e}")

        else:
            logger.debug(f"Caminho não encontrado para limpeza: {name}")

    return total_cleaned_bytes


def cleanup_terminate_processes(messages: List[str]):
    """Encerra processos específicos para otimização."""
    logger.info("\n--- 2. Encerramento de Processos de Otimização ---")
    messages.append("\n--- 2. Encerramento de Processos de Otimização ---")
    
    success_kill, terminated_list = terminate_processes(OPT_PROCESSES_TO_KILL)

    if terminated_list:
        messages.append(f"Processos encerrados com sucesso: {', '.join(terminated_list)}")
    else:
        messages.append("Nenhum processo de otimização encontrado ou encerrado.")


def cleanup_power_plan(messages: List[str], settings: Dict[str, Any]):
    """Define o plano de energia com base nas configurações da UI."""
    logger.info("\n--- 3. Otimização de Energia ---")
    messages.append("\n--- 3. Otimização de Energia ---")
    
    # Obtém a chave do plano de energia das configurações (ex: "MAXIMUM_PERFORMANCE")
    plan_key = settings.get("energy_plan", "NONE") 
    
    if plan_key != "NONE":
        success_power, msg_power = set_power_plan(plan_key)
        
        # Lógica de fallback se MAXIMUM_PERFORMANCE falhar (opcional, mas robusta)
        if not success_power and plan_key == "MAXIMUM_PERFORMANCE":
            logger.warning("Falha no Desempenho Máximo. Tentando Alto Desempenho como fallback...")
            success_power, msg_power = set_power_plan("HIGH_PERFORMANCE")
        
        messages.append(f"Resultado: {msg_power}")
    else:
        messages.append("Plano de energia não alterado por opção do utilizador.")


def cleanup_disk_optimization(messages: List[str], settings: Dict[str, Any]):
    """Executa a otimização de disco (defrag/TRIM) se configurado."""
    logger.info("\n--- 4. Otimização de Disco (SSD/HDD) ---")
    messages.append("\n--- 4. Otimização de Disco ---")

    if settings.get("optimize_disk", False):
        if not sys.platform.startswith('win'):
            messages.append("Otimização de disco ignorada: Apenas suportado no Windows.")
        else:
            # Chama a função de otimização para a unidade C:
            success_disk, msg_disk = optimize_disk("C") 
            messages.append(f"Resultado: {msg_disk}")
    else:
        messages.append("Otimização de disco C:\\ ignorada por opção do utilizador.")


def cleanup_additional_info(messages: List[str]):
    """Adiciona informações sobre otimizações manuais."""
    logger.info("\n--- 5. Otimizações Adicionais (Ação Manual Recomendada) ---")
    messages.append("\n--- 5. Otimizações Adicionais (Requer Ação Manual/Admin) ---")
    
    msg_msconfig = "Para otimizar o uso de núcleos/memória (msconfig), use o utilitário 'msconfig' (aba Inicialização do Sistema -> Opções Avançadas)."
    
    logger.info(msg_msconfig)
    messages.append(msg_msconfig)


# ====================================================================
# FUNÇÃO ORQUESTRADORA PRINCIPAL
# ====================================================================

def perform_cleanup(settings: Dict[str, Any]) -> Tuple[bool, str, str]:
    """
    Orquestra todas as etapas de limpeza e otimização.
    """
    total_cleaned_bytes = 0
    messages: List[str] = []
    
    logger.info("=" * 40)
    logger.info("INICIANDO OPERAÇÃO BLAZESCAN")
    logger.info(f"Configurações recebidas: {settings}")
    logger.info("=" * 40)

    # 1. Limpeza de Arquivos
    total_cleaned_bytes += cleanup_temp_files(messages)

    # 2. Encerramento de Processos
    cleanup_terminate_processes(messages)
    
    # 3. Otimização de Energia
    cleanup_power_plan(messages, settings)
    
    # 4. Otimização de Disco
    cleanup_disk_optimization(messages, settings)
    
    # 5. Informações Adicionais
    cleanup_additional_info(messages)

    # --- Conclusão ---
    formatted_size = format_bytes(total_cleaned_bytes)
    
    logger.info("=" * 40)
    logger.info(f"OPERAÇÃO CONCLUÍDA. Total Liberado: {formatted_size}")
    logger.info("=" * 40)
    
    final_message = "\n".join(messages)
    
    # Define o sucesso geral como True, mesmo que processos ou disco falhem (a limpeza de arquivos é o foco)
    return True, final_message, formatted_size