import os
import shutil
from datetime import datetime, date

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify
)

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# ==========================
# CONFIGURAÇÃO
# ==========================

app = Flask(__name__)

app.config["SECRET_KEY"] = "Trancas@2026_SistemaSeguro#91"

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///trancas.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)



# ==========================
# CONFIGURAÇÕES DO SISTEMA
# ==========================


HORARIOS = [

    "08:00",
    "09:00",
    "10:00",
    "11:00",
    "12:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00",
    "17:00"

]


UPLOAD_FOLDER = "static/uploads"


os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# ==========================
# BACKUP AUTOMÁTICO
# ==========================


def fazer_backup():

    banco = "instance/trancas.db"


    if os.path.exists(banco):

        os.makedirs(
            "backups",
            exist_ok=True
        )


        data_backup = datetime.now().strftime(
            "%d-%m-%Y_%H-%M"
        )


        shutil.copy(
            banco,
            f"backups/trancas_{data_backup}.db"
        )


class Caixa(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    cliente = db.Column(
        db.String(100),
        nullable=False
    )

    servico = db.Column(
        db.String(100),
        nullable=False
    )

    valor = db.Column(
        db.Float,
        nullable=False
    )

    pagamento = db.Column(
        db.String(50),
        nullable=False
    )

    data = db.Column(
        db.String(20),
        nullable=False
    )

    horario = db.Column(
        db.String(20)
    )

    observacao = db.Column(
        db.String(200)
    )


# ==========================
# MODELOS DO BANCO
# ==========================


class Cliente(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    nome = db.Column(
        db.String(100),
        nullable=False
    )


    telefone = db.Column(
        db.String(30)
    )



class Servico(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    nome = db.Column(
        db.String(100),
        nullable=False
    )


    preco = db.Column(
        db.Float,
        nullable=False
    )



class Funcionario(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    nome = db.Column(
        db.String(100),
        nullable=False
    )


    telefone = db.Column(
        db.String(30)
    )


    especialidade = db.Column(
        db.String(100)
    )



class Agendamento(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    cliente = db.Column(
        db.String(100),
        nullable=False
    )


    telefone = db.Column(
        db.String(30)
    )


    servico = db.Column(
        db.String(100)
    )


    data = db.Column(
        db.String(20)
    )


    horario = db.Column(
        db.String(20)
    )


    status = db.Column(
        db.String(30),
        default="Pendente"
    )


class Foto(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    nome = db.Column(
        db.String(100)
    )


    imagem = db.Column(
        db.String(200)
    )



class Usuario(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    usuario = db.Column(
        db.String(50),
        unique=True
    )


    senha = db.Column(
        db.String(200)
    )

    # ==========================
# CRIAÇÃO DO BANCO
# ==========================

with app.app_context():

    db.create_all()

    if not Usuario.query.first():

        admin = Usuario(
            usuario="admin",
            senha=generate_password_hash("Admin@2026")
        )

        db.session.add(admin)


    # serviços iniciais

    if not Servico.query.first():

        servicos = [

            Servico(
                nome="Box Braids",
                preco=220
            ),

            Servico(
                nome="Nagô (a partir)",
                preco=25
            ),

            Servico(
                nome="Nagô Lateral (a partir)",
                preco=20
            ),

            Servico(
                nome="Twist",
                preco=200
            ),

            Servico(
                nome="Entrelace",
                preco=250
            ),

            Servico(
                nome="Gypsy Braids",
                preco=300
            ),

            Servico(
                nome="Goddess Braids",
                preco=250
            ),

            Servico(
                nome="Boho Braids",
                preco=280
            ),

            Servico(
                nome="Faux Locs",
                preco=350
            ),

            Servico(
                nome="Manutenção de Tranças (a definir)",
                preco=0
            )

        ]

        db.session.add_all(servicos)


    db.session.commit()

# ==========================
# PÁGINA INICIAL
# ==========================


@app.route("/")
def index():

    fotos = Foto.query.all()

    servicos = Servico.query.all()


    return render_template(
        "index.html",
        fotos=fotos,
        servicos=servicos
    )



# ==========================
# AGENDAMENTO DO CLIENTE
# ==========================


@app.route(
    "/agendamento",
    methods=["GET", "POST"]
)
def agendamento():

    servicos = Servico.query.all()

    data_escolhida = request.form.get("data")


    horarios_disponiveis = HORARIOS.copy()


    if data_escolhida:

        agendamentos = Agendamento.query.filter_by(
            data=data_escolhida
        ).all()


        for ag in agendamentos:

            if ag.horario in horarios_disponiveis:

                horarios_disponiveis.remove(
                    ag.horario
                )


    if request.method == "POST":


        nome = request.form["nome"]

        telefone = request.form["telefone"]

        servico = request.form["servico"]

        data = request.form["data"]

        horario = request.form["horario"]



        # verifica se horário já existe

        horario_existente = Agendamento.query.filter_by(
            data=data,
            horario=horario
        ).first()


        if horario_existente:

            flash(
                "Este horário já está ocupado!"
            )

            return redirect(
                url_for("agendamento")
            )



        novo = Agendamento(

            cliente=nome,

            telefone=telefone,

            servico=servico,

            data=data,

            horario=horario

        )


        db.session.add(novo)



        cliente_existente = Cliente.query.filter_by(
            telefone=telefone
        ).first()



        if not cliente_existente:


            cliente = Cliente(

                nome=nome,

                telefone=telefone

            )


            db.session.add(cliente)



        db.session.commit()



        flash(
            "Agendamento realizado com sucesso!"
        )


        return redirect(
            url_for("agendamento")
        )



    return render_template(

        "agendamento.html",

        servicos=servicos,

        horarios=horarios_disponiveis

    )

    # ==========================
# LOGIN ADMIN
# ==========================


@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():


    if request.method == "POST":


        usuario = request.form["usuario"]

        senha = request.form["senha"]



        admin = Usuario.query.filter_by(
            usuario=usuario
        ).first()



        if admin and check_password_hash(
            admin.senha,
            senha
        ):


            session["admin"] = True


            flash(
                "Login realizado com sucesso!"
            )


            return redirect(
                url_for("admin")
            )


        else:

            flash(
                "Usuário ou senha incorretos!"
            )



    return render_template(
        "login.html"
    )





# ==========================
# SAIR DO ADMIN
# ==========================


@app.route("/logout")
def logout():


    session.pop(
        "admin",
        None
    )


    return redirect(
        url_for("login")
    )





# ==========================
# PAINEL ADMIN
# ==========================


@app.route("/admin")
def admin():

    if not session.get("admin"):
        return redirect(url_for("login"))

    agendamentos = Agendamento.query.all()

    total = len(agendamentos)
    clientes_total = Cliente.query.count()
    funcionarios_total = Funcionario.query.count()

    faturamento = 0
    servicos_count = {}
    eventos = []

    for ag in agendamentos:

        servicos_count[ag.servico] = (
            servicos_count.get(ag.servico, 0) + 1
        )

        eventos.append({

            "title": ag.cliente + " - " + ag.servico,

            "start": ag.data + "T" + ag.horario

        })

        servico = Servico.query.filter_by(
            nome=ag.servico
        ).first()

        if servico:
            faturamento += servico.preco

    labels = list(servicos_count.keys())

    grafico_valores = list(servicos_count.values())

    meses = [
        "Jan", "Fev", "Mar", "Abr",
        "Mai", "Jun", "Jul", "Ago",
        "Set", "Out", "Nov", "Dez"
    ]

    valores = [0] * 12

    for item in Caixa.query.all():

        try:

            mes = int(item.data.split("-")[1]) - 1

            valores[mes] += item.valor

        except:
            pass

    return render_template(

        "admin/index.html",

        total=total,

        clientes_total=clientes_total,

        funcionarios_total=funcionarios_total,

        faturamento=faturamento,

        agendamentos=agendamentos,

        eventos=eventos,

        labels=labels,

        grafico_valores=grafico_valores,

        meses=meses,

        valores=valores

    )




# ==========================
# FUNCIONÁRIOS
# ==========================


@app.route(
    "/funcionarios",
    methods=["GET", "POST"]
)
def funcionarios():

    if not session.get("admin"):
        return redirect(url_for("login"))

    if request.method == "POST":

        funcionario = Funcionario(

            nome=request.form["nome"],

            telefone=request.form["telefone"],

            especialidade=request.form["especialidade"]

        )

        db.session.add(funcionario)
        db.session.commit()

        flash("Funcionário cadastrado!")

    lista = Funcionario.query.all()

    return render_template(

        "admin/funcionarios.html",

        funcionarios=lista

    )


@app.route("/excluir-funcionario/<int:id>")
def excluir_funcionario(id):

    if not session.get("admin"):
        return redirect(url_for("login"))

    funcionario = Funcionario.query.get_or_404(id)

    db.session.delete(funcionario)
    db.session.commit()

    flash("Funcionário excluído com sucesso!")

    return redirect(url_for("funcionarios"))

    # ==========================
# SERVIÇOS
# ==========================


@app.route(
    "/servicos",
    methods=["GET", "POST"]
)
def servicos():


    if not session.get("admin"):

        return redirect(
            url_for("login")
        )



    if request.method == "POST":


        novo_servico = Servico(

            nome=request.form["nome"],

            preco=float(
                request.form["preco"]
            )

        )


        db.session.add(novo_servico)

        db.session.commit()



        flash(
            "Serviço cadastrado!"
        )



    lista = Servico.query.all()



    return render_template(

        "admin/servicos.html",

        servicos=lista

    )





# ==========================
# FOTOS / GALERIA
# ==========================


@app.route(
    "/fotos",
    methods=["GET", "POST"]
)
def fotos():


    if not session.get("admin"):

        return redirect(
            url_for("login")
        )



    if request.method == "POST":


        arquivo = request.files["imagem"]


        nome = request.form["nome"]



        if arquivo:


            caminho = os.path.join(

                UPLOAD_FOLDER,

                arquivo.filename

            )


            arquivo.save(caminho)



            foto = Foto(

                nome=nome,

                imagem=arquivo.filename

            )


            db.session.add(foto)

            db.session.commit()



            flash(
                "Foto adicionada!"
            )



    lista = Foto.query.all()



    return render_template(

        "admin/fotos.html",

        fotos=lista

    )





# ==========================
# EXCLUIR FOTO
# ==========================


@app.route(
    "/excluir-foto/<int:id>"
)
def excluir_foto(id):


    if not session.get("admin"):

        return redirect(
            url_for("login")
        )



    foto = Foto.query.get_or_404(id)



    caminho = os.path.join(

        UPLOAD_FOLDER,

        foto.imagem

    )



    if os.path.exists(caminho):

        os.remove(caminho)



    db.session.delete(foto)

    db.session.commit()



    flash(
        "Foto removida!"
    )


    return redirect(
        url_for("fotos")
    )





# ==========================
# RELATÓRIO
# ==========================


@app.route("/relatorio")
def relatorio():


    if not session.get("admin"):

        return redirect(
            url_for("login")
        )



    total = Agendamento.query.count()


    clientes_total = Cliente.query.count()


    funcionarios_total = Funcionario.query.count()



    faturamento = 0


    servicos = {}



    agendamentos = Agendamento.query.all()



    for ag in agendamentos:


        servicos[ag.servico] = (
            servicos.get(ag.servico, 0) + 1
        )



        servico = Servico.query.filter_by(
            nome=ag.servico
        ).first()



        if servico:

            faturamento += servico.preco



    return render_template(

        "admin/relatorio.html",

        total=total,

        clientes_total=clientes_total,

        funcionarios_total=funcionarios_total,

        faturamento=faturamento,

        servicos=servicos

    )

    # ==========================
# EXCLUIR AGENDAMENTO
# ==========================


@app.route(
    "/excluir/<int:id>"
)
def excluir_agendamento(id):


    if not session.get("admin"):

        return redirect(
            url_for("login")
        )


    agendamento = Agendamento.query.get_or_404(id)


    db.session.delete(
        agendamento
    )


    db.session.commit()


    flash(
        "Agendamento excluído!"
    )


    return redirect(
        url_for("admin")
    )    


# ==========================
# EDITAR AGENDAMENTO
# ==========================


@app.route(
    "/editar/<int:id>",
    methods=["GET", "POST"]
)
def editar(id):


    if not session.get("admin"):

        return redirect(
            url_for("login")
        )


    agendamento = Agendamento.query.get_or_404(id)



    if request.method == "POST":


        agendamento.cliente = request.form["nome"]

        agendamento.telefone = request.form["telefone"]

        agendamento.servico = request.form["servico"]

        agendamento.data = request.form["data"]

        agendamento.horario = request.form["horario"]



        db.session.commit()



        flash(
            "Agendamento atualizado!"
        )


        return redirect(
            url_for("admin")
        )



    servicos = Servico.query.all()



    return render_template(

        "admin/editar.html",

        agendamento=agendamento,

        servicos=servicos,

        horarios=HORARIOS

    )





# ==========================
# INICIALIZAÇÃO
# ==========================
@app.route(
    "/status/<int:id>/<novo>"
)
def alterar_status(id, novo):

    if not session.get("admin"):
        return redirect(url_for("login"))

    agendamento = Agendamento.query.get_or_404(id)

    agendamento.status = novo

    db.session.commit()

    return redirect(url_for("admin"))


@app.route("/receber/<int:id>")
def receber(id):

    if not session.get("admin"):
        return redirect(url_for("login"))

    ag = Agendamento.query.get_or_404(id)

    servico = Servico.query.filter_by(
        nome=ag.servico
    ).first()

    if not servico:

        flash("Serviço não encontrado.")

        return redirect(url_for("admin"))

    existente = Caixa.query.filter_by(

        cliente=ag.cliente,

        servico=ag.servico,

        data=ag.data

    ).first()

    if existente:

        flash("Esse atendimento já foi registrado no caixa.")

        return redirect(url_for("admin"))

    novo_caixa = Caixa(

        cliente=ag.cliente,

        servico=ag.servico,

        valor=servico.preco,

        pagamento="PIX",

        data=ag.data,

        horario=ag.horario,

        observacao="Pagamento do agendamento"

    )

    db.session.add(novo_caixa)

    db.session.commit()

    flash("Pagamento registrado com sucesso!")

    return redirect(url_for("admin"))

@app.route("/api/agendamentos")
def api_agendamentos():

    agendamentos = Agendamento.query.all()

    eventos = []


    for ag in agendamentos:

        eventos.append({

            "id": ag.id,

            "title": ag.cliente + " - " + ag.servico,

            "start": ag.data + "T" + ag.horario,


            "cliente": ag.cliente,

            "telefone": ag.telefone,

            "servico": ag.servico,

            "data": ag.data,

            "horario": ag.horario,

            "status": ag.status

        })


    return jsonify(eventos)

@app.route("/whatsapp/<int:id>")
def whatsapp(id):

    if not session.get("admin"):
        return redirect(url_for("login"))

    ag = Agendamento.query.get_or_404(id)

    telefone = (
        ag.telefone
        .replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
    )

    mensagem = (
        f"Olá {ag.cliente}! "
        f"Seu agendamento para {ag.servico} "
        f"está marcado para o dia {ag.data} às {ag.horario}. "
        f"Aguardamos você! 😊"
    )

    from urllib.parse import quote

    return redirect(
        f"https://wa.me/55{telefone}?text={quote(mensagem)}"
    )


@app.route(
    "/estoque",
    methods=["GET", "POST"]
)
def estoque():

    if not session.get("admin"):
        return redirect(url_for("login"))

    if request.method == "POST":

        produto = Estoque(
            produto=request.form["produto"],
            quantidade=int(request.form["quantidade"]),
            minimo=int(request.form["minimo"]),
            valor=float(request.form["valor"])
        )

        db.session.add(produto)
        db.session.commit()

        flash("Produto cadastrado com sucesso!")

        return redirect(url_for("estoque"))

    produtos = Estoque.query.all()

    return render_template(
        "admin/estoque.html",
        produtos=produtos
    )

class Estoque(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    produto = db.Column(
        db.String(100),
        nullable=False
    )

    quantidade = db.Column(
        db.Integer,
        nullable=False
    )

    minimo = db.Column(
        db.Integer,
        nullable=False
    )

    valor = db.Column(
        db.Float,
        nullable=False
    )

# ==========================
# INICIALIZAÇÃO
# ==========================

# ==========================
# CAIXA
# ==========================

@app.route("/caixa")
def caixa():

    if not session.get("admin"):
        return redirect(url_for("login"))

    registros = Caixa.query.all()

    total = sum(
        item.valor for item in registros
    )

    return render_template(
        "admin/caixa.html",
        registros=registros,
        total=total
    )

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )