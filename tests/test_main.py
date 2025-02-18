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
        
        # Atualiza a variável global db_path para os testes
        global db_path
        db_path = temp_db
        
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Inicializa o banco de dados de teste
        init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_index(self):
        # Verifica se a página inicial retorna 200 e contém a palavra 'Produtos'
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Produtos Dispon\xc3\xadveis', response.data)

    def test_register_and_login(self):
        # Testa o fluxo de registro e login
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
        # Testa se é possível adicionar um produto no painel administrativo
        # Primeiro, loga como admin
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': '1234'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Painel Administrativo', response.data)
        
        # Adiciona um produto
        response = self.client.post('/admin', data={
            'nome': 'Produto Teste',
            'preco': '10.50',
            'quantidade': '5'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Verifica se o produto aparece na lista de produtos
        self.assertIn(b'Produto Teste', response.data)

    def test_list_products(self):
        # Testa se a listagem de produtos funciona
        Produto("Produto Teste", 10.50, 5, "admin").salvar()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Produto Teste', response.data)

if __name__ == '__main__':
    unittest.main()
