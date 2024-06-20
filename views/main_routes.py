from flask import request, render_template, redirect, url_for, current_app, jsonify
from lxml import etree
import xml.sax.saxutils as saxutils
from datetime import datetime
from . import main
from .utils import load_products

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

# Create cXML PunchOutOrderMessage
def create_punchout_order_message(buyer_cookie, product):
    cxml = etree.Element("cXML", payloadID="2023-04-15T12:00:00-07:00", timestamp="2023-04-15T12:00:00-07:00")

    message = etree.SubElement(cxml, "Message")
    punchout_order_message = etree.SubElement(message, "PunchOutOrderMessage")

    # BuyerCookie
    buyer_cookie_elem = etree.SubElement(punchout_order_message, "BuyerCookie")
    buyer_cookie_elem.text = buyer_cookie

    # PunchOutOrderMessageHeader
    header = etree.SubElement(punchout_order_message, "PunchOutOrderMessageHeader", operationAllowed="create")
    total = etree.SubElement(header, "Total")
    money = etree.SubElement(total, "Money", currency="USD")
    money.text = product["price"]

    # ItemIn
    item_in = etree.SubElement(punchout_order_message, "ItemIn", quantity="1")
    item_id = etree.SubElement(item_in, "ItemID")
    supplier_part_id = etree.SubElement(item_id, "SupplierPartID")
    supplier_part_id.text = product["id"]
    supplier_part_aux_id = etree.SubElement(item_id, "SupplierPartAuxiliaryID")
    supplier_part_aux_id.text = "140-1163021-7594456,1"

    item_detail = etree.SubElement(item_in, "ItemDetail")
    unit_price = etree.SubElement(item_detail, "UnitPrice")
    money = etree.SubElement(unit_price, "Money", currency="USD")
    money.text = product["unit_price"]
    description = etree.SubElement(item_detail, "Description", lang="en")
    description.text = product["description"]
    unit_of_measure = etree.SubElement(item_detail, "UnitOfMeasure")
    unit_of_measure.text = product["unit_of_measure"]
    classification = etree.SubElement(item_detail, "Classification", domain="UNSPSC")
    classification.text = product["classification"]
    manufacturer_part_id = etree.SubElement(item_detail, "ManufacturerPartID")
    manufacturer_part_id.text = product["manufacturer_part_id"]
    manufacturer_name = etree.SubElement(item_detail, "ManufacturerName")
    manufacturer_name.text = product["manufacturer_name"]

    # Extrinsic fields
    extrinsic_sold_by = etree.SubElement(item_detail, "Extrinsic", name="soldBy")
    extrinsic_sold_by.text = product["sold_by"]
    extrinsic_fulfilled_by = etree.SubElement(item_detail, "Extrinsic", name="fulfilledBy")
    extrinsic_fulfilled_by.text = product["fulfilled_by"]
    extrinsic_category = etree.SubElement(item_detail, "Extrinsic", name="category")
    extrinsic_category.text = product["category"]
    extrinsic_sub_category = etree.SubElement(item_detail, "Extrinsic", name="subCategory")
    extrinsic_sub_category.text = product["sub_category"]
    extrinsic_item_condition = etree.SubElement(item_detail, "Extrinsic", name="itemCondition")
    extrinsic_item_condition.text = product["item_condition"]
    extrinsic_qualified_offer = etree.SubElement(item_detail, "Extrinsic", name="qualifiedOffer")
    extrinsic_qualified_offer.text = product["qualified_offer"]
    extrinsic_upc = etree.SubElement(item_detail, "Extrinsic", name="UPC")
    extrinsic_upc.text = product["upc"]
    extrinsic_detail_page_url = etree.SubElement(item_detail, "Extrinsic", name="detailPageURL")
    extrinsic_detail_page_url.text = product["detail_page_url"]
    extrinsic_ean = etree.SubElement(item_detail, "Extrinsic", name="ean")
    extrinsic_ean.text = product["ean"]
    extrinsic_preference = etree.SubElement(item_detail, "Extrinsic", name="preference")
    extrinsic_preference.text = product["preference"]

    return etree.tostring(cxml, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode()

@main.route('/')
def index():
    return_url = request.args.get('return_url', '')
    current_app.logger.info(f"Index - Return URL: {return_url}")
    return render_template('index.html', return_url=return_url)

@main.route('/punchout', methods=['GET', 'POST'])
def punchout():
    if request.method == 'POST':
        incoming_data = request.data.decode('utf-8')
        current_app.logger.info(f"PunchOut - Incoming Data: {incoming_data}")

        # Extract BuyerCookie and BrowserFormPost URL using string functions
        buyer_cookie = extract_value(incoming_data, '<BuyerCookie>', '</BuyerCookie>')
        return_url = extract_value(incoming_data, '<BrowserFormPost><URL>', '</URL></BrowserFormPost>')
        
        current_app.logger.info(f"PunchOut - Buyer Cookie: {buyer_cookie}")
        current_app.logger.info(f"PunchOut - Return URL: {return_url}")

        payload_id = saxutils.escape("2023-04-15T12:00:00-07:00")
        timestamp = saxutils.escape("2023-04-15T12:00:00-07:00")
        start_page_url = saxutils.escape(url_for('main.catalog', return_url=return_url, buyer_cookie=buyer_cookie, _external=True))
        
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
        
        return response_xml
    return render_template('product_details.html', product=products[0], return_url=request.args.get('return_url', ''))

@main.route('/catalog')
def catalog():
    return_url = request.args.get('return_url', '')
    buyer_cookie = request.args.get('buyer_cookie', '')
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
        products.append(product_data)
        return redirect(url_for('main.catalog'))

    return render_template('create_product.html')

@main.route('/checkout', methods=['POST'])
def checkout():
    return_url = request.args.get('return_url', '')
    buyer_cookie = request.args.get('buyer_cookie', '')
    current_app.logger.info(f"Checkout - Return URL: {return_url}, Buyer Cookie: {buyer_cookie}")
    product_id = request.form.get('product_id')

    # Retrieve product from in-memory storage
    product = next((p for p in products if p['id'] == product_id), None)

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Log the order details for debugging purposes
    order_details = create_punchout_order_message(buyer_cookie, product)
    current_app.logger.info(f"Order Details: {order_details}")

    if return_url:
        current_app.logger.info(f"Redirecting to: {return_url}")
        return redirect(return_url)
    return order_details
