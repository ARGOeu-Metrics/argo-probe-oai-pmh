import unittest
from unittest import mock

from argo_probe_oai_pmh.exceptions import XMLSchemaRequestException
from argo_probe_oai_pmh.validator import Validator


def mock_func(*args, **kwargs):
    pass


def mock_schema_exception(*args, **kwargs):
    raise XMLSchemaRequestException(title="", msg="500 SERVER ERROR")


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.verbose_validator = Validator(
            url="mock_url?Identify", timeout=30, verbose=True
        )
        self.nonverbose_validator = Validator(
            url="mock_url?Identify", timeout=30, verbose=False
        )

    @mock.patch("argo_probe_oai_pmh.validator.sys.exit")
    @mock.patch("argo_probe_oai_pmh.validator.print")
    @mock.patch("argo_probe_oai_pmh.validator.xml_schema_validation")
    @mock.patch("argo_probe_oai_pmh.validator.fetchXMLSchema")
    @mock.patch("argo_probe_oai_pmh.validator.fetchXML")
    def test_validate_XML_ok_verbose(
            self, mock_fetch_xml, mock_fetch_schema, mock_schema_validation,
            mock_print, mock_exit
    ):
        mock_fetch_xml.return_value = b"mock_xml", "text/xml; charset=UTF-8"
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
            mock.call(url="mock_url?Identify", timeout=30),
            mock.call(url="mock_url", timeout=30)
        ], any_order=True)
        mock_fetch_schema.assert_called_once_with(
            url="http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd", timeout=30
        )
        mock_schema_validation.assert_called_once()
        mock_print.assert_called_once_with(
            "OK - XML is valid.\n"
            "HTTP status OK.\n"
            "Content type text/xml\n"
            "Content XML valid.\n"
            "XML complies with OAI-PMH XML Schema http://www.openarchives.org"
            "/OAI/2.0/OAI-PMH.xsd\n"
            "Valid adminEmail: mock@email.com"
        )
        mock_exit.assert_called_once_with(0)

    @mock.patch("argo_probe_oai_pmh.validator.sys.exit")
    @mock.patch("argo_probe_oai_pmh.validator.print")
    @mock.patch("argo_probe_oai_pmh.validator.xml_schema_validation")
    @mock.patch("argo_probe_oai_pmh.validator.fetchXMLSchema")
    @mock.patch("argo_probe_oai_pmh.validator.fetchXML")
    def test_validate_XML_ok_not_verbose(
            self, mock_fetch_xml, mock_fetch_schema, mock_schema_validation,
            mock_print, mock_exit
    ):
        mock_fetch_xml.return_value = b"mock_xml", "text/xml; charset=UTF-8"
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
            mock.call(url="mock_url?Identify", timeout=30),
            mock.call(url="mock_url", timeout=30)
        ], any_order=True)
        mock_fetch_schema.assert_called_once_with(
            url="http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd", timeout=30
        )
        mock_schema_validation.assert_called_once()
        mock_print.assert_called_once_with("OK - XML is valid.")
        mock_exit.assert_called_once_with(0)

    @mock.patch("argo_probe_oai_pmh.validator.sys.exit")
    @mock.patch("argo_probe_oai_pmh.validator.print")
    @mock.patch("argo_probe_oai_pmh.validator.xml_schema_validation")
    @mock.patch("argo_probe_oai_pmh.validator.fetchXMLSchema")
    @mock.patch("argo_probe_oai_pmh.validator.fetchXML")
    def test_validate_XML_critical_content_verbose(
            self, mock_fetch_xml, mock_fetch_schema, mock_schema_validation,
            mock_print, mock_exit
    ):
        mock_fetch_xml.return_value = b"mock_xml", "text/xml; charset=UTF-8"
        mock_fetch_schema.return_value = b"mock_xml_schema"
        mock_schema_validation.return_value = False
        mock_print.side_effect = mock_func
        mock_exit.side_effect = mock_func
        mock_xml_content = mock.Mock()
        mock_xml_content_instance = mock_xml_content.return_value
        mock_xml_content_instance.validate.return_value = \
            "Missing element 'test'."
        mock_xml_content_instance.validate_admin_emails.return_value = None
        mock_xml_content_instance.get_admin_emails.return_value = \
            ["mock@email.com"]
        with mock.patch(
                "argo_probe_oai_pmh.validator.XMLContent", mock_xml_content
        ):
            self.verbose_validator.validate()
        self.assertEqual(mock_fetch_xml.call_count, 2)
        mock_fetch_xml.assert_has_calls([
            mock.call(url="mock_url?Identify", timeout=30),
            mock.call(url="mock_url", timeout=30)
        ], any_order=True)
        mock_fetch_schema.assert_called_once_with(
            url="http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd", timeout=30
        )
        mock_schema_validation.assert_called_once()
        mock_print.assert_called_once_with(
            "CRITICAL - Content XML not valid - Missing element 'test'.\n"
            "XML does not comply with OAI-PMH XML Schema "
            "http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd"
        )
        mock_exit.assert_called_once_with(2)

    @mock.patch("argo_probe_oai_pmh.validator.sys.exit")
    @mock.patch("argo_probe_oai_pmh.validator.print")
    @mock.patch("argo_probe_oai_pmh.validator.xml_schema_validation")
    @mock.patch("argo_probe_oai_pmh.validator.fetchXMLSchema")
    @mock.patch("argo_probe_oai_pmh.validator.fetchXML")
    def test_validate_XML_critical_content_nonverbose(
            self, mock_fetch_xml, mock_fetch_schema, mock_schema_validation,
            mock_print, mock_exit
    ):
        mock_fetch_xml.return_value = b"mock_xml", "text/xml; charset=UTF-8"
        mock_fetch_schema.return_value = b"mock_xml_schema"
        mock_schema_validation.return_value = False
        mock_print.side_effect = mock_func
        mock_exit.side_effect = mock_func
        mock_xml_content = mock.Mock()
        mock_xml_content_instance = mock_xml_content.return_value
        mock_xml_content_instance.validate.return_value = \
            "Missing element 'test'."
        mock_xml_content_instance.validate_admin_emails.return_value = None
        mock_xml_content_instance.get_admin_emails.return_value = \
            ["mock@email.com"]
        with mock.patch(
                "argo_probe_oai_pmh.validator.XMLContent", mock_xml_content
        ):
            self.nonverbose_validator.validate()
        self.assertEqual(mock_fetch_xml.call_count, 2)
        mock_fetch_xml.assert_has_calls([
            mock.call(url="mock_url?Identify", timeout=30),
            mock.call(url="mock_url", timeout=30)
        ], any_order=True)
        mock_fetch_schema.assert_called_once_with(
            url="http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd", timeout=30
        )
        mock_schema_validation.assert_called_once()
        mock_print.assert_called_once_with(
            "CRITICAL - Content XML not valid - Missing element 'test'.\n"
            "XML does not comply with OAI-PMH XML Schema "
            "http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd"
        )
        mock_exit.assert_called_once_with(2)

    @mock.patch("argo_probe_oai_pmh.validator.sys.exit")
    @mock.patch("argo_probe_oai_pmh.validator.print")
    @mock.patch("argo_probe_oai_pmh.validator.xml_schema_validation")
    @mock.patch("argo_probe_oai_pmh.validator.fetchXMLSchema")
    @mock.patch("argo_probe_oai_pmh.validator.fetchXML")
    def test_validate_XML_xmlschema_fetch_error_content_verbose(
            self, mock_fetch_xml, mock_fetch_schema, mock_schema_validation,
            mock_print, mock_exit
    ):
        mock_fetch_xml.return_value = b"mock_xml", "text/xml; charset=UTF-8"
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
            mock.call(url="mock_url?Identify", timeout=30),
            mock.call(url="mock_url", timeout=30)
        ], any_order=True)
        mock_fetch_schema.assert_called_once_with(
            url="http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd", timeout=30
        )
        self.assertFalse(mock_schema_validation.called)
        mock_print.assert_called_once_with(
            "CRITICAL - Unable to fetch OAI-PMH XML Schema "
            "http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd - "
            "schema compliance not tested: Error fetching XML schema : "
            "500 SERVER ERROR"
        )
        mock_exit.assert_called_once_with(2)

    @mock.patch("argo_probe_oai_pmh.validator.sys.exit")
    @mock.patch("argo_probe_oai_pmh.validator.print")
    @mock.patch("argo_probe_oai_pmh.validator.xml_schema_validation")
    @mock.patch("argo_probe_oai_pmh.validator.fetchXMLSchema")
    @mock.patch("argo_probe_oai_pmh.validator.fetchXML")
    def test_validate_XML_xmlschema_fetch_error_content_nonverbose(
            self, mock_fetch_xml, mock_fetch_schema, mock_schema_validation,
            mock_print, mock_exit
    ):
        mock_fetch_xml.return_value = b"mock_xml", "text/xml; charset=UTF-8"
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
            mock.call(url="mock_url?Identify", timeout=30),
            mock.call(url="mock_url", timeout=30)
        ], any_order=True)
        mock_fetch_schema.assert_called_once_with(
            url="http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd", timeout=30
        )
        self.assertFalse(mock_schema_validation.called)
        mock_print.assert_called_once_with(
            "CRITICAL - Unable to fetch OAI-PMH XML Schema "
            "http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd - "
            "schema compliance not tested: Error fetching XML schema : "
            "500 SERVER ERROR"
        )
        mock_exit.assert_called_once_with(2)
