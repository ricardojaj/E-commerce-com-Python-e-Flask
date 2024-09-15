# importacao
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

# variavel para receber instancia da classe flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

# conexao
db = SQLAlchemy(app)

# Modelagem
# Produto (id, name, price, description)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)


@app.route('/api/products/add', methods=["POST"])
def add_product():
    #variavel para receber dados da minha requisicao
    data = request.json
    #criar produto e salvar no db
    product = Produto(name=data["name"], price=data["price"], description=data.get("description", ""))
    db.session.add(product)
    db.session.commit()
    return "Product successfully registered."

# Definindo uma rota raiz (page inicial) e a funcao que sera executada ao ser requisitada pelo user
@app.route('/teste')
def hello_world():
    return 'Hello World'

# Disponibilizando api para ser utilizada no modo debug
if __name__ == "__main__":
    app.run(debug=True)
