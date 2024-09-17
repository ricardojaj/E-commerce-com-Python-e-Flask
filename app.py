# importacao
from flask import Flask, request, jsonify
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

# add
@app.route('/api/products/add', methods=["POST"])
def add_product():
    #variavel para receber dados da minha requisicao
    data = request.json
    if 'name' in data and 'price' in data:
        #criar produto e salvar no db
        product = Produto(name=data["name"], price=data["price"], description=data.get("description", ""))
        db.session.add(product)
        db.session.commit()
        return "Product successfully registered."
    return jsonify({"message": "Invalid product data"}), 400


# delete
@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
def delete_product(product_id):
    #recuperar product na base
    # condicao para verificar se o produto realmente existe
    product = Produto.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify ({"message": "Product deleted successfully."})
    return jsonify({"message": "Product not found"}), 404

#detalhes produto
@app.route('/api/products/<int:product_id>', methods=["GET"])
def get_product_details(product_id):
    product = Produto.query.get(product_id)
    if product:
        return jsonify({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description
            })
    return jsonify({"message": "Product not found"}), 404



# Definindo uma rota raiz (page inicial) e a funcao que sera executada ao ser requisitada pelo user
@app.route('/teste')
def hello_world():
    return 'Hello World'

# Disponibilizando api para ser utilizada no modo debug
if __name__ == "__main__":
    app.run(debug=True)
