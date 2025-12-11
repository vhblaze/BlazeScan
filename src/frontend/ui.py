import os 
import customtkinter as ctk
import threading
from tkinter import messagebox
import sys
import logging
from typing import Dict, Any, Tuple

# --- IMPORTAÇÕES CORRIGIDAS (Mudança de Relativa para Absoluta) ---
try:
    from src.backend.cleanup import perform_cleanup
    from src.update.updater import is_update_available
except ImportError as e:
    logging.error(f"Erro de importação no UI: {e}")

# --- CONFIGURAÇÃO DO CAMINHO DO ÍCONE ---
ICON_FILENAME = "blazescan_logo.ico"
ICON_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ICON_FILENAME))

# --- CONFIGURAÇÃO DO LOGGER ---
# Configuração do logger principal para a UI
logger = logging.getLogger('BlazeScan')
logger.setLevel(logging.INFO) # Define o nível padrão para INFO

class LogHandler(logging.Handler):
    """Manipulador de log que redireciona mensagens para a Textbox da UI."""
    def __init__(self, textbox):
        super().__init__()
        self.textbox = textbox
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
    
    def emit(self, record):
        # A inserção na textbox deve ocorrer na thread principal da UI
        self.textbox.after(0, self.append_message, self.format(record))
    
    def append_message(self, msg):
        self.textbox.configure(state="normal") # Habilita para escrever
        self.textbox.insert(ctk.END, msg + "\n")
        self.textbox.see(ctk.END) # Scroll automático
        self.textbox.configure(state="disabled") # Desabilita novamente

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da janela principal
        self.title("BlazeScan - Otimizador de Sistema")
        self.geometry("600x750")
        
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # 🚨 CORREÇÃO 1: Inicialização das variáveis de controle 🚨
        self.energy_plan_var = ctk.StringVar(value="Balanceado")
        self.disk_optimize_var = ctk.BooleanVar(value=False)
        self.is_running = False # Variável para controlar o estado da limpeza
        
        # --- IMPLEMENTAÇÃO DO ÍCONE ---
        try:
            if sys.platform.startswith('win'):
                if os.path.exists(ICON_PATH):
                    self.iconbitmap(ICON_PATH)
                else:
                    logging.warning(f"Ícone não encontrado em {ICON_PATH}. Usando ícone padrão.")
        except Exception as e:
            logging.error(f"Falha ao carregar o ícone: {e}")
            
        # Configuração do grid (Ajustado para incluir a Row 0 para configurações)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Configurações (novo)
        self.grid_rowconfigure(1, weight=0) # Título
        self.grid_rowconfigure(2, weight=1) # Log (principal)
        self.grid_rowconfigure(3, weight=0) # Resultado
        self.grid_rowconfigure(4, weight=0) # Botão

        # 🚨 CORREÇÃO 2: Chamada para criar os widgets de configurações 🚨
        self.setup_settings_widgets()

        # 1. Título (agora na row 1)
        self.title_label = ctk.CTkLabel(self, text="Otimização de Sistema BlazeScan", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="n")

        # 2. Área de Log (agora na row 2)
        self.log_text = ctk.CTkTextbox(self, width=450, height=200)
        self.log_text.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.log_text.insert("0.0", "Bem-vindo ao BlazeScan!\nClique em 'Iniciar Limpeza e Otimização' para começar.")
        self.log_text.configure(state="disabled")
        
        # Configura o logger para a UI
        ui_handler = LogHandler(self.log_text)
        logger.addHandler(ui_handler)

        # 3. Label de Resultado (agora na row 3)
        self.result_label = ctk.CTkLabel(self, text="Tamanho Limpo: 0 Bytes", font=ctk.CTkFont(size=14))
        self.result_label.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="w")

        # 4. Botão de Ação (agora na row 4)
        self.cleanup_button = ctk.CTkButton(self, text="Iniciar Limpeza e Otimização", command=self.start_cleanup_thread)
        self.cleanup_button.grid(row=4, column=0, padx=20, pady=(10, 20), sticky="s")

        # 5. Verificar atualização ao iniciar
        self.after(100, self.check_for_update)
    
    # 🚨 CORREÇÃO 3: Método para criar os widgets de configuração (Row 0) 🚨
    def setup_settings_widgets(self):
        """Cria e posiciona o frame de configurações de otimização (Row 0)."""
        settings_frame = ctk.CTkFrame(self)
        settings_frame.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="ew") 
        settings_frame.grid_columnconfigure(1, weight=1)

        # Configuração de Energia
        ctk.CTkLabel(settings_frame, text="Plano de Energia:", anchor="w").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        energy_options = ["Desempenho Máximo", "Alto Desempenho", "Balanceado", "Não Alterar"]
        ctk.CTkOptionMenu(settings_frame, variable=self.energy_plan_var, values=energy_options).grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Configuração de Disco
        ctk.CTkCheckBox(settings_frame, text="Otimizar Disco C: (Defrag/TRIM)", variable=self.disk_optimize_var).grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
    def _get_settings(self) -> dict:
        """Retorna um dicionário com as configurações atuais da UI."""
        # Mapeia a seleção da UI para as chaves do backend (system.py)
        plan_mapping = {
            "Desempenho Máximo": "MAXIMUM_PERFORMANCE",
            "Alto Desempenho": "HIGH_PERFORMANCE",
            "Balanceado": "BALANCED",
            "Não Alterar": "NONE"
        }
        
        return {
            "energy_plan": plan_mapping.get(self.energy_plan_var.get(), "NONE"),
            "optimize_disk": self.disk_optimize_var.get()
        }
        
    def update_log(self, message: str):
        """Atualiza a área de log com uma nova mensagem (usado para mensagens não-logger)."""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", "\n" + message)
        self.log_text.see("end") # Rola para o final
        self.log_text.configure(state="disabled")

    def start_cleanup_thread(self):
        """Inicia a limpeza em uma thread separada para não travar a GUI."""
        if self.is_running:
            return
            
        # 1. OBTER CONFIGURAÇÕES
        try:
            settings = self._get_settings()
        except AttributeError:
            # Não deve mais ocorrer após as correções 1 e 2
            self.update_log("\nERRO CRÍTICO: Falha ao obter configurações da UI.")
            return

        self.is_running = True
        self.cleanup_button.configure(state="disabled", text="Limpando...")
        self.log_text.delete("0.0", ctk.END) # Limpa o log
        self.update_log("--- INICIANDO PROCESSO DE LIMPEZA E OTIMIZAÇÃO ---")
        
        # 2. CRIAÇÃO E INÍCIO DA THREAD (PASSANDO settings)
        cleanup_thread = threading.Thread(target=self.run_cleanup, args=(settings,))
        cleanup_thread.start()

    def run_cleanup(self, settings: Dict[str, Any]):
        """Função que executa a lógica de limpeza do backend."""
        try:
            # perform_cleanup é chamado com 'settings'
            success, log_message, formatted_size = perform_cleanup(settings)
            
            self.after(0, self.finish_cleanup, success, log_message, formatted_size)
            
        except Exception as e:
            logger.error(f"Erro inesperado no backend: {e}")
            self.after(0, self.finish_cleanup, False, f"Erro inesperado durante a limpeza: {e}", "0 Bytes")

    def finish_cleanup(self, success: bool, log_message: str, formatted_size: str):
        """Finaliza o processo de limpeza e atualiza a GUI."""
        self.update_log(log_message) # Adiciona o log sumarizado do backend
        self.result_label.configure(text=f"Tamanho Limpo: {formatted_size}")
        
        final_status = "CONCLUÍDO COM SUCESSO!" if success else "CONCLUÍDO COM ERROS."
        self.update_log(f"\n--- {final_status} ---")
        
        self.cleanup_button.configure(state="normal", text="Iniciar Limpeza e Otimização")
        self.is_running = False

    # --- Lógica de Atualização (Mantida) ---
    def check_for_update(self):
        """Verifica se há uma nova versão disponível e mostra um pop-up."""
        update_thread = threading.Thread(target=self._run_update_check)
        update_thread.start()

    def _run_update_check(self):
        """Lógica de verificação de atualização."""
        try:
            # Usando is_update_available do seu módulo
            available, local_version, latest_version = is_update_available()
            
            if available:
                self.after(0, self._show_update_popup, local_version, latest_version)
        except NameError:
            logger.warning("Módulo de atualização não carregado. Pulando verificação.")
        except Exception as e:
            logger.error(f"Erro na verificação de atualização: {e}")

    def _show_update_popup(self, local_version: str, latest_version: str):
        """Mostra o pop-up de atualização."""
        response = messagebox.askyesno(
            "Atualização Disponível",
            f"Uma nova versão ({latest_version}) está disponível!\nSua versão atual é: {local_version}.\n\nDeseja atualizar agora?"
        )
        
        if response:
            messagebox.showinfo("Atualização", "A lógica de atualização será iniciada. Por favor, aguarde.")
        else:
            messagebox.showinfo("Atualização", "A atualização foi cancelada. Você pode verificar novamente mais tarde.")

def start_ui():
    """Função para iniciar a aplicação."""
    app = App()
    app.mainloop()

if __name__ == '__main__':
    start_ui()