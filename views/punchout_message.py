import lxml.etree as etree
from datetime import datetime

def create_punchout_order_message(buyer_cookie, cart):
    # Create the XML root element
    cxml = etree.Element(
        "cXML", 
        payloadID="1718898801551.591.1348@sreejith.co.uk",
        timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    )
    
    # Create the Header section
    header = etree.SubElement(cxml, "Header")
    
    from_cred = etree.SubElement(header, "From")
    from_credential = etree.SubElement(from_cred, "Credential", domain="DUNS")
    from_identity = etree.SubElement(from_credential, "Identity")
    from_identity.text = "128990368"
    from_credential2 = etree.SubElement(from_cred, "Credential", domain="NetworkId")
    from_identity2 = etree.SubElement(from_credential2, "Identity")
    from_identity2.text = "Amazon"
    
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
    sender_identity2.text = "Amazon"
    user_agent = etree.SubElement(sender, "UserAgent")
    user_agent.text = "Amazon LLC eProcurement Application"
    
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
    money.text = str(sum(float(item["price"]) for item in cart if isinstance(item, dict) and "price" in item))
    
    for product in cart:
        if isinstance(product, dict):  # Ensure product is a dictionary
            # ItemIn
            item_in = etree.SubElement(punchout_order_message, "ItemIn", quantity="1")
            item_id = etree.SubElement(item_in, "ItemID")
            supplier_part_id = etree.SubElement(item_id, "SupplierPartID")
            supplier_part_id.text = product.get("id", "")
            supplier_part_aux_id = etree.SubElement(item_id, "SupplierPartAuxiliaryID")
            supplier_part_aux_id.text = "140-1163021-7594456,1"
            
            item_detail = etree.SubElement(item_in, "ItemDetail")
            unit_price = etree.SubElement(item_detail, "UnitPrice")
            money = etree.SubElement(unit_price, "Money", currency="USD")
            money.text = product.get("unit_price", "0")
            
            description = etree.SubElement(item_detail, "Description", nsmap={"xml": "http://www.w3.org/XML/1998/namespace"})
            description.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = "en-US"
            description.text = product.get("description", "")
            
            unit_of_measure = etree.SubElement(item_detail, "UnitOfMeasure")
            unit_of_measure.text = product.get("unit_of_measure", "")
            classification = etree.SubElement(item_detail, "Classification", domain="UNSPSC")
            classification.text = product.get("classification", "")
            manufacturer_part_id = etree.SubElement(item_detail, "ManufacturerPartID")
            manufacturer_part_id.text = product.get("manufacturer_part_id", "")
            manufacturer_name = etree.SubElement(item_detail, "ManufacturerName")
            manufacturer_name.text = product.get("manufacturer_name", "")
            
            # Extrinsic fields
            extrinsic_fields = {
                "soldBy": product.get("sold_by", ""),
                "fulfilledBy": product.get("fulfilled_by", ""),
                "category": product.get("category", ""),
                "subCategory": product.get("sub_category", ""),
                "itemCondition": product.get("item_condition", ""),
                "qualifiedOffer": product.get("qualified_offer", ""),
                "UPC": product.get("upc", ""),
                "detailPageURL": product.get("detail_page_url", ""),
                "ean": product.get("ean", ""),
                "preference": product.get("preference", "")
            }
            for name, value in extrinsic_fields.items():
                extrinsic = etree.SubElement(item_detail, "Extrinsic", name=name)
                extrinsic.text = value
    
    # Convert the XML tree to a string
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>'
    doc_type = '<!DOCTYPE cXML SYSTEM "http://xml.cxml.org/schemas/cXML/1.2.024/cXML.dtd">'
    cxml_string = etree.tostring(cxml, pretty_print=True, xml_declaration=False, encoding="UTF-8").decode()
    
    return f"{xml_declaration}\n{doc_type}\n{cxml_string}"
