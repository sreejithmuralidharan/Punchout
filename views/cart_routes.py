from flask import Blueprint, request, redirect, url_for, jsonify, session, render_template, current_app

cart_blueprint = Blueprint('cart', __name__)

@cart_blueprint.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    product = next((p for p in products if p['id'] == product_id), None)

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    cart = session.get('cart', [])
    cart.append(product)
    session['cart'] = cart

    current_app.logger.info(f"Added to cart: {product['name']}")
    current_app.logger.info(f"Cart: {session['cart']}")
    current_app.logger.info(f"Session after adding to cart: {dict(session)}")

    return redirect(url_for('product.catalog', return_url=session.get('return_url', ''), buyer_cookie=session.get('buyer_cookie', '')))

@cart_blueprint.route('/cart')
def cart():
    cart = session.get('cart', [])
    return_url = session.get('return_url', '')
    buyer_cookie = session.get('buyer_cookie', '')
    current_app.logger.info(f"Cart: {cart}")
    current_app.logger.info(f"Session in Cart: {dict(session)}")
    return render_template('cart.html', cart=cart, return_url=return_url, buyer_cookie=buyer_cookie)
