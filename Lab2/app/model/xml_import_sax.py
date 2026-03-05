from typing import List
import xml.sax
from xml.sax.handler import ContentHandler

from Lab2.app.model.entities import ClientRecord


class _ClientsHandler(ContentHandler):
    def __init__(self):
        super().__init__()
        self.records: List[ClientRecord] = []
        self._current = None
        self._current_tag = None
        self._buffer = []

    def startElement(self, name, attrs):
        if name == "client":
            self._current = {
                "fio": "",
                "account_number": "",
                "registration_address": "",
                "mobile_phone": "",
                "home_phone": "",
            }
        elif self._current is not None:
            self._current_tag = name
            self._buffer = []

    def characters(self, content):
        if self._current is not None and self._current_tag is not None:
            self._buffer.append(content)

    def endElement(self, name):
        if name == "client":
            d = self._current or {}
            self.records.append(ClientRecord(**d))
            self._current = None
            self._current_tag = None
            self._buffer = []
            return

        if self._current is not None and self._current_tag == name:
            text = "".join(self._buffer).strip()
            if name in self._current:
                self._current[name] = text
            self._current_tag = None
            self._buffer = []


def import_clients_from_xml_sax(file_path: str) -> List[ClientRecord]:
    handler = _ClientsHandler()
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)

    with open(file_path, "rb") as f:
        parser.parse(f)

    return handler.records