---

# E-commerce Flask

Um projeto de e-commerce desenvolvido com Flask, que implementa funcionalidades essenciais como autenticação de usuários (login/logout), gerenciamento de produtos, carrinho de compras, finalização de pedidos, avaliações e histórico de atividades. Além disso, o projeto utiliza WebSocket com Flask-SocketIO para notificações em tempo real e conta com uma interface responsiva e moderna.

## Funcionalidades

- **Autenticação:** Cadastro e login de usuários, com controle de acesso às páginas protegidas.
- **Gerenciamento de Produtos:** Painel administrativo para adicionar, editar e excluir produtos.
- **Carrinho de Compras:** Adição, remoção e listagem de produtos no carrinho.
- **Pedidos:** Finalização de pedidos, com atualização do estoque e histórico de atividades.
- **Avaliações:** Sistema de avaliações para produtos com média e contagem de avaliações.
- **Notificações em Tempo Real:** Utilização de WebSocket para notificar os clientes quando um novo produto é adicionado.
- **Responsividade:** Layout responsivo com CSS moderno e transições suaves para melhor experiência em dispositivos móveis.

## Estrutura do Projeto

- **main.py:** Arquivo principal que inicializa a aplicação Flask e o SocketIO.
- **controllers.py:** Rotas e lógica principal do backend.
- **models.py:** Modelos e interações com o banco de dados SQLite.
- **static/**: Arquivos estáticos, incluindo o `style.css`.
- **templates/**: Arquivos HTML que compõem as páginas do site.
- **tests/**: Testes unitários que garantem a qualidade das funcionalidades.
- **requirements.txt:** Lista de dependências do projeto.
- **Dockerfile:** Arquivo para criação da imagem Docker da aplicação.
- **docker-compose.yml:** Configuração opcional para executar a aplicação via Docker Compose.

## Requisitos

- Python 3.9 ou superior
- Flask
- Flask-SocketIO
- Eventlet
- SQLite (banco de dados utilizado)
- (Opcional) Docker

## Instalação

### Executando Localmente

1. **Clone o repositório:**

   ```bash
   git clone <URL_do_repositorio>
   cd <nome_do_projeto>
   ```

2. **Crie e ative um ambiente virtual (opcional, mas recomendado):**

   ```bash
   python -m venv venv
   source venv/bin/activate   # Unix/MacOS
   venv\Scripts\activate      # Windows
   ```

3. **Instale as dependências:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Inicie a aplicação:**

   ```bash
   python main.py
   ```

   A aplicação estará disponível em `http://localhost:5000`.

### Executando com Docker

1. **Construa a imagem Docker:**

   ```bash
   docker build -t ecommerce-flask .
   ```

2. **Execute o container:**

   ```bash
   docker run -p 5000:5000 ecommerce-flask
   ```

   Ou, para usar o Docker Compose:

   ```bash
   docker-compose up --build
   ```

   A aplicação estará disponível em `http://localhost:5000`.

## Testes

Para rodar os testes unitários, execute:

```bash
python -m unittest discover tests
```

## Melhorias Futuras

- Aumentar a cobertura dos testes unitários e implementar testes de integração.
- Adicionar filtros e buscas avançadas para produtos.
- Melhorar a experiência do usuário com mais elementos de UI/UX.
- Implementar recursos adicionais conforme novas necessidades.

## Contribuição

Contribuições são muito bem-vindas! Caso deseje contribuir, por favor abra uma issue ou envie um pull request com as suas melhorias ou correções.

## Contato

Bernardo Watanabe Venzi - 232001120
Pedro Henrique Pereia Santos - 232038442

---