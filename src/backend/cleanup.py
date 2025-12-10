import os
import shutil
import logging
from typing import Tuple, List

# Importação revisada para incluir as novas funções de otimização
from src.utils.system import get_temp_paths, set_power_plan, execute_windows_command, format_bytes, terminate_processes, OPT_PROCESSES_TO_KILL

# Configura o logger para ser usado neste módulo
logger = logging.getLogger('BlazeScan') 

def get_dir_size(path: str) -> int:
    # ... (função get_dir_size permanece a mesma) ...
    total_size = 0
    if not os.path.isdir(path):
        return 0
    
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                try:
                    total_size += os.path.getsize(fp)
                except OSError as e:
                    logger.warning(f"Não foi possível obter o tamanho do arquivo '{fp}'. Ignorando. Erro: {e}")
                    pass
    return total_size

def clean_directory(path: str) -> int:
    # ... (função clean_directory permanece a mesma com a proteção de segurança) ...
    total_size_cleaned = 0
    if not os.path.isdir(path):
        logger.info(f"Diretório não encontrado ou inválido: {path}")
        return 0

    # ====================================================================
    # 🚨 VERIFICAÇÃO DE SEGURANÇA CRÍTICA 🚨
    absolute_path = os.path.abspath(path)
    
    critical_roots = [
        os.path.abspath(os.environ.get('SystemRoot', 'C:\\Windows')),
        os.path.abspath(os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32')),
        os.path.abspath("C:\\"),
        os.path.abspath(os.environ.get('ProgramFiles', 'C:\\Program Files')),
        os.path.abspath(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')),
    ]

    if absolute_path in critical_roots:
        logger.critical(f"TENTATIVA DE ACESSO CRÍTICO: O caminho '{path}' é uma pasta vital do Windows. Limpeza Abortada.")
        return 0
    # ====================================================================
    
    logger.info(f"Iniciando limpeza no diretório: {path}")

    items_to_delete = [os.path.join(path, item) for item in os.listdir(path)]

    for item_path in items_to_delete:
        try:
            size_to_delete = 0
            
            if os.path.isfile(item_path) or os.path.islink(item_path):
                try:
                    size_to_delete = os.path.getsize(item_path)
                    os.remove(item_path)
                    logger.info(f" - REMOVIDO Arquivo: {os.path.basename(item_path)}")
                except OSError:
                    pass
                
            elif os.path.isdir(item_path):
                try:
                    size_to_delete = get_dir_size(item_path)
                    shutil.rmtree(item_path)
                    logger.info(f" - REMOVIDO Diretório: {os.path.basename(item_path)} e conteúdo.")
                except OSError:
                    pass

            total_size_cleaned += size_to_delete

        except Exception as e:
            logger.warning(f" - FALHOU ao remover '{os.path.basename(item_path)}'. Motivo: {e}")
            pass
            
    logger.info(f"Limpeza de '{path}' finalizada. Total liberado: {format_bytes(total_size_cleaned)}")
    return total_size_cleaned

def perform_cleanup() -> Tuple[bool, str, str]:
    """
    Executa a limpeza de arquivos temporários, encerra processos e otimiza o plano de energia.
    Retorna (sucesso_geral, mensagem_log, tamanho_limpo_formatado).
    """
    total_cleaned_bytes = 0
    messages: List[str] = []
    
    logger.info("=" * 40)
    logger.info("INICIANDO OPERAÇÃO BLAZESCAN")
    logger.info("=" * 40)

    # --- 1. Limpeza de Arquivos Temporários ---
    logger.info("--- 1. Limpeza de Arquivos Temporários ---")
    messages.append("--- 1. Limpeza de Arquivos Temporários ---")
    
    temp_paths = get_temp_paths() 
    
    for path in temp_paths:
        cleaned_size = clean_directory(path) 
        total_cleaned_bytes += cleaned_size
        
        messages.append(f"Limpeza em '{os.path.basename(path)}' concluída. Liberado: {format_bytes(cleaned_size)}")

    # ====================================================================
    # 🆕 NOVO: 2. Encerramento de Processos de Otimização
    # ====================================================================
    logger.info("\n--- 2. Encerramento de Processos de Otimização ---")
    messages.append("\n--- 2. Encerramento de Processos de Otimização ---")
    
    success_kill, terminated_list = terminate_processes(OPT_PROCESSES_TO_KILL)

    if terminated_list:
        messages.append(f"Processos encerrados com sucesso: {', '.join(terminated_list)}")
    else:
        messages.append("Nenhum processo de otimização encontrado ou encerrado.")
        
    # --- 3. Otimização de Energia (Antigo 2) ---
    logger.info("\n--- 3. Otimização de Energia ---")
    messages.append("\n--- 3. Otimização de Energia ---")
    
    success_power, msg_power = set_power_plan("MAXIMUM_PERFORMANCE")
    
    if not success_power:
        logger.warning("Falha ao definir Desempenho Máximo. Tentando Alto Desempenho...")
        success_power, msg_power = set_power_plan("HIGH_PERFORMANCE")
        
    messages.append(f"Resultado: {msg_power}")

    # --- 4. Otimizações Adicionais (Antigo 3) ---
    logger.info("\n--- 4. Otimizações Adicionais (Ação Manual Recomendada) ---")
    messages.append("\n--- 4. Otimizações Adicionais (Requer Ação Manual/Admin) ---")
    
    msg_msconfig = "Para otimizar o uso de núcleos/memória (msconfig), use o utilitário 'msconfig' (aba Inicialização do Sistema -> Opções Avançadas)."
    msg_defrag = "Para otimizar o disco (SSD/HDD), execute o comando 'defrag C: /O' como Administrador."
    
    logger.info(msg_msconfig)
    logger.info(msg_defrag)
    messages.append(msg_msconfig)
    messages.append(msg_defrag)
    
    # --- Conclusão ---
    formatted_size = format_bytes(total_cleaned_bytes)
    
    logger.info("=" * 40)
    logger.info(f"OPERAÇÃO CONCLUÍDA. Total Liberado: {formatted_size}")
    logger.info("=" * 40)
    
    final_message = "\n".join(messages)
    
    return True, final_message, formatted_size

if __name__ == '__main__':
    pass