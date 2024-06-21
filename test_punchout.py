import pytest
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client

def test_punchout(client):
    with open('sample_punchout.xml', 'r') as file:
        sample_xml = file.read()

    headers = {'Content-Type': 'text/xml'}
    response = client.post('/punchout', data=sample_xml, headers=headers)
    assert response.status_code == 200
    assert '<Status code="200" text="OK">Success</Status>' in response.data.decode()
    assert '<PunchOutSetupResponse>' in response.data.decode()

def test_checkout_with_cookie(client):
    with client.session_transaction() as sess:
        sess['buyer_cookie'] = 'MjAyNDA2MjEuMS4zMjg2ODU0N0BlbnYxMS5pdmFsdWEuYXBwc3JlZWppdGgubXVyYWxpZGhhcmFuQG9qYy1jb25zdWx0aW5nLmNvbQ=='
        sess['return_url'] = 'https://env11.ivalua.app/buyer/bravida/sandboxevol/zpa8y/page.aspx/en/pun/basket_cxml/1?__isSecurePage=True'

    product_data = {
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
    }

    with client.application.app_context():
        client.application.db.products.insert_one(product_data)

    data = {
        'product_id': 'P001'
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = client.post('/checkout', data=data, headers=headers)
    assert response.status_code == 302  # Assuming a redirect happens on successful checkout

    # Validate redirect URL and that the buyer_cookie is correctly passed
    assert 'https://env11.ivalua.app/buyer/bravida/sandboxevol/zpa8y/page.aspx/en/pun/basket_cxml/1?__isSecurePage=True' in response.location
    assert 'buyer_cookie=MjAyNDA2MjEuMS4zMjg2ODU0N0BlbnYxMS5pdmFsdWEuYXBwc3JlZWppdGgubXVyYWxpZGhhcmFuQG9qYy1jb25zdWx0aW5nLmNvbQ==' in response.headers

def test_checkout_missing_cookie(client):
    data = {
        'product_id': 'P001'
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = client.post('/checkout', data=data, headers=headers)
    assert response.status_code == 400  # Should return 400 if buyer_cookie is missing

def test_full_flow(client):
    with open('sample_punchout.xml', 'r') as file:
        sample_xml = file.read()

    headers = {'Content-Type': 'text/xml'}
    punchout_response = client.post('/punchout', data=sample_xml, headers=headers)
    assert punchout_response.status_code == 200
    assert '<Status code="200" text="OK">Success</Status>' in punchout_response.data.decode()
    assert '<PunchOutSetupResponse>' in punchout_response.data.decode()

    with client.session_transaction() as sess:
        sess['buyer_cookie'] = 'MjAyNDA2MjEuMS4zMjg2ODU0N0BlbnYxMS5pdmFsdWEuYXBwc3JlZWppdGgubXVyYWxpZGhhcmFuQG9qYy1jb25zdWx0aW5nLmNvbQ=='
        sess['return_url'] = 'https://env11.ivalua.app/buyer/bravida/sandboxevol/zpa8y/page.aspx/en/pun/basket_cxml/1?__isSecurePage=True'

    product_data = {
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
    }

    with client.application.app_context():
        client.application.db.products.insert_one(product_data)

    data = {
        'product_id': 'P001'
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    checkout_response = client.post('/checkout', data=data, headers=headers)
    assert checkout_response.status_code == 302  # Assuming a redirect happens on successful checkout

    # Validate redirect URL and that the buyer_cookie is correctly passed
    assert 'https://env11.ivalua.app/buyer/bravida/sandboxevol/zpa8y/page.aspx/en/pun/basket_cxml/1?__isSecurePage=True' in checkout_response.location
    assert 'buyer_cookie=MjAyNDA2MjEuMS4zMjg2ODU0N0BlbnYxMS5pdmFsdWEuYXBwc3JlZWppdGgubXVyYWxpZGhhcmFuQG9qYy1jb25zdWx0aW5nLmNvbQ==' in checkout_response.headers
