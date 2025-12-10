#!/usr/bin/env python3
"""
BlazeScan - Ponto de entrada principal
"""

import sys
import os
import logging
import ctypes  # Módulo nativo para interagir com o sistema operacional
from typing import NoReturn

# --- CONFIGURAÇÃO INICIAL E LOGGING ---

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Adiciona o diretório raiz do projeto ao sys.path para importações absolutas (necessário para a estrutura do pacote)
try:
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
except Exception as e:
    logging.error(f"Não foi possível configurar o caminho de importação: {e}")
    sys.exit(1)

# Importa a UI após configurar o path
try:
    # Lembre-se: Mantenha a importação absoluta, ex: from src.frontend.ui import start_ui
    from src.frontend.ui import start_ui
except ImportError as e:
    logging.error(f"Falha ao carregar a interface (UI). Erro: {e}")
    logging.info("Verifique se as dependências (ex: customtkinter) estão instaladas e se as importações são absolutas (ex: from src...).")
    sys.exit(1)


# --- FUNÇÕES DE ADMINISTRAÇÃO ---

def is_admin() -> bool:
    """Verifica se o script está rodando com privilégios de administrador."""
    try:
        # Retorna True se o token de acesso indicar que o usuário é administrador
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        # Em caso de erro (ex: sistema não Windows), assume que não é admin
        return False

def elevate_privileges():
    """
    Tenta reiniciar o script com permissões de administrador.
    Exibe o prompt UAC do Windows.
    """
    if not is_admin():
        script = os.path.abspath(sys.argv[0])
        # Usa ShellExecuteW com o verbo "runas" para solicitar elevação de privilégio
        # Isso fará o Windows exibir a caixa "Deseja permitir que este app..."
        ret = ctypes.windll.shell32.ShellExecuteW(
            None,      # hWnd (handle da janela)
            "runas",   # Verbo: solicitar execução como administrador
            sys.executable,  # Caminho para o executável Python
            script,    # Argumento: o próprio script principal
            None,      # Diretório de trabalho
            1          # SW_SHOWNORMAL (mostra a janela normalmente)
        )
        
        # O valor ret 42 indica que a operação foi bem-sucedida, mas o programa atual está sendo fechado.
        # Sai do programa atual, pois ele será reaberto com privilégios elevados.
        if ret > 32:
             sys.exit(0)
        else:
            # Caso a elevação falhe (e.g., usuário cancela no UAC ou erro)
            logging.error("Falha ao solicitar permissões de administrador. O programa pode não funcionar corretamente.")
            # Continuamos para permitir que o usuário veja a UI, mas com funcionalidade limitada.


# --- FUNÇÕES DE EXECUÇÃO PRINCIPAL ---

def check_os() -> bool:
    """Verifica se o sistema operacional é Windows."""
    if sys.platform != 'win32':
        logging.warning("AVISO: Este programa foi projetado para Windows.")
        response = input("Deseja continuar mesmo assim? (s/n): ")
        return response.lower() == 's'
    return True


def main() -> NoReturn:
    """Função principal que inicia a aplicação BlazeScan."""

    # 1. VERIFICA E ELEVA PRIVILÉGIOS (NOVA ETAPA)
    elevate_privileges() 
    # Se a elevação for bem-sucedida, o código daqui para baixo só será executado na nova instância Admin.

    # 2. VERIFICA SISTEMA OPERACIONAL
    if not check_os():
        logging.info("Encerrando a aplicação.")
        sys.exit(0)
    
    # Inicia a interface gráfica
    logging.info("Iniciando BlazeScan...")
    if is_admin():
        logging.info("Executando com privilégios de Administrador.")
    else:
        logging.warning("Executando sem privilégios de Administrador. Algumas funções podem falhar.")
        
    try:
        start_ui()
    except KeyboardInterrupt:
        logging.info("\nAplicação encerrada pelo usuário (Ctrl+C).")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Erro fatal durante a execução da aplicação: {e}")
        sys.exit(1)
        
    sys.exit(0)

if __name__ == '__main__':
    main()