from flask import Blueprint, request, session, Response, current_app, jsonify
from .punchout_message import create_punchout_order_message

checkout = Blueprint('checkout', __name__)

@checkout.route('/checkout', methods=['POST'])
def checkout_route():
    return_url = session.get('return_url', '')
    buyer_cookie = session.get('buyer_cookie', '')
    current_app.logger.info(f"Checkout - Return URL: {return_url}, Buyer Cookie: {buyer_cookie}")
    current_app.logger.info(f"Session in Checkout: {dict(session)}")
    cart = session.get('cart', [])

    if not cart:
        return jsonify({'error': 'Cart is empty'}), 404

    order_details = create_punchout_order_message(buyer_cookie, cart)
    current_app.logger.info(f"Order Details: {order_details}")

    return Response(order_details, mimetype='application/xml', headers={'Content-Disposition': 'attachment; filename=order_details.xml'})

@checkout.route('/proceed_checkout', methods=['POST'])
def proceed_checkout():
    return_url = session.get('return_url', '')
    if return_url:
        current_app.logger.info(f"Redirecting to: {return_url}")
        return redirect(return_url)
    return jsonify({'message': 'Proceed to checkout successful'}), 200
