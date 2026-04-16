from typing import List
from xml.dom import minidom

from app.model.entities import ClientRecord


def export_clients_to_xml_dom(records: List[ClientRecord], file_path: str) -> None:
    doc = minidom.Document()
    root = doc.createElement("clients")
    doc.appendChild(root)

    def add_text(parent, tag, text: str):
        el = doc.createElement(tag)
        el.appendChild(doc.createTextNode(text or ""))
        parent.appendChild(el)

    for r in records:
        client = doc.createElement("client")
        root.appendChild(client)

        add_text(client, "fio", r.fio)
        add_text(client, "account_number", r.account_number)
        add_text(client, "registration_address", r.registration_address)
        add_text(client, "mobile_phone", r.mobile_phone)
        add_text(client, "home_phone", r.home_phone)

    xml_str = doc.toprettyxml(indent="  ", encoding="utf-8")

    with open(file_path, "wb") as f:
        f.write(xml_str)
