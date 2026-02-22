import os
import socket
import threading
from datetime import datetime
from scapy.all import sniff, IP, TCP, UDP
from database import BancoDeDados

class MotorSniffer:
    def __init__(self):
        """
        Construtor. Inicializa o banco de dados e prepara a estrutura de pastas para os logs.
        """
        self.db = BancoDeDados()
        self.rodando = False
        self.thread_captura = None
        self.arquivo_log_atual = None
        
        # Cria a pasta 'logs' automaticamente se ela não existir
        if not os.path.exists("logs"):
            os.makedirs("logs")

    def _obter_nome_host(self, ip):
        """Tenta resolver o Reverse DNS do IP fornecido."""
        try:
            nome_host, _, _ = socket.gethostbyaddr(ip)
            return nome_host
        except socket.herror:
            return "Desconhecido"

    def _analisar_pacote(self, pacote):
        if not self.rodando:
            return

        if pacote.haslayer(IP):
            ip_origem = pacote[IP].src
            ip_destino = pacote[IP].dst
            
            if (ip_destino.endswith('.255') or ip_destino.startswith('224.') or ip_destino.startswith('239.') or ip_destino == '255.255.255.255'):
                return
            
            porta_origem = "N/A"
            porta_destino = "N/A"
            protocolo = "Outro"

            if pacote.haslayer(TCP):
                protocolo = "TCP"
                porta_origem = pacote[TCP].sport
                porta_destino = pacote[TCP].dport
            elif pacote.haslayer(UDP):
                protocolo = "UDP"
                porta_origem = pacote[UDP].sport
                porta_destino = pacote[UDP].dport
            else:
                return

            portas_ignoradas = [80, 443, 53]
            
            if porta_origem not in portas_ignoradas and porta_destino not in portas_ignoradas:
                ip_investigado = ip_destino if not ip_destino.startswith('192.168.') else ip_origem
                host_externo = "Rede Local"
                
                if not ip_investigado.startswith('192.168.'):
                    host_externo = self._obter_nome_host(ip_investigado)

                # SALVA NO BANCO COM O ID DA SESSÃO ATUAL
                self.db.inserir_alerta(
                    sessao=self.sessao_atual,
                    protocolo=protocolo,
                    ip_origem=ip_origem,
                    porta_origem=str(porta_origem),
                    ip_destino=ip_destino,
                    porta_destino=str(porta_destino),
                    host_externo=host_externo
                )
                
                if self.arquivo_log_atual:
                    agora_str = datetime.now().strftime("%H:%M:%S")
                    linha_log = f"[{agora_str}] ALERTA {protocolo} | Origem: {ip_origem}:{porta_origem} -> Destino: {ip_destino}:{porta_destino} (Host: {host_externo})\n"
                    with open(self.arquivo_log_atual, "a", encoding="utf-8") as f:
                        f.write(linha_log)

    def _iniciar_sniff(self):
        sniff(prn=self._analisar_pacote, store=False, stop_filter=lambda x: not self.rodando)

    def iniciar(self):
        if not self.rodando:
            # Define o nome da Sessão que vai tanto para o SQLite quanto para o .txt
            self.sessao_atual = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
            timestamp_arquivo = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            self.arquivo_log_atual = f"logs/captura_{timestamp_arquivo}.txt"
            
            with open(self.arquivo_log_atual, "w", encoding="utf-8") as f:
                f.write("=" * 70 + "\n")
                f.write(f"  Sessão Iniciada em: {self.sessao_atual}\n")
                f.write("=" * 70 + "\n\n")

            self.rodando = True
            self.thread_captura = threading.Thread(target=self._iniciar_sniff, daemon=True)
            self.thread_captura.start()

    def parar(self):
        """Encerra a captura e finaliza o arquivo de log."""
        if self.rodando:
            self.rodando = False
            if self.thread_captura:
                self.thread_captura.join(timeout=2)
            
            # Escreve o rodapé avisando que a sessão terminou corretamente
            if self.arquivo_log_atual:
                with open(self.arquivo_log_atual, "a", encoding="utf-8") as f:
                    f.write("\n" + "=" * 70 + "\n")
                    f.write(f"  Sessão Encerrada em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}\n")
                    f.write("=" * 70 + "\n")