import pytest
from flask import Flask
from pymongo import MongoClient

@pytest.fixture
def app():
    from app import app  # Import your Flask app from your main application file

    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'supersecretkey'
    mongo_uri = "mongodb+srv://sreeojcconsulting:QGkO89qCZ8jNqNZA@punchouttester.zwv1kcs.mongodb.net/?retryWrites=true&w=majority&appName=PunchoutTester"
    mongo_db = "your_database_name_test"
    mongo_client = MongoClient(mongo_uri)
    test_db = mongo_client[mongo_db]
    app.db = test_db

    # Clean up database before running tests
    with app.app_context():
        app.db.sessions.delete_many({})
        app.db.products.delete_many({})

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_punchout(client):
    headers = {'Content-Type': 'text/xml'}
    with open('sample_punchout_request.xml', 'r') as file:
        sample_xml = file.read()
    response = client.post('/punchout', data=sample_xml, headers=headers)
    assert response.status_code == 200
    assert '<Status code="200" text="OK">Success</Status>' in response.data.decode()
    assert '<PunchOutSetupResponse>' in response.data.decode()

    # Check that the session was stored in the database
    session_count = client.application.db.sessions.count_documents({})
    assert session_count == 1

def test_checkout(client):
    # Simulate product addition to cart
    client.application.db.sessions.insert_one({
        'buyer_cookie': 'MjAyNDA2MjEuMS4zMjg2ODU0N0BlbnYxMS5pdmFsdWEuYXBwc3JlZWppdGgubXVyYWxpZGhhcmFuQG9qYy1jb25zdWx0aW5nLmNvbQ==',
        'return_url': 'https://env11.ivalua.app/buyer/bravida/sandboxevol/zpa8y/page.aspx/en/pun/basket_cxml/1?__isSecurePage=True'
    })

    # Add a sample product to the products collection
    client.application.db.products.insert_one({
        "id": "P001",
        "name": "Sample Product",
        "description": "Experience the best quality with our Sample Product. Crafted to perfection, this item is designed to meet your needs and exceed your expectations. Perfect for any occasion.",
        "price": "100.00",
        "image": "https://example.com/product_image.jpg",
        "unit_price": "100.00",
        "unit_of_measure": "EA",
        "classification": "601210",
        "manufacturer_part_id": "P001",
        "manufacturer_name": "Sample Manufacturer",
        "sold_by": "Our Company",
        "fulfilled_by": "Our Company",
        "category": "GENERAL",
        "sub_category": "GENERAL_ITEMS",
        "item_condition": "New",
        "qualified_offer": "true",
        "upc": "UPC-123456789012",
        "detail_page_url": "https://example.com/product/P001",
        "ean": "1234567890123",
        "preference": "default"
    })

    data = {
        'product_id': 'P001',
        'return_url': 'https://env11.ivalua.app/buyer/bravida/sandboxevol/zpa8y/page.aspx/en/pun/basket_cxml/1?__isSecurePage=True',
        'buyer_cookie': 'MjAyNDA2MjEuMS4zMjg2ODU0N0BlbnYxMS5pdmFsdWEuYXBwc3JlZWppdGgubXVyYWxpZGhhcmFuQG9qYy1jb25zdWx0aW5nLmNvbQ=='
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = client.post('/checkout', data=data, headers=headers)
    assert response.status_code == 302  # Assuming a redirect happens on successful checkout

    # Check that the product was correctly handled
    product_count = client.application.db.products.count_documents({'id': 'P001'})
    assert product_count == 1

    # Validate redirect URL and that the buyer_cookie is correctly passed
    assert 'https://env11.ivalua.app/buyer/bravida/sandboxevol/zpa8y/page.aspx/en/pun/basket_cxml/1?__isSecurePage=True' in response.location
    assert 'buyer_cookie=MjAyNDA2MjEuMS4zMjg2ODU0N0BlbnYxMS5pdmFsdWEuYXBwc3JlZWppdGgubXVyYWxpZGhhcmFuQG9qYy1jb25zdWx0aW5nLmNvbQ==' in response.location

if __name__ == '__main__':
    pytest.main()
