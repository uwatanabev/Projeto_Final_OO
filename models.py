import sqlite3
import os

db_path = "ecommerce.db"

class DatabaseManager:
    """Gerencia operações com o banco de dados."""
    @staticmethod
    def init_db():
        if not os.path.exists(db_path):
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                # Tabela de produtos com quantidade e vendedor (username)
                cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    nome TEXT NOT NULL,
                                    preco REAL NOT NULL,
                                    quantidade INTEGER NOT NULL DEFAULT 0,
                                    username TEXT NOT NULL)''')
                # Tabela de usuários
                cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    username TEXT NOT NULL UNIQUE,
                                    password TEXT NOT NULL)''')
                # Tabela do carrinho de compras
                cursor.execute('''CREATE TABLE IF NOT EXISTS carrinho (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    username TEXT NOT NULL,
                                    product_id INTEGER NOT NULL,
                                    quantity INTEGER NOT NULL,
                                    FOREIGN KEY(product_id) REFERENCES produtos(id))''')
                # Tabela de pedidos finalizados
                cursor.execute('''CREATE TABLE IF NOT EXISTS pedidos (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    username TEXT NOT NULL,
                                    total REAL NOT NULL,
                                    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    status TEXT NOT NULL)''')
                # Itens de cada pedido
                cursor.execute('''CREATE TABLE IF NOT EXISTS itens_pedido (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    pedido_id INTEGER NOT NULL,
                                    product_id INTEGER NOT NULL,
                                    quantity INTEGER NOT NULL,
                                    price REAL NOT NULL,
                                    FOREIGN KEY(pedido_id) REFERENCES pedidos(id),
                                    FOREIGN KEY(product_id) REFERENCES produtos(id))''')
                # Log de atividades (histórico)
                cursor.execute('''CREATE TABLE IF NOT EXISTS log_atividades (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    username TEXT NOT NULL,
                                    acao TEXT NOT NULL,
                                    detalhes TEXT,
                                    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
                # Avaliações de produtos
                cursor.execute('''CREATE TABLE IF NOT EXISTS avaliacoes (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    product_id INTEGER NOT NULL,
                                    username TEXT NOT NULL,
                                    rating INTEGER NOT NULL,
                                    comment TEXT,
                                    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    FOREIGN KEY(product_id) REFERENCES produtos(id))''')
                # Insere um usuário admin padrão
                cursor.execute("INSERT OR IGNORE INTO usuarios (username, password) VALUES (?, ?)", ("admin", "1234"))
                conn.commit()

    @staticmethod
    def get_connection():
        return sqlite3.connect(db_path)


class Produto:
    """Modelo de produto."""
    def __init__(self, nome, preco, quantidade, username, id=None):
        self.id = id
        self.nome = nome
        self.preco = preco
        self.quantidade = quantidade
        self.username = username

    def salvar(self):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO produtos (nome, preco, quantidade, username) VALUES (?, ?, ?, ?)",
                (self.nome, self.preco, self.quantidade, self.username)
            )
            conn.commit()

    @staticmethod
    def listar_por_usuario(username):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM produtos WHERE username = ?", (username,))
            return cursor.fetchall()

    @staticmethod
    def listar_todos():
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM produtos WHERE quantidade > 0")
            return cursor.fetchall()

    @staticmethod
    def obter_por_id(produto_id):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
            return cursor.fetchone()

    def atualizar(self):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE produtos SET nome = ?, preco = ?, quantidade = ? WHERE id = ?",
                (self.nome, self.preco, self.quantidade, self.id)
            )
            conn.commit()

    @staticmethod
    def excluir(produto_id):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
            conn.commit()


class Usuario:
    """Modelo de usuário."""
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def registrar(self):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuarios (username, password) VALUES (?, ?)",
                (self.username, self.password)
            )
            conn.commit()

    @staticmethod
    def autenticar(username, password):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM usuarios WHERE username = ? AND password = ?",
                (username, password)
            )
            return cursor.fetchone()


class Carrinho:
    """Gerencia o carrinho de compras."""
    @staticmethod
    def adicionar(username, product_id, quantity):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quantidade FROM produtos WHERE id = ?", (product_id,))
            available = cursor.fetchone()
            if available is None:
                return
            available_stock = available[0]
            cursor.execute(
                "SELECT id, quantity FROM carrinho WHERE username = ? AND product_id = ?",
                (username, product_id)
            )
            item = cursor.fetchone()
            if item:
                new_quantity = item[1] + quantity
                if new_quantity > available_stock:
                    new_quantity = available_stock
                cursor.execute(
                    "UPDATE carrinho SET quantity = ? WHERE id = ?",
                    (new_quantity, item[0])
                )
            else:
                if quantity > available_stock:
                    quantity = available_stock
                cursor.execute(
                    "INSERT INTO carrinho (username, product_id, quantity) VALUES (?, ?, ?)",
                    (username, product_id, quantity)
                )
            conn.commit()

    @staticmethod
    def listar(username):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT carrinho.id, produtos.nome, produtos.preco, carrinho.quantity, produtos.id "
                "FROM carrinho INNER JOIN produtos ON carrinho.product_id = produtos.id "
                "WHERE carrinho.username = ?",
                (username,)
            )
            return cursor.fetchall()

    @staticmethod
    def remover(item_id):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM carrinho WHERE id = ?", (item_id,))
            conn.commit()

    @staticmethod
    def limpar(username):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM carrinho WHERE username = ?", (username,))
            conn.commit()


class Pedido:
    """Gerencia a finalização de pedidos."""
    @staticmethod
    def finalizar(username):
        itens = Carrinho.listar(username)
        if not itens:
            return None
        total = sum(item[2] * item[3] for item in itens)
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO pedidos (username, total, status) VALUES (?, ?, ?)",
                (username, total, "finalizado")
            )
            pedido_id = cursor.lastrowid
            for item in itens:
                product_id = item[4]
                quantity = item[3]
                price = item[2]
                cursor.execute(
                    "INSERT INTO itens_pedido (pedido_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                    (pedido_id, product_id, quantity, price)
                )
                cursor.execute(
                    "UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?",
                    (quantity, product_id)
                )
            conn.commit()
        Carrinho.limpar(username)
        LogAtividades.registrar(username, "finalizar_pedido", f"Pedido {pedido_id} finalizado com total {total}")
        return pedido_id


class LogAtividades:
    """Registra as atividades dos usuários."""
    @staticmethod
    def registrar(username, acao, detalhes):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO log_atividades (username, acao, detalhes) VALUES (?, ?, ?)",
                (username, acao, detalhes)
            )
            conn.commit()

    @staticmethod
    def listar(username):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM log_atividades WHERE username = ? ORDER BY data DESC",
                (username,)
            )
            return cursor.fetchall()


class Avaliacao:
    """Gerencia as avaliações de produtos."""
    @staticmethod
    def registrar(product_id, username, rating, comment):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO avaliacoes (product_id, username, rating, comment) VALUES (?, ?, ?, ?)",
                (product_id, username, rating, comment)
            )
            conn.commit()

    @staticmethod
    def listar_por_produto(product_id):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM avaliacoes WHERE product_id = ? ORDER BY data DESC",
                (product_id,)
            )
            return cursor.fetchall()

    @staticmethod
    def media_rating(product_id):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT AVG(rating) FROM avaliacoes WHERE product_id = ?", (product_id,))
            avg = cursor.fetchone()[0]
            if avg is None:
                return None
            return round(avg, 1)

    @staticmethod
    def contar(product_id):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM avaliacoes WHERE product_id = ?", (product_id,))
            return cursor.fetchone()[0]
