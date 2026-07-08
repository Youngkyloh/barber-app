import sqlite3
import pandas as pd

# Conexão centralizada
def conectar():
    return sqlite3.connect('barbearia.db', check_same_thread=False)

def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()
    # Tabela de Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            telefone TEXT PRIMARY KEY,
            nome TEXT
        )
    ''')
    # Tabela de Agendamentos (com coluna de STATUS)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telefone TEXT,
            nome TEXT,
            barbeiro TEXT,
            servico TEXT,
            data TEXT,
            hora TEXT,
            valor REAL,
            status TEXT DEFAULT 'Pendente'
        )
    ''')
    # Tabela de Barbeiros
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS barbeiros (
            nome TEXT PRIMARY KEY
        )
    ''')
    
    # Inserir barbeiros padrão se a tabela estiver vazia
    cursor.execute("SELECT COUNT(*) FROM barbeiros")
    if cursor.fetchone()[0] == 0:
        barbeiros_iniciais = [('Thiago',), ('Marcos',), ('Leo',)]
        cursor.executemany("INSERT INTO barbeiros (nome) VALUES (?)", barbeiros_iniciais)
        
    conn.commit()
    conn.close()

# Funções Seguras de Leitura e Escrita (CRUD)
def get_cliente(telefone):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM clientes WHERE telefone = ?", (telefone,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

def add_cliente(telefone, nome):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clientes (telefone, nome) VALUES (?, ?)", (telefone, nome))
    conn.commit()
    conn.close()

def add_agendamento(telefone, nome, barbeiro, servico, data, hora, valor):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO agendamentos (telefone, nome, barbeiro, servico, data, hora, valor, status) 
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Pendente')
    ''', (telefone, nome, barbeiro, servico, data, hora, valor))
    conn.commit()
    conn.close()

def get_horarios_ocupados(barbeiro, data):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT hora FROM agendamentos WHERE barbeiro = ? AND data = ? AND status != 'Cancelado'", (barbeiro, data))
    resultados = cursor.fetchall()
    conn.close()
    return [r[0] for r in resultados]

def get_barbeiros():
    conn = conectar()
    df = pd.read_sql_query("SELECT nome FROM barbeiros", conn)
    conn.close()
    return df['nome'].tolist()

def add_barbeiro(nome):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO barbeiros (nome) VALUES (?)", (nome,))
        conn.commit()
        sucesso = True
    except:
        sucesso = False
    conn.close()
    return sucesso

def get_todos_agendamentos():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM agendamentos", conn)
    conn.close()
    return df

def atualizar_status(id_agendamento, novo_status):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE agendamentos SET status = ? WHERE id = ?", (novo_status, id_agendamento))
    conn.commit()
    conn.close()