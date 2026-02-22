import socket
from scapy.all import sniff, IP, TCP, UDP

def obter_nome_host(ip):
    """Tenta descobrir o nome da máquina ou empresa dona do IP"""
    try:
        # A função gethostbyaddr faz o Reverse DNS
        nome_host, _, _ = socket.gethostbyaddr(ip)
        return nome_host
    except socket.herror:
        # Se o IP não tiver um nome público registrado, retorna Desconhecido
        return "Desconhecido"

def analisar_pacote_v3(pacote):
    # Verifica se o pacote tem a camada IP
    if pacote.haslayer(IP):
        ip_origem = pacote[IP].src
        ip_destino = pacote[IP].dst
        
        # 1. FILTRO DE RUÍDO LOCAL (Ignora Broadcast e Multicast)
        if (ip_destino.endswith('.255') or 
            ip_destino.startswith('224.') or 
            ip_destino.startswith('239.') or 
            ip_destino == '255.255.255.255'):
            return # Interrompe a análise deste pacote e vai para o próximo
        
        porta_origem = "N/A"
        porta_destino = "N/A"
        protocolo = "Outro"

        # Extrai as portas
        if pacote.haslayer(TCP):
            protocolo = "TCP"
            porta_origem = pacote[TCP].sport
            porta_destino = pacote[TCP].dport
        elif pacote.haslayer(UDP):
            protocolo = "UDP"
            porta_origem = pacote[UDP].sport
            porta_destino = pacote[UDP].dport
        else:
            return # Ignora outros protocolos mais complexos por enquanto

        # 2. FILTRO DE PORTAS CONHECIDAS (Web e DNS)
        portas_ignoradas = [80, 443, 53]
        
        if porta_origem not in portas_ignoradas and porta_destino not in portas_ignoradas:
            
            # 3. IDENTIFICAÇÃO DO ALVO EXTERNO
            # Descobre qual dos dois IPs não é o do seu PC local para investigar
            ip_investigado = ip_destino if not ip_destino.startswith('192.168.') else ip_origem
            nome_empresa = "Rede Local"
            
            # Se o IP não for local, faz a pesquisa de Reverse DNS
            if not ip_investigado.startswith('192.168.'):
                nome_empresa = obter_nome_host(ip_investigado)

            print(f"[{protocolo}] ALERTA - CONEXÃO INCOMUM DETECTADA:")
            print(f"    Origem:  {ip_origem}:{porta_origem}")
            print(f"    Destino: {ip_destino}:{porta_destino}")
            print(f"    Dono do IP Externo: {nome_empresa}")
            print("-" * 55)

print("Iniciando o Sniffer v3.0 (Silencioso)... (Pressione Ctrl+C para parar)")
print("Aguardando tráfego fora do padrão...")

sniff(prn=analisar_pacote_v3, store=False)