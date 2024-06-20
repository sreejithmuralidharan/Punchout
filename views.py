from flask import Blueprint, request, render_template, redirect, url_for, current_app
import xml.etree.ElementTree as ET
import xml.sax.saxutils as saxutils

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

# cXML PunchOut Setup Response Template
punchout_setup_response = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE cXML SYSTEM "http://xml.cxml.org/schemas/cXML/1.2.014/cXML.dtd">
<cXML payloadID="{payload_id}" timestamp="{timestamp}">
    <Response>
        <Status code="200" text="OK">Success</Status>
        <PunchOutSetupResponse>
            <StartPage>
                <URL>{start_page_url}</URL>
            </StartPage>
        </PunchOutSetupResponse>
    </Response>
</cXML>
'''

# cXML Order Message Template
order_message = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE cXML SYSTEM "http://xml.cxml.org/schemas/cXML/1.2.014/cXML.dtd">
<cXML payloadID="2023-04-15T12:00:00-07:00" timestamp="2023-04-15T12:00:00-07:00">
    <Response>
        <Status code="200" text="OK">Success</Status>
    </Response>
    <Message>
        <PunchOutOrderMessage>
            <BuyerCookie>{buyer_cookie}</BuyerCookie>
            <PunchOutOrderMessageHeader operationAllowed="edit">
                <Total>
                    <Money currency="USD">{total_amount}</Money>
                </Total>
            </PunchOutOrderMessageHeader>
            <ItemIn quantity="1">
                <ItemID>
                    <SupplierPartID>{product_id}</SupplierPartID>
                </ItemID>
                <ItemDetail>
                    <UnitPrice>
                        <Money currency="USD">{unit_price}</Money>
                    </UnitPrice>
                    <Description xml:lang="en">{description}</Description>
                    <UnitOfMeasure>EA</UnitOfMeasure>
                    <Classification domain="UNSPSC">601210</Classification>
                    <ManufacturerPartID>{product_id}</ManufacturerPartID>
                    <ManufacturerName>Sample Manufacturer</ManufacturerName>
                </ItemDetail>
            </ItemIn>
        </PunchOutOrderMessage>
    </Message>
</cXML>
'''

@main.route('/')
def index():
    return_url = request.args.get('return_url', '')
    current_app.logger.info(f"Index - Return URL: {return_url}")
    return render_template('index.html', return_url=return_url)

@main.route('/punchout', methods=['GET', 'POST'])
def punchout():
    if request.method == 'POST':
        # Log the incoming request data for debugging
        incoming_data = request.data.decode('utf-8')
        current_app.logger.info(f"PunchOut - Incoming Data: {incoming_data}")

        # Parse the XML payload to extract return_url and buyer_cookie
        try:
            namespace = {'cxml': 'http://xml.cxml.org/schemas/cXML/1.1.008'}
            tree = ET.ElementTree(ET.fromstring(incoming_data))
            root = tree.getroot()
            current_app.logger.info(f"Parsed XML: {ET.tostring(root, encoding='utf8').decode('utf8')}")

            browser_form_post = tree.find('.//cxml:BrowserFormPost', namespace)
            if browser_form_post is not None:
                return_url = browser_form_post.find('cxml:URL', namespace).text
                current_app.logger.info(f"Found BrowserFormPost URL: {return_url}")
            else:
                current_app.logger.warning("BrowserFormPost element not found in the XML.")

            buyer_cookie_element = tree.find('.//cxml:BuyerCookie', namespace)
            if buyer_cookie_element is not None:
                buyer_cookie = buyer_cookie_element.text
                current_app.logger.info(f"Found BuyerCookie: {buyer_cookie}")
            else:
                current_app.logger.warning("BuyerCookie element not found in the XML.")
        except Exception as e:
            current_app.logger.error(f"Error parsing XML: {e}")
            return_url = ''
            buyer_cookie = ''

        current_app.logger.info(f"PunchOut - Return URL: {return_url}")
        current_app.logger.info(f"PunchOut - Buyer Cookie: {buyer_cookie}")
        
        payload_id = saxutils.escape("2023-04-15T12:00:00-07:00")
        timestamp = saxutils.escape("2023-04-15T12:00:00-07:00")
        start_page_url = saxutils.escape(url_for('main.catalog', return_url=return_url, buyer_cookie=buyer_cookie, _external=True))
        response_xml = punchout_setup_response.format(payload_id=payload_id, timestamp=timestamp, start_page_url=start_page_url)
        
        current_app.logger.info(f"PunchOut Setup Response: {response_xml}")
        
        return response_xml
    return render_template('product_details.html', product=product, return_url=request.args.get('return_url', ''))

@main.route('/catalog')
def catalog():
    return_url = request.args.get('return_url', '')
    buyer_cookie = request.args.get('buyer_cookie', '')
    current_app.logger.info(f"Catalog - Return URL: {return_url}, Buyer Cookie: {buyer_cookie}")
    return render_template('catalog.html', product=product, return_url=return_url, buyer_cookie=buyer_cookie)

@main.route('/checkout', methods=['POST'])
def checkout():
    return_url = request.args.get('return_url', '')
    buyer_cookie = request.args.get('buyer_cookie', '')
    current_app.logger.info(f"Checkout - Return URL: {return_url}, Buyer Cookie: {buyer_cookie}")
    product_id = request.form.get('product_id')
    # Simulate returning order details to the procurement system
    order_details = order_message.format(
        buyer_cookie=saxutils.escape(buyer_cookie),
        total_amount=saxutils.escape(product['price']),
        product_id=saxutils.escape(product_id),
        unit_price=saxutils.escape(product['price']),
        description=saxutils.escape(product['description'])
    )
    current_app.logger.info(f"Order Details: {order_details}")
    if return_url:
        current_app.logger.info(f"Redirecting to: {return_url}")
        return redirect(return_url)
    return order_details
