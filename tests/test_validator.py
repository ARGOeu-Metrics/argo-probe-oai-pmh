import os.path
import unittest
from unittest import mock

from argo_probe_oai_pmh.exceptions import XMLSchemaRequestException, \
    RequestException
from argo_probe_oai_pmh.validator import Validator, CompareXMLSchemas

from test_xml import ok_xml_string

XML_PERFDATA = "|time=0.234432s;size=1234567B"

ok_xml_string2 = \
    b'<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" ' \
    b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"' \
    b' xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/' \
    b' http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">' \
    b'<responseDate>2002-02-08T12:00:01Z</responseDate>' \
    b'<request verb="Identify">http://memory.loc.gov/cgi-bin/oai</request>' \
    b'<Identify> ' \
    b'<repositoryName>Library of Congress Open Archive Initiative ' \
    b'Repository 1</repositoryName>' \
    b'<baseURL>http://memory.loc.gov/cgi-bin/oai</baseURL>' \
    b'<protocolVersion>2.0</protocolVersion>' \
    b'<adminEmail>somebody@loc.gov</adminEmail>' \
    b'<adminEmail>anybody@loc.gov</adminEmail>' \
    b'<earliestDatestamp>1990-02-01T12:00:00Z</earliestDatestamp>' \
    b'<deletedRecord>transient</deletedRecord>' \
    b'<granularity>YYYY-MM-DDThh:mm:ssZ</granularity>' \
    b'<compression>deflate</compression>' \
    b'<description>' \
    b'<oai-identifier ' \
    b'xmlns="http://www.openarchives.org/OAI/2.0/oai-identifier" ' \
    b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
    b'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai-identifier ' \
    b'http://www.openarchives.org/OAI/2.0/oai-identifier.xsd">' \
    b'<scheme>oai</scheme>' \
    b'<repositoryIdentifier>lcoa1.loc.gov</repositoryIdentifier>' \
    b'<delimiter>:</delimiter>' \
    b'<sampleIdentifier>oai:lcoa1.loc.gov:loc.music/musdi.002' \
    b'</sampleIdentifier>' \
    b'</oai-identifier>' \
    b'</description>' \
    b'<description>' \
    b'<eprints xmlns="http://www.openarchives.org/OAI/1.1/eprints" ' \
    b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
    b'xsi:schemaLocation="http://www.openarchives.org/OAI/1.1/eprints ' \
    b'http://www.openarchives.org/OAI/1.1/eprints.xsd">' \
    b'<content>' \
    b'<URL>http://memory.loc.gov/ammem/oamh/lcoa1_content.html</URL>' \
    b'<text>Selected collections from American Memory at the Library ' \
    b'of Congress</text>' \
    b'</content>' \
    b'<metadataPolicy/>' \
    b'<dataPolicy/>' \
    b'</eprints>' \
    b'</description>' \
    b'<description>' \
    b'<friends xmlns="http://www.openarchives.org/OAI/2.0/friends/" ' \
    b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
    b'xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/friends/ ' \
    b'http://www.openarchives.org/OAI/2.0/friends.xsd"> ' \
    b'<baseURL>http://oai.east.org/foo/</baseURL> ' \
    b'<baseURL>http://oai.hq.org/bar/</baseURL>' \
    b'<baseURL>http://oai.south.org/repo.cgi</baseURL>' \
    b'</friends>' \
    b'</description>' \
    b'</Identify>' \
    b'</OAI-PMH>'


def mock_func(*args, **kwargs):
    pass


def mock_schema_exception(*args, **kwargs):
    raise XMLSchemaRequestException(title="", msg="500 SERVER ERROR")


def mock_request_exception(*args, **kwargs):
    raise RequestException(msg="request exception")


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.verbose_validator = Validator(
            url="https://mock.url.eu?Identify",
            schema="/var/spool/argo/probe/oai_pmh/schema.xsd",
            timeout=30,
            verbose=True
        )
        self.nonverbose_validator = Validator(
            url="https://mock.url.eu?Identify",
            schema="/var/spool/argo/probe/oai_pmh/schema.xsd",
            timeout=30,
            verbose=False
        )

    @mock.patch("argo_probe_oai_pmh.validator.sys.exit")
    @mock.patch("argo_probe_oai_pmh.validator.print")
    @mock.patch("argo_probe_oai_pmh.validator.xml_schema_validation")
    @mock.patch("argo_probe_oai_pmh.validator.get_xml_schema")
    @mock.patch("argo_probe_oai_pmh.validator.get_xml")
    def test_validate_XML_ok_verbose(
            self, mock_fetch_xml, mock_fetch_schema, mock_schema_validation,
            mock_print, mock_exit
    ):
        mock_fetch_xml.return_value = (b"mock_xml", "text/xml; charset=UTF-8",
                                       XML_PERFDATA)
        mock_fetch_schema.return_value = b"mock_xml_schema"
        mock_schema_validation.return_value = True
        mock_print.side_effect = mock_func
        mock_exit.side_effect = mock_func
        mock_xml_content = mock.Mock()
        mock_xml_content_instance = mock_xml_content.return_value
        mock_xml_content_instance.validate.side_effect = mock_func
        mock_xml_content_instance.validate_admin_emails.return_value = None
        mock_xml_content_instance.get_admin_emails.return_value = \
            ["mock@email.com"]
        with mock.patch(
                "argo_probe_oai_pmh.validator.XMLContent", mock_xml_content
        ):
            self.verbose_validator.validate()
        self.assertEqual(mock_fetch_xml.call_count, 2)
        mock_fetch_xml.assert_has_calls([
            mock.call(url="https://mock.url.eu?Identify", timeout=30),
            mock.call(url="https://mock.url.eu", timeout=30)
        ], any_order=True)
        mock_fetch_schema.assert_called_once_with(
            schema="/var/spool/argo/probe/oai_pmh/schema.xsd"
        )
        mock_schema_validation.assert_called_once()
        mock_print.assert_called_once_with(
            f"OK - XML is valid{XML_PERFDATA}\n"
            f"HTTP status OK\n"
            f"Content type text/xml\n"
            f"Content XML valid\n"
            f"XML complies with OAI-PMH XML Schema https://www.openarchives.org"
            f"/OAI/2.0/OAI-PMH.xsd\n"
            f"Valid adminEmail: mock@email.com"
        )
        mock_exit.assert_called_once_with(0)

    @mock.patch("argo_probe_oai_pmh.validator.sys.exit")
    @mock.patch("argo_probe_oai_pmh.validator.print")
    @mock.patch("argo_probe_oai_pmh.validator.xml_schema_validation")
    @mock.patch("argo_probe_oai_pmh.validator.get_xml_schema")
    @mock.patch("argo_probe_oai_pmh.validator.get_xml")
    def test_validate_XML_ok_not_verbose(
            self, mock_fetch_xml, mock_fetch_schema, mock_schema_validation,
            mock_print, mock_exit
    ):
        mock_fetch_xml.return_value = (b"mock_xml", "text/xml; charset=UTF-8",
                                       XML_PERFDATA)
        mock_fetch_schema.return_value = b"mock_xml_schema"
        mock_schema_validation.return_value = True
        mock_print.side_effect = mock_func
        mock_exit.side_effect = mock_func
        mock_xml_content = mock.Mock()
        mock_xml_content_instance = mock_xml_content.return_value
        mock_xml_content_instance.validate.side_effect = mock_func
        mock_xml_content_instance.validate_admin_emails.return_value = None
        mock_xml_content_instance.get_admin_emails.return_value = \
            ["mock@email.com"]
        with mock.patch(
                "argo_probe_oai_pmh.validator.XMLContent", mock_xml_content
        ):
            self.nonverbose_validator.validate()
        self.assertEqual(mock_fetch_xml.call_count, 2)
        mock_fetch_xml.assert_has_calls([
            mock.call(url="https://mock.url.eu?Identify", timeout=30),
            mock.call(url="https://mock.url.eu", timeout=30)
        ], any_order=True)
        mock_fetch_schema.assert_called_once_with(
            schema="/var/spool/argo/probe/oai_pmh/schema.xsd"
        )
        mock_schema_validation.assert_called_once()
        mock_print.assert_called_once_with(f"OK - XML is valid{XML_PERFDATA}")
        mock_exit.assert_called_once_with(0)

    @mock.patch("argo_probe_oai_pmh.validator.sys.exit")
    @mock.patch("argo_probe_oai_pmh.validator.print")
    @mock.patch("argo_probe_oai_pmh.validator.xml_schema_validation")
    @mock.patch("argo_probe_oai_pmh.validator.get_xml_schema")
    @mock.patch("argo_probe_oai_pmh.validator.get_xml")
    def test_validate_XML_critical_content_verbose(
            self, mock_fetch_xml, mock_fetch_schema, mock_schema_validation,
            mock_print, mock_exit
    ):
        mock_fetch_xml.return_value = (b"mock_xml", "text/xml; charset=UTF-8",
                                       XML_PERFDATA)
        mock_fetch_schema.return_value = b"mock_xml_schema"
        mock_schema_validation.return_value = False
        mock_print.side_effect = mock_func
        mock_exit.side_effect = mock_func
        mock_xml_content = mock.Mock()
        mock_xml_content_instance = mock_xml_content.return_value
        mock_xml_content_instance.validate.return_value = \
            "Missing element 'test'"
        mock_xml_content_instance.validate_admin_emails.return_value = None
        mock_xml_content_instance.get_admin_emails.return_value = \
            ["mock@email.com"]
        with mock.patch(
                "argo_probe_oai_pmh.validator.XMLContent", mock_xml_content
        ):
            self.verbose_validator.validate()
        self.assertEqual(mock_fetch_xml.call_count, 2)
        mock_fetch_xml.assert_has_calls([
            mock.call(url="https://mock.url.eu?Identify", timeout=30),
            mock.call(url="https://mock.url.eu", timeout=30)
        ], any_order=True)
        mock_fetch_schema.assert_called_once_with(
            schema="/var/spool/argo/probe/oai_pmh/schema.xsd"
        )
        mock_schema_validation.assert_called_once()
        mock_print.assert_called_once_with(
            f"CRITICAL - Content XML not valid - Missing element 'test'"
            f"{XML_PERFDATA}\n"
            f"XML does not comply with OAI-PMH XML Schema "
            f"https://www.openarchives.org/OAI/2.0/OAI-PMH.xsd"
        )
        mock_exit.assert_called_once_with(2)

    @mock.patch("argo_probe_oai_pmh.validator.sys.exit")
    @mock.patch("argo_probe_oai_pmh.validator.print")
    @mock.patch("argo_probe_oai_pmh.validator.xml_schema_validation")
    @mock.patch("argo_probe_oai_pmh.validator.get_xml_schema")
    @mock.patch("argo_probe_oai_pmh.validator.get_xml")
    def test_validate_XML_critical_content_nonverbose(
            self, mock_fetch_xml, mock_fetch_schema, mock_schema_validation,
            mock_print, mock_exit
    ):
        mock_fetch_xml.return_value = (b"mock_xml", "text/xml; charset=UTF-8",
                                       XML_PERFDATA)
        mock_fetch_schema.return_value = b"mock_xml_schema"
        mock_schema_validation.return_value = False
        mock_print.side_effect = mock_func
        mock_exit.side_effect = mock_func
        mock_xml_content = mock.Mock()
        mock_xml_content_instance = mock_xml_content.return_value
        mock_xml_content_instance.validate.return_value = \
            "Missing element 'test'"
        mock_xml_content_instance.validate_admin_emails.return_value = None
        mock_xml_content_instance.get_admin_emails.return_value = \
            ["mock@email.com"]
        with mock.patch(
                "argo_probe_oai_pmh.validator.XMLContent", mock_xml_content
        ):
            self.nonverbose_validator.validate()
        self.assertEqual(mock_fetch_xml.call_count, 2)
        mock_fetch_xml.assert_has_calls([
            mock.call(url="https://mock.url.eu?Identify", timeout=30),
            mock.call(url="https://mock.url.eu", timeout=30)
        ], any_order=True)
        mock_fetch_schema.assert_called_once_with(
            schema="/var/spool/argo/probe/oai_pmh/schema.xsd"
        )
        mock_schema_validation.assert_called_once()
        mock_print.assert_called_once_with(
            f"CRITICAL - Content XML not valid - Missing element 'test'"
            f"{XML_PERFDATA}\n"
            f"XML does not comply with OAI-PMH XML Schema "
            f"https://www.openarchives.org/OAI/2.0/OAI-PMH.xsd"
        )
        mock_exit.assert_called_once_with(2)

    @mock.patch("argo_probe_oai_pmh.validator.sys.exit")
    @mock.patch("argo_probe_oai_pmh.validator.print")
    @mock.patch("argo_probe_oai_pmh.validator.xml_schema_validation")
    @mock.patch("argo_probe_oai_pmh.validator.get_xml_schema")
    @mock.patch("argo_probe_oai_pmh.validator.get_xml")
    def test_validate_XML_xmlschema_fetch_error_content_verbose(
            self, mock_fetch_xml, mock_fetch_schema, mock_schema_validation,
            mock_print, mock_exit
    ):
        mock_fetch_xml.return_value = (b"mock_xml", "text/xml; charset=UTF-8",
                                       XML_PERFDATA)
        mock_fetch_schema.side_effect = mock_schema_exception
        mock_schema_validation.side_effect = mock_func
        mock_print.side_effect = mock_func
        mock_exit.side_effect = mock_func
        mock_xml_content = mock.Mock()
        mock_xml_content_instance = mock_xml_content.return_value
        mock_xml_content_instance.validate.side_effect = mock_func
        mock_xml_content_instance.validate_admin_emails.return_value = None
        mock_xml_content_instance.get_admin_emails.return_value = \
            ["mock@email.com"]
        with mock.patch(
                "argo_probe_oai_pmh.validator.XMLContent", mock_xml_content
        ):
            self.verbose_validator.validate()
        self.assertEqual(mock_fetch_xml.call_count, 2)
        mock_fetch_xml.assert_has_calls([
            mock.call(url="https://mock.url.eu?Identify", timeout=30),
            mock.call(url="https://mock.url.eu", timeout=30)
        ], any_order=True)
        mock_fetch_schema.assert_called_once_with(
            schema="/var/spool/argo/probe/oai_pmh/schema.xsd"
        )
        self.assertFalse(mock_schema_validation.called)
        mock_print.assert_called_once_with(
            f"CRITICAL - Unable to read OAI-PMH XML Schema "
            f"/var/spool/argo/probe/oai_pmh/schema.xsd - "
            f"schema compliance not tested: Error reading XML schema: "
            f"500 SERVER ERROR{XML_PERFDATA}"
        )
        mock_exit.assert_called_once_with(2)

    @mock.patch("argo_probe_oai_pmh.validator.sys.exit")
    @mock.patch("argo_probe_oai_pmh.validator.print")
    @mock.patch("argo_probe_oai_pmh.validator.xml_schema_validation")
    @mock.patch("argo_probe_oai_pmh.validator.get_xml_schema")
    @mock.patch("argo_probe_oai_pmh.validator.get_xml")
    def test_validate_XML_xmlschema_fetch_error_content_nonverbose(
            self, mock_fetch_xml, mock_fetch_schema, mock_schema_validation,
            mock_print, mock_exit
    ):
        mock_fetch_xml.return_value = (b"mock_xml", "text/xml; charset=UTF-8",
                                       XML_PERFDATA)
        mock_fetch_schema.side_effect = mock_schema_exception
        mock_schema_validation.side_effect = mock_func
        mock_print.side_effect = mock_func
        mock_exit.side_effect = mock_func
        mock_xml_content = mock.Mock()
        mock_xml_content_instance = mock_xml_content.return_value
        mock_xml_content_instance.validate.side_effect = mock_func
        mock_xml_content_instance.validate_admin_emails.return_value = None
        mock_xml_content_instance.get_admin_emails.return_value = \
            ["mock@email.com"]
        with mock.patch(
                "argo_probe_oai_pmh.validator.XMLContent", mock_xml_content
        ):
            self.nonverbose_validator.validate()
        self.assertEqual(mock_fetch_xml.call_count, 2)
        mock_fetch_xml.assert_has_calls([
            mock.call(url="https://mock.url.eu?Identify", timeout=30),
            mock.call(url="https://mock.url.eu", timeout=30)
        ], any_order=True)
        mock_fetch_schema.assert_called_once_with(
            schema="/var/spool/argo/probe/oai_pmh/schema.xsd"
        )
        self.assertFalse(mock_schema_validation.called)
        mock_print.assert_called_once_with(
            f"CRITICAL - Unable to read OAI-PMH XML Schema "
            f"/var/spool/argo/probe/oai_pmh/schema.xsd - "
            f"schema compliance not tested: Error reading XML schema: "
            f"500 SERVER ERROR{XML_PERFDATA}"
        )
        mock_exit.assert_called_once_with(2)


class CompareXMLSchemasTests(unittest.TestCase):
    def setUp(self):
        self.mock_schema_file = os.path.join(os.getcwd(), "oai-pmh.xsd")
        self.comparison = CompareXMLSchemas(
            url="https://mock.url.eu",
            user_agent="Mozilla/5.0 (X11; Linux x86_64)",
            timeout=30
        )

    def tearDown(self):
        if os.path.exists(self.mock_schema_file):
            os.remove(self.mock_schema_file)

    @mock.patch("argo_probe_oai_pmh.validator.sys.exit")
    @mock.patch("argo_probe_oai_pmh.validator.print")
    @mock.patch("argo_probe_oai_pmh.validator.fetch_xml_schema")
    @mock.patch("argo_probe_oai_pmh.validator.get_xml_schema")
    def test_compare_equal(self, mock_get, mock_fetch, mock_print, mock_exit):
        mock_get.return_value = ok_xml_string
        mock_fetch.return_value = ok_xml_string
        mock_print.side_effect = mock_func
        mock_exit.side_effect = mock_func
        self.comparison.compare(filepath=self.mock_schema_file)
        mock_get.assert_called_once_with(schema=self.mock_schema_file)
        mock_fetch.assert_called_once_with(
            url="https://mock.url.eu",
            user_agent="Mozilla/5.0 (X11; Linux x86_64)",
            timeout=30
        )
        self.assertFalse(os.path.exists(self.mock_schema_file))
        mock_print.assert_called_once_with("OK - XML schema is up-to-date")
        mock_exit.assert_called_once_with(0)

    @mock.patch("argo_probe_oai_pmh.validator.sys.exit")
    @mock.patch("argo_probe_oai_pmh.validator.print")
    @mock.patch("argo_probe_oai_pmh.validator.fetch_xml_schema")
    @mock.patch("argo_probe_oai_pmh.validator.get_xml_schema")
    def test_compare_not_equal(
            self, mock_get, mock_fetch, mock_print, mock_exit
    ):
        mock_get.return_value = ok_xml_string2
        mock_fetch.return_value = ok_xml_string
        mock_print.side_effect = mock_func
        mock_exit.side_effect = mock_func
        self.comparison.compare(filepath=self.mock_schema_file)
        mock_get.assert_called_once_with(schema=self.mock_schema_file)
        mock_fetch.assert_called_once_with(
            url="https://mock.url.eu",
            user_agent="Mozilla/5.0 (X11; Linux x86_64)",
            timeout=30
        )
        self.assertTrue(os.path.exists(self.mock_schema_file))
        with open(self.mock_schema_file, "rb") as f:
            mock_data = f.read()
        self.assertEqual(mock_data, ok_xml_string)
        mock_print.assert_called_once_with(
            "WARNING - XML schema is outdated - updating"
        )
        mock_exit.assert_called_once_with(1)

    @mock.patch("argo_probe_oai_pmh.validator.sys.exit")
    @mock.patch("argo_probe_oai_pmh.validator.print")
    @mock.patch("argo_probe_oai_pmh.validator.fetch_xml_schema")
    @mock.patch("argo_probe_oai_pmh.validator.get_xml_schema")
    def test_compare_with_fetch_exception(
            self, mock_get, mock_fetch, mock_print, mock_exit
    ):
        mock_get.return_value = ok_xml_string2
        mock_fetch.side_effect = mock_request_exception
        mock_print.side_effect = mock_func
        mock_exit.side_effect = mock_func
        self.comparison.compare(filepath=self.mock_schema_file)
        mock_fetch.assert_called_once_with(
            url="https://mock.url.eu",
            user_agent="Mozilla/5.0 (X11; Linux x86_64)",
            timeout=30
        )
        self.assertFalse(os.path.exists(self.mock_schema_file))
        mock_print.assert_called_once_with("CRITICAL - request exception")
        mock_exit.assert_called_once_with(2)

    @mock.patch("argo_probe_oai_pmh.validator.sys.exit")
    @mock.patch("argo_probe_oai_pmh.validator.print")
    @mock.patch("argo_probe_oai_pmh.validator.fetch_xml_schema")
    @mock.patch("argo_probe_oai_pmh.validator.get_xml_schema")
    def test_compare_with_read_exception(
            self, mock_get, mock_fetch, mock_print, mock_exit
    ):
        mock_get.side_effect = mock_schema_exception
        mock_fetch.return_value = ok_xml_string
        mock_print.side_effect = mock_func
        mock_exit.side_effect = mock_func
        self.comparison.compare(filepath=self.mock_schema_file)
        mock_fetch.assert_called_once_with(
            url="https://mock.url.eu",
            user_agent="Mozilla/5.0 (X11; Linux x86_64)",
            timeout=30
        )
        self.assertFalse(os.path.exists(self.mock_schema_file))
        mock_print.assert_called_once_with(
            "CRITICAL - Error reading XML schema: 500 SERVER ERROR"
        )
        mock_exit.assert_called_once_with(2)

