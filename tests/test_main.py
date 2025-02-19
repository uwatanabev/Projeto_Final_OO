# tests/test_main.py
import os
import tempfile
import unittest
from main import app, init_db
from models import Produto, Usuario

class MainTestCase(unittest.TestCase):
    def setUp(self):
        # Cria um arquivo temporário para o banco de dados
        self.db_fd, temp_db = tempfile.mkstemp()
        app.config['DATABASE'] = temp_db
        global db_path
        from models import db_path as model_db_path
        db_path = temp_db
        app.config['TESTING'] = True
        self.client = app.test_client()
        init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Produtos Dispon', response.data)

    def test_register_and_login(self):
        response = self.client.post('/register', data={
            'username': 'testuser',
            'password': 'testpass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Painel Administrativo', response.data)

    def test_add_product(self):
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': '1234'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Painel Administrativo', response.data)

        response = self.client.post('/admin', data={
            'nome': 'Produto Teste',
            'preco': '10.50',
            'quantidade': '5'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Produto Teste', response.data)

    def test_list_products(self):
        Produto("Produto Teste", 10.50, 5, "admin").salvar()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Produto Teste', response.data)

if __name__ == '__main__':
    unittest.main()
