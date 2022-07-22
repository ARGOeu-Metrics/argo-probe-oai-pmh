import unittest
from unittest.mock import patch

from argo_probe_oai_pmh.exceptions import XMLRequestException, \
    RequestException, XMLSchemaRequestException
from argo_probe_oai_pmh.requests import fetchXML, fetchXMLSchema

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


class MockResponse:
    def __init__(self, data, status_code):
        self.content = data
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


class RequestsTests(unittest.TestCase):
    @patch("requests.get")
    def test_fetch_XML(self, mock_get):
        mock_get.side_effect = mock_get_response_ok
        data, content_type = fetchXML("mock_url", timeout=30)
        self.assertEqual(data, ok_xml_string)
        self.assertEqual(content_type, "text/xml; charset=UTF-8")
        mock_get.assert_called_once_with("mock_url", timeout=30)

    @patch("requests.get")
    def test_fetch_XML_bad_status_code(self, mock_get):
        mock_get.side_effect = mock_get_response_500
        with self.assertRaises(XMLRequestException) as context:
            fetchXML("mock_url", timeout=30)
        mock_get.assert_called_once_with("mock_url", timeout=30)
        self.assertEqual(
            context.exception.__str__(),
            "Error fetching XML mock_url: 500 SERVER ERROR"
        )

    @patch("requests.get")
    def test_fetch_XML_ok_with_error(self, mock_get):
        mock_get.side_effect = mock_get_response_ok_with_error
        with self.assertRaises(XMLRequestException) as context:
            fetchXML("mock_url", timeout=30)
        mock_get.assert_called_once_with("mock_url", timeout=30)
        self.assertEqual(
            context.exception.__str__(),
            "Error fetching XML mock_url: badVerb: Invalid verb: bla"
        )

    @patch("requests.get")
    def test_fetch_XMLSchema(self, mock_get):
        mock_get.side_effect = mock_get_response_ok
        data = fetchXMLSchema("mock_url", timeout=30)
        self.assertEqual(data, ok_xml_string)
        mock_get.assert_called_once_with("mock_url", timeout=30)

    @patch("requests.get")
    def test_fetch_XMLSchema_bad_status_code(self, mock_get):
        mock_get.side_effect = mock_get_response_500
        with self.assertRaises(XMLSchemaRequestException) as context:
            fetchXMLSchema("mock_url", timeout=30)
        mock_get.assert_called_once_with("mock_url", timeout=30)
        self.assertEqual(
            context.exception.__str__(),
            "Error fetching XML schema mock_url: 500 SERVER ERROR"
        )
