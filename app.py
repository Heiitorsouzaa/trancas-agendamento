import os
import shutil

from datetime import datetime, timedelta

from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database import db

from models import (
    Usuario,
    Cliente,
    Servico,
    Agendamento,
    Estoque,
    Caixa
)


# ==========================
# CRIAÇÃO APP
# ==========================

app = Flask(__name__)


# ==========================
# CONFIGURAÇÕES
# ==========================

app.config["SECRET_KEY"] = "Trancas@2026"

database_url = os.environ.get(
    "DATABASE_URL",
    "sqlite:///trancas.db"
)

if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://",
        "postgresql://",
        1
    )


app.config["SQLALCHEMY_DATABASE_URI"] = database_url

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


app.permanent_session_lifetime = timedelta(
    hours=1
)


db.init_app(app)



# ==========================
# MODELOS
# ==========================

from models import (
    Usuario,
    Cliente,
    Servico,
    Agendamento,
    Caixa,
    Estoque
)



# ==========================
# HORÁRIOS
# ==========================

HORARIOS = [

    "08:00",
    "09:00",
    "10:00",
    "11:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00",
    "17:00"

]



# ==========================
# BACKUP
# ==========================

def fazer_backup():

    origem = os.path.join(
        "instance",
        "trancas.db"
    )


    pasta = "backup"


    os.makedirs(
        pasta,
        exist_ok=True
    )


    if os.path.exists(origem):

        destino = os.path.join(

            pasta,

            f"trancas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

        )


        shutil.copy2(
            origem,
            destino
        )



# ==========================
# LOGIN REQUIRED
# ==========================

def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "usuario_id" not in session:

            flash(
                "Faça login para acessar.",
                "warning"
            )

            return redirect(
                url_for("login")
            )


        return func(*args, **kwargs)


    return wrapper

    # ==========================
# HOME
# ==========================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )



# ==========================
# LOGIN
# ==========================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form["email"].strip()

        senha = request.form["senha"]


        usuario = Usuario.query.filter_by(
            email=email
        ).first()



        if usuario and check_password_hash(
            usuario.senha,
            senha
        ):

            session.permanent = True

            session["usuario_id"] = usuario.id

            session["usuario_nome"] = usuario.nome


            flash(
                "Login realizado com sucesso!",
                "success"
            )


            return redirect(
                url_for("admin")
            )



        flash(
            "Email ou senha incorretos.",
            "danger"
        )


    return render_template(
        "login.html"
    )



# ==========================
# LOGOUT
# ==========================

@app.route("/logout")
def logout():

    session.clear()


    flash(
        "Você saiu do sistema.",
        "info"
    )


    return redirect(
        url_for("login")
    )



# ==========================
# PAINEL ADMIN
# ==========================

@app.route("/admin")
@login_required
def admin():

    total_clientes = Cliente.query.count()

    total_agendamentos = Agendamento.query.count()

    total_servicos = Servico.query.count()

    total_estoque = Estoque.query.count()



    entradas = db.session.query(
        db.func.sum(Caixa.valor)
    ).filter(
        Caixa.tipo == "Entrada"
    ).scalar() or 0



    saidas = db.session.query(
        db.func.sum(Caixa.valor)
    ).filter(
        Caixa.tipo == "Saida"
    ).scalar() or 0



    saldo = entradas - saidas



    return render_template(

        "admin.html",

        clientes=total_clientes,

        agendamentos=total_agendamentos,

        servicos=total_servicos,

        estoque=total_estoque,

        saldo=saldo

    )

    # ==========================
# AGENDAMENTO
# ==========================


@app.route(
    "/agendamento",
    methods=["GET", "POST"]
)
def agendamento():


    if request.method == "POST":


        cliente = request.form["cliente"]

        telefone = request.form["telefone"]

        servico = request.form["servico"]

        data = request.form["data"]

        horario = request.form["horario"]



        # verifica horário ocupado

        ocupado = Agendamento.query.filter_by(
            data=data,
            horario=horario
        ).first()



        if ocupado:

            flash(
                "Esse horário já está ocupado.",
                "danger"
            )

            return redirect(
                url_for("agendamento")
            )



        novo = Agendamento(

            cliente=cliente,

            telefone=telefone,

            servico=servico,

            data=data,

            horario=horario,

            status="Pendente"

        )



        db.session.add(novo)

        db.session.commit()



        flash(
            "Agendamento realizado!",
            "success"
        )


        return redirect(
            url_for("index")
        )



    return render_template(

        "agendamento.html",

        horarios=HORARIOS

    )





# ==========================
# CLIENTES
# ==========================


@app.route("/clientes")
@login_required
def clientes():


    lista = Cliente.query.order_by(
        Cliente.id.desc()
    ).all()



    return render_template(

        "clientes.html",

        clientes=lista

    )




@app.route(
    "/clientes/cadastrar",
    methods=["POST"]
)
@login_required
def cadastrar_cliente():


    cliente = Cliente(

        nome=request.form["nome"],

        telefone=request.form["telefone"],

        email=request.form.get("email"),

        observacao=request.form.get(
            "observacao"
        )

    )



    db.session.add(cliente)

    db.session.commit()



    flash(
        "Cliente cadastrado!",
        "success"
    )


    return redirect(
        url_for("clientes")
    )





@app.route(
    "/clientes/excluir/<int:id>"
)
@login_required
def excluir_cliente(id):


    cliente = Cliente.query.get_or_404(id)



    db.session.delete(cliente)

    db.session.commit()



    flash(
        "Cliente removido!",
        "success"
    )



    return redirect(
        url_for("clientes")
    )

    # ==========================
# SERVIÇOS
# ==========================


@app.route("/servicos")
@login_required
def servicos():

    lista = Servico.query.order_by(
        Servico.id.desc()
    ).all()


    return render_template(
        "servicos.html",
        servicos=lista
    )



@app.route(
    "/servicos/cadastrar",
    methods=["POST"]
)
@login_required
def cadastrar_servico():


    novo = Servico(

        nome=request.form["nome"],

        descricao=request.form.get(
            "descricao"
        ),

        valor=float(
            request.form["valor"]
        ),

        duracao=request.form.get(
            "duracao"
        )

    )


    db.session.add(novo)

    db.session.commit()


    flash(
        "Serviço cadastrado!",
        "success"
    )


    return redirect(
        url_for("servicos")
    )




@app.route(
    "/servicos/excluir/<int:id>"
)
@login_required
def excluir_servico(id):

    servico = Servico.query.get_or_404(id)


    db.session.delete(servico)

    db.session.commit()


    flash(
        "Serviço excluído!",
        "success"
    )


    return redirect(
        url_for("servicos")
    )




# ==========================
# ESTOQUE
# ==========================


@app.route("/estoque")
@login_required
def estoque():

    produtos = Estoque.query.order_by(
        Estoque.id.desc()
    ).all()

    return render_template(
        "estoque.html",
        produtos=produtos
    )


@app.route(
    "/estoque/cadastrar",
    methods=["POST"]
)
@login_required
def cadastrar_estoque():


    produto = Estoque(

        produto=request.form["produto"],

        categoria=request.form.get(
            "categoria"
        ),

        quantidade=int(
            request.form["quantidade"]
        ),

        valor=float(
            request.form["valor"]
        )

    )


    db.session.add(produto)

    db.session.commit()



    flash(
        "Produto cadastrado!",
        "success"
    )



    return redirect(
        url_for("estoque")
    )





@app.route(
    "/estoque/excluir/<int:id>"
)
@login_required
def excluir_estoque(id):


    produto = Estoque.query.get_or_404(id)



    db.session.delete(produto)

    db.session.commit()



    flash(
        "Produto removido!",
        "success"
    )



    return redirect(
        url_for("estoque")
    )





@app.route(
    "/estoque/editar/<int:id>",
    methods=["GET","POST"]
)
@login_required
def editar_estoque(id):


    produto = Estoque.query.get_or_404(id)



    if request.method == "POST":


        produto.produto = request.form["produto"]


        produto.categoria = request.form.get(
            "categoria"
        )


        produto.quantidade = int(
            request.form["quantidade"]
        )


        produto.valor = float(
            request.form["valor"]
        )


        db.session.commit()



        flash(
            "Produto atualizado!",
            "success"
        )



        return redirect(
            url_for("estoque")
        )



    return render_template(

        "editar_estoque.html",

        produto=produto

    )

    # ==========================
# CAIXA
# ==========================


@app.route("/caixa")
@login_required
def caixa():


    registros = Caixa.query.order_by(
        Caixa.id.desc()
    ).all()



    total = 0



    for item in registros:

        if item.tipo == "Entrada":

            total += item.valor


        elif item.tipo == "Saida":

            total -= item.valor




    return render_template(

        "caixa.html",

        registros=registros,

        total=total

    )





@app.route(
    "/caixa/cadastrar",
    methods=["POST"]
)
@login_required
def cadastrar_caixa():


    movimento = Caixa(

        descricao=request.form["descricao"],

        tipo=request.form["tipo"],

        valor=float(
            request.form["valor"]
        ),

        categoria=request.form.get(
            "categoria"
        )

    )



    db.session.add(movimento)

    db.session.commit()



    flash(
        "Movimentação registrada!",
        "success"
    )



    return redirect(
        url_for("caixa")
    )





# ==========================
# CRIAR ADMIN PADRÃO
# ==========================


def criar_admin():


    usuario = Usuario.query.filter_by(
        email="admin@trancas.com"
    ).first()



    if not usuario:


        novo = Usuario(

            nome="Administrador",

            email="admin@trancas.com",

            senha=generate_password_hash(
                "Admin@2026"
            ),

            nivel="admin"

        )



        db.session.add(novo)

        db.session.commit()





# ==========================
# CRIAÇÃO DAS TABELAS
# ==========================


with app.app_context():

    db.create_all()

    criar_admin()



if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )