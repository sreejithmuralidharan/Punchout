from flask import Flask, request, render_template_string, redirect, url_for
import os

app = Flask(__name__)

# Mock product data
product = {
    "id": "P001",
    "name": "Sample Product",
    "description": ("Experience the best quality with our Sample Product. "
                    "Crafted to perfection, this item is designed to meet your needs and "
                    "exceed your expectations. Perfect for any occasion." * 5),
    "price": "100.00",
    "image": "https://blog.aditmicrosys.com/wp-content/uploads/2019/03/dummy-product.png"
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
    return_url = request.args.get('return_url', '')
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.0.2/dist/tailwind.min.css" rel="stylesheet">
        <title>PunchOut Catalog</title>
    </head>
    <body class="bg-gray-100 text-gray-800">
        <div class="container mx-auto p-4">
            <h1 class="text-2xl font-bold mb-4">Welcome to the PunchOut Catalog</h1>
            <a href="/punchout?return_url={{ return_url }}" class="bg-blue-500 text-white px-4 py-2 rounded">PunchOut to Catalog</a>
        </div>
    </body>
    </html>
    ''', return_url=return_url)

@app.route('/punchout', methods=['GET', 'POST'])
def punchout():
    if request.method == 'POST':
        payload_id = "2023-04-15T12:00:00-07:00"
        timestamp = "2023-04-15T12:00:00-07:00"
        start_page_url = url_for('catalog', return_url=request.args.get('return_url', ''), _external=True)
        return punchout_setup_response.format(payload_id=payload_id, timestamp=timestamp, start_page_url=start_page_url)
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.0.2/dist/tailwind.min.css" rel="stylesheet">
        <title>Product Details</title>
    </head>
    <body class="bg-gray-100 text-gray-800">
        <div class="container mx-auto p-4">
            <div class="bg-white shadow-md rounded p-4">
                <img src="{{ product.image }}" alt="{{ product.name }}" class="w-full h-64 object-contain mb-4">
                <h1 class="text-2xl font-bold mb-2">{{ product.name }}</h1>
                <p class="mb-2">{{ product.description }}</p>
                <p class="text-lg font-semibold mb-4">Price: ${{ product.price }}</p>
                <form method="post" action="/submit?return_url={{ return_url }}">
                    <input type="hidden" name="product_id" value="{{ product.id }}">
                    <input type="submit" value="Add to Cart" class="bg-blue-500 text-white px-4 py-2 rounded">
                </form>
            </div>
        </div>
    </body>
    </html>
    ''', product=product, return_url=request.args.get('return_url', ''))

@app.route('/catalog')
def catalog():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.0.2/dist/tailwind.min.css" rel="stylesheet">
        <title>Product Catalog</title>
    </head>
    <body class="bg-gray-100 text-gray-800">
        <div class="container mx-auto p-4">
            <div class="bg-white shadow-md rounded p-4">
                <img src="{{ product.image }}" alt="{{ product.name }}" class="w-full h-64 object-contain mb-4">
                <h1 class="text-2xl font-bold mb-2">{{ product.name }}</h1>
                <p class="mb-2">{{ product.description }}</p>
                <p class="text-lg font-semibold mb-4">Price: ${{ product.price }}</p>
                <form method="post" action="/checkout?return_url={{ return_url }}">
                    <input type="hidden" name="product_id" value="{{ product.id }}">
                    <input type="submit" value="Checkout" class="bg-blue-500 text-white px-4 py-2 rounded">
                </form>
            </div>
        </div>
    </body>
    </html>
    ''', product=product, return_url=request.args.get('return_url', ''))

@app.route('/checkout', methods=['POST'])
def checkout():
    return_url = request.args.get('return_url', '')
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
        return redirect(return_url)
    return order_details

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
