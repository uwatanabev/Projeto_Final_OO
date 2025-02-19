# controllers.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import Produto, Usuario, Carrinho, Pedido, LogAtividades, Avaliacao
bp = Blueprint("bp", __name__)

@bp.route('/')
def index():
    produtos = Produto.listar_todos()
    product_data = []
    for p in produtos:
        product_id, nome, preco, quantidade, seller = p
        avg = Avaliacao.media_rating(product_id)
        count = Avaliacao.contar(product_id)
        product_data.append({
            "id": product_id,
            "nome": nome,
            "preco": preco,
            "quantidade": quantidade,
            "username": seller,
            "avg_rating": avg,
            "count_rating": count
        })
    username = session.get('username')
    return render_template('index.html', produtos=product_data, username=username)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if Usuario.autenticar(username, password):
            session['username'] = username
            return redirect(url_for('bp.admin'))
        else:
            flash("Login inválido! Verifique suas credenciais e tente novamente.", "error")
            return render_template('login.html')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('bp.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            usuario = Usuario(username, password)
            usuario.registrar()
            return redirect(url_for('bp.login'))
        except Exception:
            flash("Usuário já existe! Tente outro nome.", "error")
            return render_template('register.html')
    return render_template('register.html')

@bp.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'username' not in session:
        return redirect(url_for('bp.login'))
    username = session['username']
    if request.method == 'POST':
        nome = request.form['nome']
        preco = request.form['preco']
        quantidade = request.form['quantidade']
        produto = Produto(nome, preco, quantidade, username)
        produto.salvar()
        LogAtividades.registrar(username, "adicionar_produto", f"Produto {nome} adicionado.")
        # Emite mensagem via WebSocket para notificar os clientes conectados
        from main import socketio
        socketio.emit("mensagem", f"Novo produto {nome} adicionado!", broadcast=True)
        return redirect(url_for('bp.admin'))
    produtos = Produto.listar_por_usuario(username)
    return render_template('admin.html', produtos=produtos, username=username)

@bp.route('/admin/edit/<int:produto_id>', methods=['GET', 'POST'])
def edit_produto(produto_id):
    if 'username' not in session:
        return redirect(url_for('bp.login'))
    produto = Produto.obter_por_id(produto_id)
    if not produto:
        return "Produto não encontrado."
    if request.method == 'POST':
        nome = request.form['nome']
        preco = request.form['preco']
        quantidade = request.form['quantidade']
        produto_atualizado = Produto(nome, preco, quantidade, produto[4], produto[0])
        produto_atualizado.atualizar()
        LogAtividades.registrar(session['username'], "editar_produto", f"Produto {nome} editado.")
        return redirect(url_for('bp.admin'))
    return render_template('edit.html', produto=produto)

@bp.route('/admin/delete/<int:produto_id>')
def delete_produto(produto_id):
    if 'username' not in session:
        return redirect(url_for('bp.login'))
    Produto.excluir(produto_id)
    LogAtividades.registrar(session['username'], "excluir_produto", f"Produto {produto_id} excluído.")
    return redirect(url_for('bp.admin'))

@bp.route('/carrinho')
def carrinho():
    if 'username' not in session:
        return redirect(url_for('bp.login'))
    username = session['username']
    itens = Carrinho.listar(username)
    return render_template('carrinho.html', itens=itens, username=username)

@bp.route('/adicionar_carrinho/<int:produto_id>', methods=['POST'])
def adicionar_carrinho(produto_id):
    if 'username' not in session:
        return redirect(url_for('bp.login'))
    username = session['username']
    quantity = int(request.form.get('quantity', 1))
    Carrinho.adicionar(username, produto_id, quantity)
    LogAtividades.registrar(username, "adicionar_carrinho", f"Produto {produto_id} adicionado ao carrinho.")
    return redirect(url_for('bp.carrinho'))

@bp.route('/remover_carrinho/<int:item_id>', methods=['POST'])
def remover_carrinho(item_id):
    if 'username' not in session:
        return redirect(url_for('bp.login'))
    Carrinho.remover(item_id)
    LogAtividades.registrar(session['username'], "remover_carrinho", f"Item {item_id} removido do carrinho.")
    return redirect(url_for('bp.carrinho'))

@bp.route('/finalizar_pedido')
def finalizar_pedido():
    if 'username' not in session:
        return redirect(url_for('bp.login'))
    username = session['username']
    pedido_id = Pedido.finalizar(username)
    if pedido_id:
        LogAtividades.registrar(username, "finalizar_pedido", f"Pedido {pedido_id} finalizado.")
        return redirect(url_for('bp.pedido_finalizado', pedido_id=pedido_id))
    else:
        flash("Seu carrinho está vazio! Adicione itens antes de finalizar o pedido.", "error")
        return redirect(url_for('bp.carrinho'))

@bp.route('/pedido_finalizado/<int:pedido_id>')
def pedido_finalizado(pedido_id):
    from models import DatabaseManager
    with DatabaseManager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT total FROM pedidos WHERE id = ?", (pedido_id,))
        pedido = cursor.fetchone()
    total = pedido[0] if pedido else 0
    return render_template('pedido_finalizado.html', pedido_id=pedido_id, total=total)

@bp.route('/avaliacoes')
def avaliacoes():
    from models import DatabaseManager
    with DatabaseManager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
           SELECT a.id, a.product_id, a.username, a.rating, a.comment, a.data, p.nome
           FROM avaliacoes a
           JOIN produtos p ON a.product_id = p.id
           ORDER BY a.data DESC
         """)
        avaliacoes_data = cursor.fetchall()
    return render_template('avaliacoes.html', avaliacoes=avaliacoes_data, username=session.get('username'))

@bp.route('/historico')
def historico():
    if 'username' not in session:
        return redirect(url_for('bp.login'))
    username = session['username']
    atividades = LogAtividades.listar(username)
    return render_template('historico.html', atividades=atividades, username=username)

@bp.route('/avaliar/<int:produto_id>', methods=['GET', 'POST'])
def avaliar_produto(produto_id):
    if 'username' not in session:
        return redirect(url_for('bp.login'))
    if request.method == 'POST':
        rating = int(request.form['rating'])
        comment = request.form['comment']
        Avaliacao.registrar(produto_id, session['username'], rating, comment)
        LogAtividades.registrar(session['username'], "avaliar_produto", f"Avaliação para produto {produto_id} registrada.")
        return redirect(url_for('bp.index'))
    avaliacoes_produto = Avaliacao.listar_por_produto(produto_id)
    return render_template('avaliar.html', produto_id=produto_id, avaliacoes=avaliacoes_produto, username=session['username'])
