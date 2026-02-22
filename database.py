import sqlite3
from datetime import datetime

class BancoDeDados:
    def __init__(self, nome_banco="historico_rede.db"):
        self.nome_banco = nome_banco
        self.criar_tabela()

    def conectar(self):
        return sqlite3.connect(self.nome_banco)

    def criar_tabela(self):
        conexao = self.conectar()
        cursor = conexao.cursor()
        
        # Adicionada a coluna 'sessao'
        sql_create = """
        CREATE TABLE IF NOT EXISTS alertas_rede (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sessao TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            protocolo TEXT NOT NULL,
            ip_origem TEXT NOT NULL,
            porta_origem TEXT NOT NULL,
            ip_destino TEXT NOT NULL,
            porta_destino TEXT NOT NULL,
            host_externo TEXT
        );
        """
        cursor.execute(sql_create)
        conexao.commit()
        conexao.close()

    def inserir_alerta(self, sessao, protocolo, ip_origem, porta_origem, ip_destino, porta_destino, host_externo):
        conexao = self.conectar()
        cursor = conexao.cursor()
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        sql_insert = """
        INSERT INTO alertas_rede 
        (sessao, timestamp, protocolo, ip_origem, porta_origem, ip_destino, porta_destino, host_externo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        valores = (sessao, agora, protocolo, ip_origem, porta_origem, ip_destino, porta_destino, host_externo)
        
        cursor.execute(sql_insert, valores)
        conexao.commit()
        conexao.close()

    def buscar_sessoes(self):
        """Retorna uma lista com o nome de todas as sessões registradas."""
        conexao = self.conectar()
        cursor = conexao.cursor()
        
        # Agrupa pelo nome da sessão e ordena para a mais recente ficar no topo
        sql_select = "SELECT sessao FROM alertas_rede GROUP BY sessao ORDER BY MAX(id) DESC"
        cursor.execute(sql_select)
        resultados = cursor.fetchall()
        conexao.close()
        
        # O SQLite retorna uma lista de tuplas: [('Sessão A',), ('Sessão B',)]. Extraímos o primeiro item.
        return [linha[0] for linha in resultados] if resultados else []

    def buscar_historico(self, sessao=None, limite=50):
        """Busca o histórico. Se uma sessão for passada, filtra por ela."""
        conexao = self.conectar()
        cursor = conexao.cursor()
        
        if sessao and sessao != "Nenhuma sessão salva":
            sql_select = f"SELECT * FROM alertas_rede WHERE sessao = ? ORDER BY id DESC LIMIT {limite}"
            cursor.execute(sql_select, (sessao,))
        else:
            sql_select = f"SELECT * FROM alertas_rede ORDER BY id DESC LIMIT {limite}"
            cursor.execute(sql_select)
            
        resultados = cursor.fetchall()
        conexao.close()
        return resultados