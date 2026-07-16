from datetime import datetime

from database import db


# ==========================
# USUÁRIOS
# ==========================

class Usuario(db.Model):

    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    senha = db.Column(db.String(255), nullable=False)

    nivel = db.Column(db.String(30), default="admin")

    criado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# ==========================
# CLIENTES
# ==========================

class Cliente(db.Model):

    __tablename__ = "cliente"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(100), nullable=False)

    telefone = db.Column(db.String(30), nullable=False)

    email = db.Column(db.String(120))

    observacao = db.Column(db.Text)

    criado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# ==========================
# SERVIÇOS
# ==========================

class Servico(db.Model):

    __tablename__ = "servico"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(100), nullable=False)

    descricao = db.Column(db.Text)

    valor = db.Column(db.Float, default=0)

    duracao = db.Column(db.String(50))

    ativo = db.Column(db.Boolean, default=True)


# ==========================
# AGENDAMENTOS
# ==========================

class Agendamento(db.Model):

    __tablename__ = "agendamento"

    id = db.Column(db.Integer, primary_key=True)

    cliente = db.Column(db.String(100), nullable=False)

    telefone = db.Column(db.String(30))

    servico = db.Column(db.String(100))

    data = db.Column(db.String(20), nullable=False)

    horario = db.Column(db.String(10), nullable=False)

    status = db.Column(
        db.String(30),
        default="Pendente"
    )

    valor = db.Column(db.Float, default=0)

    pagamento = db.Column(db.String(30))

    observacao = db.Column(db.Text)

    criado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# ==========================
# ESTOQUE
# ==========================

class Estoque(db.Model):

    __tablename__ = "estoque"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    produto = db.Column(
        db.String(100),
        nullable=False
    )


    categoria = db.Column(
        db.String(100)
    )


    quantidade = db.Column(
        db.Integer,
        default=0
    )


    minimo = db.Column(
        db.Integer,
        default=0
    )


    valor = db.Column(
        db.Float,
        default=0
    )


    criado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

# ==========================
# CAIXA
# ==========================

class Caixa(db.Model):

    __tablename__ = "caixa"

    id = db.Column(db.Integer, primary_key=True)

    descricao = db.Column(db.String(200), nullable=False)

    tipo = db.Column(db.String(20))

    valor = db.Column(db.Float, default=0)

    categoria = db.Column(db.String(100))

    criado_em = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )