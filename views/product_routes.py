from flask import Blueprint, request, redirect, url_for, render_template, session
from .utils import load_products

product = Blueprint('product', __name__)
products = load_products('products.json')

@product.route('/product', methods=['GET', 'POST'])
def create_product():
    if request.method == 'POST':
        product_data = {
            "id": request.form['id'],
            "name": request.form['name'],
            "description": request.form['description'],
            "price": request.form['price'],
            "image": request.form['image'],
            "unit_price": request.form['price'],
            "unit_of_measure": "EA",
            "classification": "601210",
            "manufacturer_part_id": request.form['id'],
            "manufacturer_name": "Sreejith",
            "sold_by": "Our Company",
            "fulfilled_by": "Our Company",
            "category": "GENERAL",
            "sub_category": "GENERAL_ITEMS",
            "item_condition": "New",
            "qualified_offer": "true",
            "upc": "UPC-123456789012",
            "detail_page_url": f"https://punchout-nxnr.onrender.com/product/{request.form['id']}",
            "ean": "1234567890123",
            "preference": "default"
        }
        products.append(product_data)
        return redirect(url_for('product.catalog'))

    return render_template('create_product.html')

@product.route('/catalog')
def catalog():
    return_url = session.get('return_url', '')
    buyer_cookie = session.get('buyer_cookie', '')
    current_app.logger.info(f"Catalog - Return URL: {return_url}, Buyer Cookie: {buyer_cookie}")

    return render_template('catalog.html', products=products, return_url=return_url, buyer_cookie=buyer_cookie)
