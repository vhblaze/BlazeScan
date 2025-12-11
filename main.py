#!/usr/bin/env python3
"""
BlazeScan - Ponto de entrada principal
"""

import sys
import os
import logging
import ctypes 
import customtkinter as ctk # Adicionado, pois main.py deve configurar o CTK
from typing import NoReturn

# --- CONFIGURAÇÃO INICIAL E LOGGING ---

# Configuração do Logging para console
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger('BlazeScan')
logger.setLevel(logging.INFO)

# Adiciona o diretório raiz do projeto ao sys.path
try:
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
except Exception as e:
    logger.error(f"Não foi possível configurar o caminho de importação: {e}")
    sys.exit(1)

# Importa a classe App
try:
    # 🚨 CORREÇÃO: Importar a classe App, não a função start_ui
    from src.frontend.ui import App 
except ImportError as e:
    logger.error(f"Falha ao carregar a interface (UI). Erro: {e}")
    logger.info("Verifique se as dependências (ex: customtkinter) estão instaladas e se as importações são absolutas (ex: from src...).")
    sys.exit(1)


# --- FUNÇÕES DE ADMINISTRAÇÃO ---

def is_admin() -> bool:
    """Verifica se o script está rodando com privilégios de administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def elevate_privileges():
    """Tenta reiniciar o script com permissões de administrador."""
    if not is_admin() and sys.platform == 'win32':
        script = os.path.abspath(sys.argv[0])
        ret = ctypes.windll.shell32.ShellExecuteW(
            None,      
            "runas",   
            sys.executable,
            f'"{script}"', # Passa o caminho do script entre aspas
            None,      
            1          
        )
        
        # Se a operação for bem-sucedida, o programa atual é fechado
        if ret > 32:
            sys.exit(0)
        else:
            logger.error("Falha ao solicitar permissões de administrador. O programa pode não funcionar corretamente.")


# --- FUNÇÃO DE EXECUÇÃO PRINCIPAL ---

def main() -> NoReturn:
    """Função principal que inicia a aplicação BlazeScan."""

    # 1. VERIFICA E ELEVA PRIVILÉGIOS 
    elevate_privileges() 

    # 2. VERIFICA SISTEMA OPERACIONAL (Simplificado)
    if sys.platform != 'win32':
        logger.warning("AVISO: Este programa foi projetado para Windows e pode não funcionar corretamente aqui.")
    
    # Inicia a interface gráfica
    logger.info("Iniciando BlazeScan...")
    if is_admin():
        logger.info("Executando com privilégios de Administrador.")
    else:
        logger.warning("Executando sem privilégios de Administrador. Algumas funções (como Otimização de Disco) podem falhar.")
        
    try:
        # Configurações globais do CTk (devem estar fora da classe App)
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # 🚨 CORREÇÃO: Cria e executa a instância da classe App
        app = App()
        app.mainloop()
        
    except KeyboardInterrupt:
        logger.info("\nAplicação encerrada pelo usuário (Ctrl+C).")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Erro fatal durante a execução da aplicação: {e}")
        sys.exit(1)
        
    sys.exit(0)

if __name__ == '__main__':
    main()