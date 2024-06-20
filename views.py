from flask import Blueprint, request, render_template, redirect, url_for, current_app
from lxml import etree
import xml.sax.saxutils as saxutils
from datetime import datetime

main = Blueprint('main', __name__)

# Mock product data
product = {
    "id": "P001",
    "name": "Sample Product",
    "description": ("Experience the best quality with our Sample Product. "
                    "Crafted to perfection, this item is designed to meet your needs and "
                    "exceed your expectations. Perfect for any occasion." * 5),
    "price": "100.00",
    "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff"
}

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
    punchout_order_message = etree.Element("PunchOutOrderMessage")

    # BuyerCookie
    buyer_cookie_elem = etree.SubElement(punchout_order_message, "BuyerCookie")
    buyer_cookie_elem.text = buyer_cookie

    # PunchOutOrderMessageHeader
    header = etree.SubElement(
        punchout_order_message, "PunchOutOrderMessageHeader", operationAllowed="edit")
    total = etree.SubElement(header, "Total")
    money = etree.SubElement(total, "Money", currency="USD")
    money.text = product["price"]

    # ItemIn
    item_in = etree.SubElement(punchout_order_message, "ItemIn", quantity="1")
    item_id = etree.SubElement(item_in, "ItemID")
    supplier_part_id = etree.SubElement(item_id, "SupplierPartID")
    supplier_part_id.text = product["id"]
    buyer_part_id = etree.SubElement(item_id, "BuyerPartID")
    buyer_part_id.text = product["id"]

    item_detail = etree.SubElement(item_in, "ItemDetail")
    unit_price = etree.SubElement(item_detail, "UnitPrice")
    money = etree.SubElement(unit_price, "Money", currency="USD")
    money.text = product["price"]
    description = etree.SubElement(
        item_detail, "Description", {"xml:lang": "en"})
    description.text = product["description"]
    unit_of_measure = etree.SubElement(item_detail, "UnitOfMeasure")
    unit_of_measure.text = "EA"
    classification = etree.SubElement(
        item_detail, "Classification", domain="UNSPSC")
    classification.text = "601210"
    manufacturer_part_id = etree.SubElement(item_detail, "ManufacturerPartID")
    manufacturer_part_id.text = product["id"]
    manufacturer_name = etree.SubElement(item_detail, "ManufacturerName")
    manufacturer_name.text = "Sample Manufacturer"

    return punchout_order_message


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
        buyer_cookie = extract_value(
            incoming_data, '<BuyerCookie>', '</BuyerCookie>')
        return_url = extract_value(
            incoming_data, '<BrowserFormPost>\n                <URL>', '</URL>\n            </BrowserFormPost>')

        current_app.logger.info(f"PunchOut - Buyer Cookie: {buyer_cookie}")
        current_app.logger.info(f"PunchOut - Return URL: {return_url}")

        payload_id = saxutils.escape("2023-04-15T12:00:00-07:00")
        timestamp = saxutils.escape("2023-04-15T12:00:00-07:00")
        start_page_url = saxutils.escape(url_for(
            'main.catalog', return_url=return_url, buyer_cookie=buyer_cookie, _external=True))

        punchout_setup_response = etree.Element(
            "cXML", payloadID=payload_id, timestamp=timestamp)
        response = etree.SubElement(punchout_setup_response, "Response")
        status = etree.SubElement(response, "Status", code="200", text="OK")
        status.text = "Success"
        punchout_setup_response_elem = etree.SubElement(
            response, "PunchOutSetupResponse")
        start_page = etree.SubElement(
            punchout_setup_response_elem, "StartPage")
        url_elem = etree.SubElement(start_page, "URL")
        url_elem.text = start_page_url

        response_xml = etree.tostring(
            punchout_setup_response, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode()
        current_app.logger.info(f"PunchOut Setup Response: {response_xml}")

        return response_xml
    return render_template('product_details.html', product=product, return_url=request.args.get('return_url', ''))


@main.route('/catalog')
def catalog():
    return_url = request.args.get('return_url', '')
    buyer_cookie = request.args.get(
        'buyer_cookie', 'hardcoded-buyer-cookie-value')
    current_app.logger.info(
        f"Catalog - Return URL: {return_url}, Buyer Cookie: {buyer_cookie}")
    return render_template('catalog.html', product=product, return_url=return_url, buyer_cookie=buyer_cookie)


@main.route('/checkout', methods=['POST'])
def checkout():
    return_url = request.args.get('return_url', '')
    buyer_cookie = request.args.get(
        'buyer_cookie', 'hardcoded-buyer-cookie-value')
    current_app.logger.info(
        f"Checkout - Return URL: {return_url}, Buyer Cookie: {buyer_cookie}")
    product_id = request.form.get('product_id')

    order_message_elem = etree.Element(
        "cXML", payloadID="2023-04-15T12:00:00-07:00", timestamp="2023-04-15T12:00:00-07:00")
    message = etree.SubElement(order_message_elem, "Message")
    punchout_order_message = create_punchout_order_message(
        buyer_cookie, product)
    message.append(punchout_order_message)

    order_details = etree.tostring(
        order_message_elem, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode()
    current_app.logger.info(f"Order Details: {order_details}")

    if return_url:
        current_app.logger.info(f"Redirecting to: {return_url}")
        return redirect(return_url)
    return order_details
