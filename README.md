# 🛡️ Sentinela - Network Traffic Monitor & IDS

O **Sentinela** é uma ferramenta de monitoramento de rede e Detecção de Intrusão (IDS) de código aberto, desenvolvida em Python. Projetado para rodar em background, o software intercepta, filtra e analisa pacotes de rede (TCP/UDP) em tempo real, alertando o usuário sobre conexões externas anômalas ou desconhecidas saindo da máquina.

Este projeto foi construído com foco em **Engenharia de Software** e **Redes de Computadores**, aplicando conceitos de Programação Orientada a Objetos (POO), concorrência (Multithreading), persistência de dados e design de interface (UI/UX).



## ✨ Principais Funcionalidades

* **Sniffing em Tempo Real:** Captura de pacotes brutos na camada de rede utilizando a biblioteca `scapy`.
* **Filtro Inteligente de Ruído:** O motor ignora automaticamente tráfego local inofensivo (Broadcast/Multicast), requisições DNS (porta 53) e navegação web padrão (portas 80 e 443), focando apenas em conexões de background que exigem atenção.
* **Reverse DNS (rDNS):** Resolução automática de IPs externos para identificar o nome do host/empresa de destino.
* **Sistema de Sessões e Logs:** Toda vez que a captura é iniciada, uma nova sessão é criada. Os alertas são salvos dinamicamente em arquivos `.txt` isolados por sessão para fácil auditoria.
* **Persistência de Dados:** Histórico completo de alertas armazenado localmente em um banco de dados **SQLite**.
* **Hardware Profiling:** Monitoramento ao vivo do consumo de CPU e RAM (em MB) isolado do próprio processo da aplicação, garantindo ausência de *memory leaks*.
* **Interface Gráfica Assíncrona:** Desenvolvida com `CustomTkinter`, a UI roda de forma totalmente independente do motor de captura graças à arquitetura Multithreading, garantindo que o software nunca congele.

## 🏗️ Arquitetura do Software

O sistema foi modularizado para separar as responsabilidades lógicas:

1. **`app.py` (View/Controller):** Gerencia o loop de eventos da interface gráfica, atualiza a tabela puxando dados do banco e lida com o profiling de hardware usando `psutil`.
2. **`motor_sniffer.py` (Model/Service):** Roda em uma Thread separada (Background Worker). Encapsula a lógica de interceptação do Scapy, filtra pacotes, resolve domínios e escreve os logs físicos em `.txt`.
3. **`database.py` (Data Access Layer):** Classe dedicada à conexão com o SQLite. Garante a criação do *schema* e execução segura de queries (evitando SQL Injection via parametrização).

## 🚀 Como Executar o Projeto

Você pode utilizar a ferramenta de duas formas: através do código fonte ou pelo executável portátil.

### Opção A: Executável Standalone (.exe)
Se você deseja apenas usar o software sem instalar o Python:
1. Vá até a aba **[Releases]** deste repositório.
2. Baixe o arquivo `Sentinela.exe`.
3. Execute o arquivo com **privilégios de Administrador** (necessário para ler a placa de rede).

### Opção B: Rodando o Código Fonte
Para desenvolvedores que desejam modificar ou estudar o código:

**Pré-requisitos:**
* Python 3.10+
* Npcap (Driver de captura de pacotes para Windows - [npcap.com](https://npcap.com/))

**Instalação:**
1. Clone este repositório:
   ```bash
   git clone [https://github.com/SEU_USUARIO/sentinela-ids.git](https://github.com/SEU_USUARIO/sentinela-ids.git)
   cd sentinela-ids
