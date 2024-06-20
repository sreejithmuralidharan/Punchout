from flask import Blueprint, request, render_template, redirect, url_for
import xml.etree.ElementTree as ET
import logging

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

@main.route('/')
def index():
    return_url = request.args.get('return_url', '')
    logging.info(f"Index - Return URL: {return_url}")
    return render_template('index.html', return_url=return_url)

@main.route('/punchout', methods=['GET', 'POST'])
def punchout():
    if request.method == 'POST':
        # Parse the XML payload to extract return_url
        tree = ET.fromstring(request.data)
        browser_form_post = tree.find('.//{http://xml.cxml.org/schemas/cXML/1.1.008}BrowserFormPost')
        return_url = browser_form_post.find('{http://xml.cxml.org/schemas/cXML/1.1.008}URL').text if browser_form_post is not None else ''
        
        logging.info(f"PunchOut - Return URL: {return_url}")
        
        payload_id = "2023-04-15T12:00:00-07:00"
        timestamp = "2023-04-15T12:00:00-07:00"
        start_page_url = url_for('main.catalog', return_url=return_url, _external=True)
        return punchout_setup_response.format(payload_id=payload_id, timestamp=timestamp, start_page_url=start_page_url)
    return render_template('product_details.html', product=product, return_url=request.args.get('return_url', ''))

@main.route('/catalog')
def catalog():
    return_url = request.args.get('return_url', '')
    logging.info(f"Catalog - Return URL: {return_url}")
    return render_template('catalog.html', product=product, return_url=return_url)

@main.route('/checkout', methods=['POST'])
def checkout():
    return_url = request.args.get('return_url', '')
    logging.info(f"Checkout - Return URL: {return_url}")
    product_id = request.form.get('product_id')
    # Simulate returning order details to the procurement system
    order_details = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE cXML SYSTEM "http://xml.cxml.org/schemas/cXML/1.2.014/cXML.dtd">
<cXML payloadID="2023-04-15T12:00:00-07:00" timestamp="2023-04-15T12:00:00-07:00">
    <Response>
        <Status code="200" text="OK">Success</Status>
    </Response>
    <OrderMessage>
        <Item>
            <ItemID>{product_id}</ItemID>
            <Description>{product['description']}</Description>
            <UnitPrice>{product['price']}</UnitPrice>
        </Item>
    </OrderMessage>
</cXML>
'''
    if return_url:
        logging.info(f"Redirecting to: {return_url}")
        return redirect(return_url)
    return order_details
