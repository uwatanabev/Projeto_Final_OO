import os
import tempfile
import unittest
import sys
import warnings

# Ignora os ResourceWarnings (se forem apenas avisos)
warnings.simplefilter("ignore", ResourceWarning)

# Insere o diretório raiz do projeto no path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, init_db
from models import Produto, Usuario

class AppTestCase(unittest.TestCase):
    def setUp(self):
        # Cria um arquivo temporário para o banco de dados de teste
        self.db_fd, temp_db = tempfile.mkstemp()
        app.config['DATABASE'] = temp_db
        global db_path
        from models import db_path as model_db_path
        db_path = temp_db

        app.config['TESTING'] = True
        self.client = app.test_client()
        init_db()
        
        # Limpa o cache do Jinja2 para evitar reter referências a conexões abertas
        app.jinja_env.cache = {}

        # Registra e loga um usuário padrão para os testes
        self.client.post('/register', data={'username': 'testuser', 'password': 'testpass'}, follow_redirects=True)
        self.client.post('/login', data={'username': 'testuser', 'password': 'testpass'}, follow_redirects=True)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Produtos Dispon', response.data)

    def test_register_and_login(self):
        # Testa registro de um novo usuário
        response = self.client.post('/register', data={'username': 'newuser', 'password': 'newpass'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
        
        # Testa login com o novo usuário
        response = self.client.post('/login', data={'username': 'newuser', 'password': 'newpass'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Painel Administrativo', response.data)

    def test_add_product(self):
        # Faz login como admin para adicionar produto
        self.client.post('/login', data={'username': 'admin', 'password': '1234'}, follow_redirects=True)
        response = self.client.post('/admin', data={'nome': 'Produto Teste', 'preco': '10.50', 'quantidade': '5'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Produto Teste', response.data)

    def test_list_products(self):
        Produto("Produto Teste", 10.50, 5, "admin").salvar()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Produto Teste', response.data)

if __name__ == '__main__':
    unittest.main()
