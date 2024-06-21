from flask import request, render_template, redirect, url_for, current_app, session
from lxml import etree
import xml.sax.saxutils as saxutils
from datetime import datetime
from . import main
from .utils import load_products
from .punchout_message import create_punchout_order_message

# Load products from JSON file
products = load_products('products.json')

# Function to extract values between specific tags
def extract_value(xml_str, start_tag, end_tag):
    """Extract the value between start_tag and end_tag in xml_str."""
    try:
        start_index = xml_str.index(start_tag) + len(start_tag)
        end_index = xml_str.index(end_tag, start_index)
        return xml_str[start_index:end_index].strip()
    except ValueError:
        return None

@main.route('/')
def index():
    return_url = session.get('return_url', '')
    current_app.logger.info(f"Index - Return URL: {return_url}")
    return render_template('index.html', return_url=return_url)

@main.route('/punchout', methods=['GET', 'POST'])
def punchout():
    if request.method == 'POST':
        incoming_data = request.data.decode('utf-8')
        current_app.logger.info(f"PunchOut - Incoming Data: {incoming_data}")

        buyer_cookie = extract_value(incoming_data, '<BuyerCookie>', '</BuyerCookie>')
        return_url = extract_value(incoming_data, '<BrowserFormPost><URL>', '</URL></BrowserFormPost>')

        if not return_url:
            current_app.logger.error("Failed to extract value for <BrowserFormPost><URL>")
        
        current_app.logger.info(f"PunchOut - Buyer Cookie: {buyer_cookie}")
        current_app.logger.info(f"PunchOut - Return URL: {return_url}")

        payload_id = saxutils.escape("2023-04-15T12:00:00-07:00")
        timestamp = saxutils.escape("2023-04-15T12:00:00-07:00")
        start_page_url = saxutils.escape(url_for('main.catalog', _external=True))

        punchout_setup_response = etree.Element("cXML", payloadID=payload_id, timestamp=timestamp)
        response = etree.SubElement(punchout_setup_response, "Response")
        status = etree.SubElement(response, "Status", code="200", text="OK")
        status.text = "Success"
        punchout_setup_response_elem = etree.SubElement(response, "PunchOutSetupResponse")
        start_page = etree.SubElement(punchout_setup_response_elem, "StartPage")
        url_elem = etree.SubElement(start_page, "URL")
        url_elem.text = start_page_url

        response_xml = etree.tostring(punchout_setup_response, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode()
        current_app.logger.info(f"PunchOut Setup Response: {response_xml}")

        # Store session data
        session['buyer_cookie'] = buyer_cookie
        session['return_url'] = return_url

        return response_xml

    return render_template('product_details.html', product=products[0], return_url=session.get('return_url', ''))

@main.route('/catalog')
def catalog():
    return_url = session.get('return_url', '')
    buyer_cookie = session.get('buyer_cookie', '')
    current_app.logger.info(f"Catalog - Return URL: {return_url}, Buyer Cookie: {buyer_cookie}")

    # Retrieve product list from in-memory storage
    return render_template('catalog.html', products=products, return_url=return_url, buyer_cookie=buyer_cookie)

@main.route('/product', methods=['GET', 'POST'])
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
            "manufacturer_name": "Sample Manufacturer",
            "sold_by": "Our Company",
            "fulfilled_by": "Our Company",
            "category": "GENERAL",
            "sub_category": "GENERAL_ITEMS",
            "item_condition": "New",
            "qualified_offer": "true",
            "upc": "UPC-123456789012",
            "detail_page_url": f"https://example.com/product/{request.form['id']}",
            "ean": "1234567890123",
            "preference": "default"
        }
        current_app.db.products.insert_one(product_data)
        return redirect(url_for('main.catalog'))

    return render_template('create_product.html')

@main.route('/checkout', methods=['POST'])
def checkout():
    try:
        product_id = request.form.get('product_id')

        # Fetch buyer_cookie and return_url from the session
        buyer_cookie = session.get('buyer_cookie')
        return_url = session.get('return_url')

        if not buyer_cookie or not return_url:
            current_app.logger.error("Buyer cookie or return URL not found in session")
            return "Buyer cookie or return URL not found", 400

        current_app.logger.info(f"Checkout - Return URL: {return_url}, Buyer Cookie: {buyer_cookie}")

        product = current_app.db.products.find_one({'id': product_id})
        if not product:
            current_app.logger.error("Product not found")
            return "Product not found", 404

        order_details = create_punchout_order_message(buyer_cookie, [product])
        current_app.logger.info(f"Order Details: {order_details}")

        response = redirect(return_url)
        response.headers['buyer_cookie'] = buyer_cookie
        current_app.logger.info(f"Redirecting to: {response.location}")

        return response
    except Exception as e:
        current_app.logger.error(f"Error in checkout route: {str(e)}")
        return str(e), 500
