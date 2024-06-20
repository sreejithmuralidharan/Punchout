from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

# Mock product data
product = {
    "id": "P001",
    "name": "Sample Product",
    "description": "What is Lorem Ipsum? Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum. Why do we use it?It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English. Many desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for 'lorem ipsum' will uncover many web sites still in their infancy. Various versions have evolved over the years, sometimes by accident, sometimes on purpose (injected humour and the like).",
    "price": "100.00"
}

# cXML PunchOut Setup Request Template
cxml_template = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE cXML SYSTEM "http://xml.cxml.org/schemas/cXML/1.2.014/cXML.dtd">
<cXML payloadID="2023-04-15T12:00:00-07:00" timestamp="2023-04-15T12:00:00-07:00">
    <Header>
        <From>
            <Credential domain="flask-example-from-domain">
                <Identity>flask-example-from</Identity>
            </Credential>
        </From>
        <To>
            <Credential domain="flask-example-to-domain">
                <Identity>flask-example-to</Identity>
            </Credential>
        </To>
        <Sender>
            <Credential domain="flask-example-sender-domain">
                <Identity>flask-example-sender</Identity>
                <SharedSecret>flask-example-password</SharedSecret>
            </Credential>
            <UserAgent>Python cXML PunchOut Example</UserAgent>
        </Sender>
    </Header>
    <Request>
        <PunchOutSetupRequest operation="create">
            <BuyerCookie>cookie-placeholder</BuyerCookie>
            <BrowserFormPost>
                <URL>http://localhost:5000/punchout</URL>
            </BrowserFormPost>
            <Contact role="endUser">
                <Name xml:lang="en">John Doe</Name>
                <Email>john.doe@example.com</Email>
            </Contact>
            <SupplierSetup>
                <URL>http://localhost:5000/punchout</URL>
            </SupplierSetup>
        </PunchOutSetupRequest>
    </Request>
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
        return cxml_template
    return render_template_string('''
    <h1>{{ product.name }}</h1>
    <p>{{ product.description }}</p>
    <p>Price: ${{ product.price }}</p>
    <form method="post" action="/submit">
        <input type="hidden" name="product_id" value="{{ product.id }}">
        <input type="submit" value="Add to Cart">
    </form>
    ''', product=product)

@app.route('/submit', methods=['POST'])
def submit():
    product_id = request.form.get('product_id')
    return f'<h1>Product {product_id} added to cart</h1>'

if __name__ == '__main__':
    app.run(debug=True)
