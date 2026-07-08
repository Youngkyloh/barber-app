import sqlite3
import pandas as pd

def conectar():
    return sqlite3.connect('barbearia.db', check_same_thread=False)

def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (telefone TEXT PRIMARY KEY, nome TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS barbeiros (nome TEXT PRIMARY KEY, senha TEXT)''')
    
    # NOVA TABELA: Catálogo dinâmico (Serviços, Produtos, Assinaturas)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS catalogo (
            item TEXT PRIMARY KEY,
            tipo TEXT,
            preco REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telefone TEXT,
            nome TEXT,
            barbeiro TEXT,
            item TEXT,
            data TEXT,
            hora TEXT,
            valor REAL,
            status TEXT DEFAULT 'Pendente'
        )
    ''')
    
    # Inserir dados padrão se o banco estiver vazio
    cursor.execute("SELECT COUNT(*) FROM barbeiros")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO barbeiros (nome, senha) VALUES (?, ?)", [('Thiago', '1234'), ('Marcos', '1234'), ('Leo', '1234')])
        
    cursor.execute("SELECT COUNT(*) FROM catalogo")
    if cursor.fetchone()[0] == 0:
        itens_iniciais = [
            ('Corte Padrão', 'Serviço', 40.0),
            ('Barba Completa', 'Serviço', 30.0),
            ('Pomada Modeladora', 'Produto', 35.0),
            ('Assinatura VIP (Mensal)', 'Assinatura', 150.0)
        ]
        cursor.executemany("INSERT INTO catalogo (item, tipo, preco) VALUES (?, ?, ?)", itens_iniciais)
        
    conn.commit()
    conn.close()

def get_cliente(telefone):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM clientes WHERE telefone = ?", (telefone,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else None

def add_cliente(telefone, nome):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clientes (telefone, nome) VALUES (?, ?)", (telefone, nome))
    conn.commit()
    conn.close()

def get_catalogo():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM catalogo", conn)
    conn.close()
    return df

def add_item_catalogo(item, tipo, preco):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR REPLACE INTO catalogo (item, tipo, preco) VALUES (?, ?, ?)", (item, tipo, preco))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def add_agendamento(telefone, nome, barbeiro, item, data, hora, valor):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO agendamentos (telefone, nome, barbeiro, item, data, hora, valor, status) 
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Pendente')
    ''', (telefone, nome, barbeiro, item, data, hora, valor))
    conn.commit()
    conn.close()

def get_horarios_ocupados(barbeiro, data):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT hora FROM agendamentos WHERE barbeiro = ? AND data = ? AND status != 'Cancelado'", (barbeiro, data))
    res = cursor.fetchall()
    conn.close()
    return [r[0] for r in res]

def get_barbeiros():
    conn = conectar()
    df = pd.read_sql_query("SELECT nome FROM barbeiros", conn)
    conn.close()
    return df['nome'].tolist()

def add_barbeiro(nome, senha):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO barbeiros (nome, senha) VALUES (?, ?)", (nome, senha))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def verificar_login_barbeiro(nome, senha):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM barbeiros WHERE nome = ? AND senha = ?", (nome, senha))
    res = cursor.fetchone()
    conn.close()
    return True if res else False

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