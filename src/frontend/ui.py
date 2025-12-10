import os # <-- Adicionado para manipulação de caminhos
import customtkinter as ctk
import threading
from tkinter import messagebox
import sys
import logging

# --- IMPORTAÇÕES CORRIGIDAS (Mudança de Relativa para Absoluta) ---
# A estrutura de pastas exige importações absolutas (começando por 'src')
try:
    from src.backend.cleanup import perform_cleanup
    from src.update.updater import is_update_available
except ImportError as e:
    logging.error(f"Erro de importação no UI: {e}")
    # Nota: O main.py já trata a saída, mas este log é bom para depuração interna.


# --- CONFIGURAÇÃO DO CAMINHO DO ÍCONE ---
# O ícone (blazescan_logo.ico) deve estar na raiz do projeto (BlazeScan/)
ICON_FILENAME = "blazescan_logo.ico" # <-- Use este nome para o seu arquivo .ico

ICON_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ICON_FILENAME))


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da janela principal
        self.title("BlazeScan - Otimizador de Sistema")
        self.geometry("500x400")
        
        # --- IMPLEMENTAÇÃO DO ÍCONE ---
        try:
            if sys.platform.startswith('win'):
                # iconbitmap é o método recomendado para arquivos .ico no Windows
                if os.path.exists(ICON_PATH):
                    self.iconbitmap(ICON_PATH)
                    logging.info(f"Ícone carregado com sucesso: {ICON_PATH}")
                else:
                    logging.warning(f"Ícone não encontrado em {ICON_PATH}. Usando ícone padrão.")
            else:
                # Opcional: Se precisar de suporte Linux/Mac, usaria iconphoto
                pass
        except Exception as e:
            logging.error(f"Falha ao carregar o ícone: {e}")
            
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Configuração do grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)

        # 1. Título
        self.title_label = ctk.CTkLabel(self, text="Otimização de Sistema BlazeScan", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="n")

        # 2. Área de Log
        self.log_text = ctk.CTkTextbox(self, width=450, height=200)
        self.log_text.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.log_text.insert("0.0", "Bem-vindo ao BlazeScan!\nClique em 'Iniciar Limpeza e Otimização' para começar.")
        self.log_text.configure(state="disabled")

        # 3. Label de Resultado
        self.result_label = ctk.CTkLabel(self, text="Tamanho Limpo: 0 Bytes", font=ctk.CTkFont(size=14))
        self.result_label.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="w")

        # 4. Botão de Ação
        self.cleanup_button = ctk.CTkButton(self, text="Iniciar Limpeza e Otimização", command=self.start_cleanup_thread)
        self.cleanup_button.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="s")

        # 5. Verificar atualização ao iniciar
        self.after(100, self.check_for_update)

    def update_log(self, message: str):
        """Atualiza a área de log com uma nova mensagem."""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", "\n" + message)
        self.log_text.see("end") # Rola para o final
        self.log_text.configure(state="disabled")

    def start_cleanup_thread(self):
        """Inicia a limpeza em uma thread separada para não travar a GUI."""
        self.cleanup_button.configure(state="disabled", text="Limpando...")
        self.update_log("\n--- INICIANDO PROCESSO DE LIMPEZA E OTIMIZAÇÃO ---")
        
        # Cria e inicia a thread
        cleanup_thread = threading.Thread(target=self.run_cleanup)
        cleanup_thread.start()

    def run_cleanup(self):
        """Função que executa a lógica de limpeza do backend."""
        try:
            # A função perform_cleanup retorna (sucesso_geral, mensagem_log, tamanho_limpo_formatado)
            # Nota: O log do console será exibido pelo backend
            success, log_message, formatted_size = perform_cleanup()
            
            # Atualiza a GUI após a conclusão (deve ser feito na thread principal)
            self.after(0, self.finish_cleanup, success, log_message, formatted_size)
            
        except Exception as e:
            self.after(0, self.finish_cleanup, False, f"Erro inesperado durante a limpeza: {e}", "0 Bytes")

    def finish_cleanup(self, success: bool, log_message: str, formatted_size: str):
        """Finaliza o processo de limpeza e atualiza a GUI."""
        # Note que a mensagem de log aqui é a saída sumarizada do backend,
        # enquanto os logs detalhados aparecem no console (CMD).
        self.update_log(log_message)
        self.result_label.configure(text=f"Tamanho Limpo: {formatted_size}")
        
        final_status = "CONCLUÍDO COM SUCESSO!" if success else "CONCLUÍDO COM ERROS."
        self.update_log(f"\n--- {final_status} ---")
        
        self.cleanup_button.configure(state="normal", text="Iniciar Limpeza e Otimização")

    def check_for_update(self):
        """Verifica se há uma nova versão disponível e mostra um pop-up."""
        update_thread = threading.Thread(target=self._run_update_check)
        update_thread.start()

    def _run_update_check(self):
        """Lógica de verificação de atualização."""
        # Se a importação falhar, is_update_available não será definida.
        try:
            available, local_version, latest_version = is_update_available()
            
            if available:
                self.after(0, self._show_update_popup, local_version, latest_version)
        except NameError:
            logging.warning("Módulo de atualização não carregado. Pulando verificação.")
        except Exception as e:
            logging.error(f"Erro na verificação de atualização: {e}")

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