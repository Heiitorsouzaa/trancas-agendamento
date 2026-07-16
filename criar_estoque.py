from app import app
from database import db
from models import Estoque


with app.app_context():

    db.create_all()

    print("Tabela estoque criada!")