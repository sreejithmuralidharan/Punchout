import lxml.etree as etree
from datetime import datetime

def create_punchout_order_message(buyer_cookie, product):
    # Create the XML root element
    cxml = etree.Element(
        "cXML", 
        payloadID="1718898801551.591.1348@sreejith.co.uk",
        timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    )
    
    # Define the DOCTYPE
    doc_type = '<!DOCTYPE cXML SYSTEM "http://xml.cxml.org/schemas/cXML/1.2.024/cXML.dtd">'
    
    # Create the Header section
    header = etree.SubElement(cxml, "Header")
    
    from_cred = etree.SubElement(header, "From")
    from_credential = etree.SubElement(from_cred, "Credential", domain="DUNS")
    from_identity = etree.SubElement(from_credential, "Identity")
    from_identity.text = "128990368"
    from_credential2 = etree.SubElement(from_cred, "Credential", domain="NetworkId")
    from_identity2 = etree.SubElement(from_credential2, "Identity")
    from_identity2.text = "Sree"
    
    to_cred = etree.SubElement(header, "To")
    to_credential = etree.SubElement(to_cred, "Credential", domain="NetworkId")
    to_identity = etree.SubElement(to_credential, "Identity")
    to_identity.text = "Ivalua"
    
    sender = etree.SubElement(header, "Sender")
    sender_credential = etree.SubElement(sender, "Credential", domain="DUNS")
    sender_identity = etree.SubElement(sender_credential, "Identity")
    sender_identity.text = "128990368"
    sender_credential2 = etree.SubElement(sender, "Credential", domain="NetworkId")
    sender_identity2 = etree.SubElement(sender_credential2, "Identity")
    sender_identity2.text = "Sree"
    user_agent = etree.SubElement(sender, "UserAgent")
    user_agent.text = "Sree LLC eProcurement Application"
    
    # Create the Message section
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
    
    # Correctly setting the xml:lang attribute
    nsmap = {'xml': 'http://www.w3.org/XML/1998/namespace'}
    description = etree.SubElement(item_detail, "Description", attrib={"xml:lang": "en-US"}, nsmap=nsmap)
    description.text = product["description"]
    
    unit_of_measure = etree.SubElement(item_detail, "UnitOfMeasure")
    unit_of_measure.text = product["unit_of_measure"]
    classification = etree.SubElement(item_detail, "Classification", domain="UNSPSC")
    classification.text = product["classification"]
    manufacturer_part_id = etree.SubElement(item_detail, "ManufacturerPartID")
    manufacturer_part_id.text = product["manufacturer_part_id"]
    manufacturer_name = etree.SubElement(item_detail, "ManufacturerName")
    manufacturer_name.text = "Sreejith"
    
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
    
    # Convert the XML tree to a string
    cxml_string = etree.tostring(cxml, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode()
    return f"{doc_type}\n{cxml_string}"
