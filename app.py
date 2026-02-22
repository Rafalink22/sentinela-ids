import customtkinter as ctk
from tkinter import ttk
from motor_sniffer import MotorSniffer
import psutil

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class JanelaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sentinela - Monitor de Tráfego de Rede")
        self.geometry("1000x650")
        
        self.motor = MotorSniffer()
        self.tempo_restante = -1 
        self.id_temporizador = None

        self.configurar_layout()
        self.estilizar_tabela()
        
        self.carregar_sessoes_db()
        self.atualizar_tabela_periodicamente()
        
        # INICIA O MONITORAMENTO DE HARDWARE ASSIM QUE ABRIR
        self.monitorar_hardware()

    def configurar_layout(self):
        # --- PAINEL LATERAL ---
        self.frame_lateral = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.frame_lateral.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(self.frame_lateral, text="🛡️ SENTINELA", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.pack(pady=(30, 30))

        self.lbl_tempo = ctk.CTkLabel(self.frame_lateral, text="Duração do Monitoramento:")
        self.lbl_tempo.pack(pady=(10, 0), padx=20, anchor="w")
        
        self.combo_tempo = ctk.CTkComboBox(self.frame_lateral, values=["Até eu parar", "1 Minuto (Teste)", "15 Minutos", "1 Hora"])
        self.combo_tempo.pack(pady=(5, 20), padx=20, fill="x")

        self.btn_toggle = ctk.CTkButton(self.frame_lateral, text="INICIAR CAPTURA", fg_color="green", hover_color="darkgreen", command=self.toggle_motor)
        self.btn_toggle.pack(pady=10, padx=20, fill="x")

        self.lbl_relogio = ctk.CTkLabel(self.frame_lateral, text="Status: Parado", font=ctk.CTkFont(size=14))
        self.lbl_relogio.pack(pady=10, padx=20)
        
        # ==========================================
        # PAINEL DE PERFORMANCE DO HARDWARE
        # ==========================================
        # Spacer para empurrar os status de hardware para o fundo da tela
        self.spacer = ctk.CTkFrame(self.frame_lateral, fg_color="transparent")
        self.spacer.pack(fill="y", expand=True)

        self.frame_hardware = ctk.CTkFrame(self.frame_lateral, fg_color="#2b2b2b", corner_radius=10)
        self.frame_hardware.pack(pady=20, padx=20, fill="x")

        self.lbl_hard_titulo = ctk.CTkLabel(self.frame_hardware, text="Consumo do Sistema", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_hard_titulo.pack(pady=(10, 5))

        self.lbl_cpu = ctk.CTkLabel(self.frame_hardware, text="CPU: Calculando...", font=ctk.CTkFont(size=12))
        self.lbl_cpu.pack(pady=0)
        
        self.lbl_ram = ctk.CTkLabel(self.frame_hardware, text="RAM: Calculando...", font=ctk.CTkFont(size=12))
        self.lbl_ram.pack(pady=(0, 10))

        # --- PAINEL CENTRAL ---
        self.frame_central = ctk.CTkFrame(self)
        self.frame_central.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.frame_top_tabela = ctk.CTkFrame(self.frame_central, fg_color="transparent")
        self.frame_top_tabela.pack(fill="x", pady=10, padx=10)

        self.lbl_titulo_tabela = ctk.CTkLabel(self.frame_top_tabela, text="Histórico de Alertas:", font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_titulo_tabela.pack(side="left")

        self.combo_sessao = ctk.CTkComboBox(self.frame_top_tabela, width=220, command=self.forcar_atualizacao_tabela)
        self.combo_sessao.pack(side="right")
        self.lbl_sessao = ctk.CTkLabel(self.frame_top_tabela, text="Visualizando Sessão:")
        self.lbl_sessao.pack(side="right", padx=10)

        colunas = ("ID", "Data/Hora", "Proto", "Porta Local", "Alvo", "Porta Alvo", "Host/Empresa")
        self.tabela = ttk.Treeview(self.frame_central, columns=colunas, show="headings", height=20)
        
        larguras = {"ID": 40, "Data/Hora": 140, "Proto": 50, "Porta Local": 80, "Alvo": 120, "Porta Alvo": 80, "Host/Empresa": 180}
        for col in colunas:
            self.tabela.heading(col, text=col)
            self.tabela.column(col, width=larguras[col], anchor="center")

        self.tabela.pack(fill="both", expand=True, padx=10, pady=10)

    def estilizar_tabela(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=25, fieldbackground="#2b2b2b", borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", background="#1f538d", foreground="white", relief="flat", font=('Arial', 10, 'bold'))
        style.map("Treeview.Heading", background=[('active', '#14375e')])

    def carregar_sessoes_db(self):
        sessoes = self.motor.db.buscar_sessoes()
        if sessoes:
            self.combo_sessao.configure(values=sessoes)
            self.combo_sessao.set(sessoes[0]) 
        else:
            self.combo_sessao.configure(values=["Nenhuma sessão salva"])
            self.combo_sessao.set("Nenhuma sessão salva")

    def toggle_motor(self):
        if not self.motor.rodando:
            selecao = self.combo_tempo.get()
            self.configurar_temporizador(selecao)
            
            self.motor.iniciar()
            self.btn_toggle.configure(text="PARAR CAPTURA", fg_color="red", hover_color="darkred")
            self.combo_tempo.configure(state="disabled") 
            
            nova_sessao = self.motor.sessao_atual
            valores_atuais = self.combo_sessao.cget("values")
            if "Nenhuma sessão salva" in valores_atuais:
                self.combo_sessao.configure(values=[nova_sessao])
            else:
                self.combo_sessao.configure(values=[nova_sessao] + list(valores_atuais))
                
            self.combo_sessao.set(nova_sessao)
            self.combo_sessao.configure(state="disabled") 
            
            self.atualizar_relogio()
        else:
            self.parar_captura_manualmente()

    def configurar_temporizador(self, selecao):
        if selecao == "1 Minuto (Teste)":
            self.tempo_restante = 60
        elif selecao == "15 Minutos":
            self.tempo_restante = 15 * 60
        elif selecao == "1 Hora":
            self.tempo_restante = 60 * 60
        else:
            self.tempo_restante = -1 

    def atualizar_relogio(self):
        if not self.motor.rodando:
            return 

        if self.tempo_restante > 0:
            minutos, segundos = divmod(self.tempo_restante, 60)
            self.lbl_relogio.configure(text=f"Tempo Restante: {minutos:02d}:{segundos:02d}")
            self.tempo_restante -= 1
            self.id_temporizador = self.after(1000, self.atualizar_relogio)
        elif self.tempo_restante == 0:
            self.parar_captura_manualmente()
            self.lbl_relogio.configure(text="Status: Concluído (Tempo Esgotado)")
        elif self.tempo_restante == -1:
            self.lbl_relogio.configure(text="Status: Rodando Indefinidamente...")
            self.id_temporizador = self.after(1000, self.atualizar_relogio)

    def parar_captura_manualmente(self):
        self.motor.parar()
        if self.id_temporizador:
            self.after_cancel(self.id_temporizador)
            
        self.btn_toggle.configure(text="INICIAR CAPTURA", fg_color="green", hover_color="darkgreen")
        self.combo_tempo.configure(state="normal")
        self.combo_sessao.configure(state="normal") 
        self.lbl_relogio.configure(text="Status: Parado.")

    def forcar_atualizacao_tabela(self, _=None):
        self.atualizar_tabela_periodicamente(loop=False)

    def atualizar_tabela_periodicamente(self, loop=True):
        for item in self.tabela.get_children():
            self.tabela.delete(item)
            
        sessao_selecionada = self.combo_sessao.get()
        registos = self.motor.db.buscar_historico(sessao=sessao_selecionada, limite=50)
        
        for linha in registos:
            id_bd, _, data_hora, proto, _, porta_origem, ip_destino, porta_destino, host = linha
            valores = (id_bd, data_hora, proto, porta_origem, ip_destino, porta_destino, host)
            self.tabela.insert("", "end", values=valores)
            
        if loop:
            self.after(2000, self.atualizar_tabela_periodicamente)

    # ==========================================
    # MÉTODO QUE LÊ O HARDWARE DO PRÓPRIO APP
    # ==========================================
    def monitorar_hardware(self):
        """Atualiza os medidores de CPU e RAM DO NOSSO EXECUTÁVEL a cada segundo"""
        try:
            # Captura o processo atual (o nosso app.py ou Sentinela.exe)
            processo = psutil.Process()
            
            # Pega a % de uso da CPU exclusiva deste processo desde a última checagem
            uso_cpu = processo.cpu_percent(interval=None)
            
            # Pega o uso real de RAM (Resident Set Size - RSS) em bytes
            memoria_bytes = processo.memory_info().rss
            
            # Converte de Bytes para Megabytes (MB)
            uso_ram_mb = memoria_bytes / (1024 * 1024)
            
            # Atualiza o texto na tela
            self.lbl_cpu.configure(text=f"App CPU: {uso_cpu:.1f}%")
            self.lbl_ram.configure(text=f"App RAM: {uso_ram_mb:.1f} MB")
            
            # Como agora estamos medindo o nosso app, os limites mudam.
            # Se o nosso sniffer passar de 15% de CPU ou 150MB de RAM, ele avisa (fica vermelho)
            cor_cpu = "red" if uso_cpu > 15.0 else "white"
            cor_ram = "red" if uso_ram_mb > 150.0 else "white"
            
            self.lbl_cpu.configure(text_color=cor_cpu)
            self.lbl_ram.configure(text_color=cor_ram)
            
        except Exception as e:
            # Previne que o app trave se o Windows negar acesso à leitura do processo
            pass
            
        # Roda o loop infinitamente a cada 1 segundo
        self.after(1000, self.monitorar_hardware)

if __name__ == "__main__":
    app = JanelaPrincipal()
    app.mainloop()