# importacao
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

# variavel para receber instancia da classe flask
app = Flask(__name__)
app.config['SECRET_KEY'] = "8SeYX1u8oU"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

login_manager = LoginManager()
# conexao
db = SQLAlchemy(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

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

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

#utilziando Usermixin que ja vai herdar metodos existentes
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    cart = db.relationship('CartItem', backref='user', lazy=True)

#Autenticacao
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# rota login
@app.route('/login', methods=["POST"])
def login():
    data = request.json
    
    user = User.query.filter_by(username=data.get("username")).first()

    if user:
        if user and data.get("password") == user.password:
            login_user(user)
            return jsonify({"message": "Logged in successfully"})
    
    return jsonify({"message": "Unauthorized. Invalid credentials"}), 401

#rota logout
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout in successfully"})

# add
@app.route('/api/products/add', methods=["POST"])
@login_required 
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
@login_required 
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
@login_required 
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


# Checkout
@app.route('/api/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    #info necessaria (user e product)
    user = User.query.get(int(current_user.id))
    product = Product.query.get(product_id)


    if user and product:
        return jsonify({'message': 'Item added to the cart successfully'}), 200
    return jsonify({'message': 'Failed to add item to the cart'}), 400



# Disponibilizando api para ser utilizada no modo debug
if __name__ == "__main__":
    app.run(debug=True)
