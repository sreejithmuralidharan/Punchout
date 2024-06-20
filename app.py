from flask import Flask, request, render_template_string, redirect, url_for
import os

app = Flask(__name__)

# Mock product data
product = {
    "id": "P001",
    "name": "Sample Product",
    "description": "This is a sample product.",
    "price": "100.00"
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

@app.route('/')
def index():
    return render_template_string('''
    <h1>Welcome to the PunchOut Catalog</h1>
    <a href="/punchout">PunchOut to Catalog</a>
    ''')

@app.route('/punchout', methods=['GET', 'POST'])
def punchout():
    if request.method == 'POST':
        payload_id = "2023-04-15T12:00:00-07:00"
        timestamp = "2023-04-15T12:00:00-07:00"
        start_page_url = url_for('catalog', _external=True)
        return punchout_setup_response.format(payload_id=payload_id, timestamp=timestamp, start_page_url=start_page_url)
    return render_template_string('''
    <h1>{{ product.name }}</h1>
    <p>{{ product.description }}</p>
    <p>Price: ${{ product.price }}</p>
    <form method="post" action="/checkout">
        <input type="hidden" name="product_id" value="{{ product.id }}">
        <input type="submit" value="Add to Cart">
    </form>
    ''', product=product)

@app.route('/catalog')
def catalog():
    return render_template_string('''
    <h1>{{ product.name }}</h1>
    <p>{{ product.description }}</p>
    <p>Price: ${{ product.price }}</p>
    <form method="post" action="/checkout">
        <input type="hidden" name="product_id" value="{{ product.id }}">
        <input type="submit" value="Checkout">
    </form>
    ''', product=product)

@app.route('/checkout', methods=['POST'])
def checkout():
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
    return order_details

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
