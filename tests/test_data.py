import datetime
import os
import unittest
from unittest.mock import patch

from argo_probe_oai_pmh.data import get_xml, get_xml_schema
from argo_probe_oai_pmh.exceptions import XMLRequestException, \
    RequestException, XMLSchemaRequestException

from test_xml import ok_xml_string

error_xml_string = \
    b'<?xml version="1.0" encoding="UTF-8"?>' \
    b'<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" ' \
    b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"' \
    b' xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/' \
    b' http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">' \
    b'<responseDate>2002-02-08T12:00:01Z</responseDate>' \
    b'<request>http://memory.loc.gov/cgi-bin/oai</request>' \
    b'<error code="badVerb">Invalid verb: bla</error>' \
    b'</OAI-PMH>'

LEN_OK_XML_STRING = len(ok_xml_string)


class MockResponse:
    def __init__(self, data, status_code):
        self.content = data
        self.elapsed = datetime.timedelta(seconds=0.2794524)
        self.headers = {"content-type": "text/xml; charset=UTF-8"}
        self.status_code = status_code
        self.reason = "SERVER ERROR"

    def raise_for_status(self):
        if not str(self.status_code).startswith("2"):
            raise RequestException(f"{self.status_code} {self.reason}")


def mock_get_response_ok(*args, **kwargs):
    return MockResponse(ok_xml_string, status_code=200)


def mock_get_response_500(*args, **kwargs):
    return MockResponse(ok_xml_string, status_code=500)


def mock_get_response_ok_with_error(*args, **kwargs):
    return MockResponse(error_xml_string, status_code=200)


class DataTests(unittest.TestCase):
    def setUp(self):
        self.schema_file = os.path.join(os.getcwd(), "oai-pmh.xsd")
        with open(self.schema_file, "wb") as f:
            f.write(ok_xml_string)

    def tearDown(self):
        if os.path.exists(self.schema_file):
            os.remove(self.schema_file)

    @patch("argo_probe_oai_pmh.data.requests.get")
    def test_get_xml(self, mock_get):
        mock_get.side_effect = mock_get_response_ok
        data, content_type, perfdata = get_xml(
            "https://mock.url.eu", timeout=30
        )
        self.assertEqual(data, ok_xml_string)
        self.assertEqual(content_type, "text/xml; charset=UTF-8")
        self.assertEqual(
            perfdata, f"|time=0.279452s;size={LEN_OK_XML_STRING}B"
        )
        mock_get.assert_called_once_with("https://mock.url.eu", timeout=30)

    @patch("argo_probe_oai_pmh.data.requests.get")
    def test_get_xml_bad_status_code(self, mock_get):
        mock_get.side_effect = mock_get_response_500
        with self.assertRaises(XMLRequestException) as context:
            get_xml("https://mock.url.eu", timeout=30)
        mock_get.assert_called_once_with("https://mock.url.eu", timeout=30)
        self.assertEqual(
            context.exception.__str__(),
            "Error fetching XML https://mock.url.eu: 500 SERVER ERROR"
        )

    def test_get_xml_schema(self):
        data = get_xml_schema(schema=self.schema_file)
        self.assertEqual(data, ok_xml_string)

    def test_get_xml_schema_if_file_nonexisting(self):
        with self.assertRaises(XMLSchemaRequestException) as context:
            get_xml_schema(schema="nonexisting.xsd")
        self.assertEqual(
            context.exception.__str__(),
            "Error reading XML schema: File nonexisting.xsd does not exist"
        )
