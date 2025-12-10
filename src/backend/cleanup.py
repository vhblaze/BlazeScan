import os
import shutil
import logging # <-- Novo: Importa a biblioteca de log
from typing import Tuple, List

# A importação absoluta abaixo está CORRETA para a sua estrutura (src.utils.system)
from src.utils.system import get_temp_paths, set_power_plan, execute_windows_command, format_bytes

# Configura o logger para ser usado neste módulo (o handler já está configurado no main.py)
logger = logging.getLogger(__name__)

def get_dir_size(path: str) -> int:
    """
    Calcula o tamanho total de um diretório em bytes.
    """
    total_size = 0
    if not os.path.isdir(path):
        return 0
    
    # logger.debug(f"Calculando tamanho de: {path}") # Exemplo de log para debug
    
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # Evita links simbólicos que podem causar loops ou erros de permissão
            if not os.path.islink(fp):
                try:
                    total_size += os.path.getsize(fp)
                except OSError as e:
                    # Loga o erro de permissão, mas continua
                    logger.warning(f"Não foi possível obter o tamanho do arquivo '{fp}'. Ignorando. Erro: {e}")
                    pass
    return total_size

def clean_directory(path: str) -> int:
    """
    Limpa o conteúdo de um diretório, retornando o tamanho total limpo em bytes.
    """
    total_size_cleaned = 0
    if not os.path.isdir(path):
        logger.info(f"Diretório não encontrado ou inválido: {path}")
        return 0

    logger.info(f"Iniciando limpeza no diretório: {path}") # <-- Log de Início

    # Lista de itens a serem excluídos
    # Usa list() para evitar problemas se o diretório for modificado durante o loop
    items_to_delete = [os.path.join(path, item) for item in os.listdir(path)]

    for item_path in items_to_delete:
        try:
            # Tenta obter o tamanho antes de deletar (para cálculo de bytes limpos)
            size_to_delete = 0
            
            if os.path.isfile(item_path) or os.path.islink(item_path):
                try:
                    size_to_delete = os.path.getsize(item_path)
                    os.remove(item_path)
                    logger.info(f" - REMOVIDO Arquivo: {os.path.basename(item_path)}") # <-- Log de remoção de arquivo
                except OSError:
                    pass # Se não conseguir o tamanho, ignora
                
            elif os.path.isdir(item_path):
                # Calcula o tamanho do diretório (inclui subpastas) antes de deletar
                size_to_delete = get_dir_size(item_path)
                shutil.rmtree(item_path)
                logger.info(f" - REMOVIDO Diretório: {os.path.basename(item_path)} e conteúdo.") # <-- Log de remoção de diretório

            total_size_cleaned += size_to_delete

        except Exception as e:
            # Ignora arquivos/pastas que não podem ser deletados (em uso, permissão negada, etc.)
            logger.warning(f" - FALHOU ao remover '{os.path.basename(item_path)}'. Motivo: {e}") # <-- Log de Falha
            pass
            
    logger.info(f"Limpeza de '{path}' finalizada. Total liberado: {format_bytes(total_size_cleaned)}")
    return total_size_cleaned

def perform_cleanup() -> Tuple[bool, str, str]:
    """
    Executa a limpeza de arquivos temporários e cache, e otimiza o plano de energia.
    Retorna (sucesso_geral, mensagem_log, tamanho_limpo_formatado).
    """
    total_cleaned_bytes = 0
    messages: List[str] = [] # Mantenho 'messages' para construir o log final da UI, mas uso logging para o console.
    
    logger.info("=" * 40)
    logger.info("INICIANDO OPERAÇÃO BLAZESCAN")
    logger.info("=" * 40)

    # 1. Limpeza de Arquivos Temporários
    logger.info("--- 1. Limpeza de Arquivos Temporários ---")
    temp_paths = get_temp_paths()
    for path in temp_paths:
        cleaned_size = clean_directory(path)
        total_cleaned_bytes += cleaned_size
        
        # Mantém a mensagem para o log de retorno (se for exibido na UI)
        messages.append(f"Limpeza em '{path}' concluída. Liberado: {format_bytes(cleaned_size)}")

    # 2. Otimização de Energia
    logger.info("\n--- 2. Otimização de Energia ---")
    messages.append("\n--- Otimização de Energia ---")
    
    # A função set_power_plan já deve logar seu sucesso/falha internamente
    success_power, msg_power = set_power_plan("MAXIMUM_PERFORMANCE")
    if not success_power:
        logger.warning("Falha ao definir Desempenho Máximo. Tentando Alto Desempenho...")
        success_power, msg_power = set_power_plan("HIGH_PERFORMANCE")
    
    messages.append(f"Resultado: {msg_power}")

    # 3. Otimização de MSConfig e Desfragmentação (Apenas comandos informativos)
    logger.info("\n--- 3. Otimizações Adicionais (Ação Manual Recomendada) ---")
    messages.append("\n--- Otimizações Adicionais (Requer Ação Manual/Admin) ---")
    
    msg_msconfig = "Para otimizar o uso de núcleos/memória (msconfig), use o utilitário 'msconfig' (aba Inicialização do Sistema -> Opções Avançadas)."
    msg_defrag = "Para otimizar o disco (SSD/HDD), execute o comando 'defrag C: /O' como Administrador."
    
    logger.info(msg_msconfig)
    logger.info(msg_defrag)
    messages.append(msg_msconfig)
    messages.append(msg_defrag)
    
    logger.info("=" * 40)
    logger.info(f"OPERAÇÃO CONCLUÍDA. Total Liberado: {format_bytes(total_cleaned_bytes)}")
    logger.info("=" * 40)
    
    final_message = "\n".join(messages)
    formatted_size = format_bytes(total_cleaned_bytes)
    
    return True, final_message, formatted_size

if __name__ == '__main__':
    # Teste (simulado, pois não estamos em um ambiente Windows real)
    pass