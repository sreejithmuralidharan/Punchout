from flask import Blueprint, request, session, current_app
from lxml import etree
import xml.sax.saxutils as saxutils

punchout = Blueprint('punchout', __name__)

def extract_value(xml_str, start_tag, end_tag):
    try:
        start_index = xml_str.index(start_tag) + len(start_tag)
        end_index = xml_str.index(end_tag, start_index)
        return xml_str[start_index:end_index].strip()
    except ValueError:
        return None

@punchout.route('/punchout', methods=['POST'])
def punchout_route():
    incoming_data = request.data.decode('utf-8')
    current_app.logger.info(f"PunchOut - Incoming Data: {incoming_data}")

    buyer_cookie = extract_value(incoming_data, '<BuyerCookie>', '</BuyerCookie>')
    return_url = extract_value(incoming_data, '<BrowserFormPost><URL>', '</URL></BrowserFormPost>')

    session.clear()
    session['return_url'] = return_url
    session['buyer_cookie'] = buyer_cookie
    session['cart'] = []

    current_app.logger.info(f"PunchOut - Buyer Cookie: {buyer_cookie}")
    current_app.logger.info(f"PunchOut - Return URL: {return_url}")
    current_app.logger.info(f"Session after PunchOut: {dict(session)}")

    payload_id = saxutils.escape("2023-04-15T12:00:00-07:00")
    timestamp = saxutils.escape("2023-04-15T12:00:00-07:00")
    start_page_url = saxutils.escape(url_for('product.catalog', _external=True))
    
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
