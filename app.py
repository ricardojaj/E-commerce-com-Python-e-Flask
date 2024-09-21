# importacao
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin

# variavel para receber instancia da classe flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

# conexao
db = SQLAlchemy(app)

#config para permitir que outros sistemas acesse o meu sistema
#com essa config consegui executar os endpoints no Swagger Editor
CORS(app)

# Modelagem
# Produto (id, name, price, description)
# User (id,username, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

#utilziando Usermixin que ja vai herdar metodos existentes
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


# add
@app.route('/api/products/add', methods=["POST"])
def add_product():
    #variavel para receber dados da minha requisicao
    data = request.json
    if 'name' in data and 'price' in data:
        #criar produto e salvar no db
        product = Product(name=data["name"], price=data["price"], description=data.get("description", ""))
        db.session.add(product)
        db.session.commit()
        return "Product successfully registered."
    return jsonify({"message": "Invalid product data"}), 400


# delete
@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
def delete_product(product_id):
    #recuperar product na base
    # condicao para verificar se o produto realmente existe
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify ({"message": "Product deleted successfully."})
    return jsonify({"message": "Product not found"}), 404

#detalhes produto
@app.route('/api/products/<int:product_id>', methods=["GET"])
def get_product_details(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description
            })
    return jsonify({"message": "Product not found"}), 404

#Visualize all products
@app.route('/api/products', methods=["GET"])
def get_all_products():
    products = Product.query.all()
    product_list = []
    for product in products:
        product_data = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description
        }

        #adicionando informacoes do produto na lista
        product_list.append(product_data)
    
    return jsonify(product_list)
        
    
#update product
@app.route('/api/products/update/<int:product_id>', methods=["PUT"])
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404
    #se passar pelo codigo acima, significa que o produto realmente existe
    
    data = request.json
    if 'name' in data:
        product.name = data['name']
    
    if 'price' in data:
        product.price = data['price']

    if 'description' in data:
        product.description = data['description']

    #salvar informacoes atualizadas
    db.session.commit()

    return jsonify({'message': 'Product updated susuccessfully'}), 200


# rota login
@app.route('/login', methods=["POST"])
def login():
    data = request.json
    
    user = User.query.filter_by(username=data.get("username")).first()

    if user:
        if user and data.get("password") == user.password:
            return jsonify({"message": "Logged in successfully"})
    
    return jsonify({"message": "Unauthorized. Invalid credentials"}), 401
    

# Definindo uma rota raiz (page inicial) e a funcao que sera executada ao ser requisitada pelo user
@app.route('/teste')
def hello_world():
    return 'Hello World'

# Disponibilizando api para ser utilizada no modo debug
if __name__ == "__main__":
    app.run(debug=True)
