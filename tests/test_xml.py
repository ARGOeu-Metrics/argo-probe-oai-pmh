import unittest

from argo_probe_oai_pmh.exceptions import XMLException
from argo_probe_oai_pmh.xml import XMLContent

ok_xml_string = \
    b'<?xml version="1.0" encoding="UTF-8"?>' \
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

xml_string_missing_entries = ok_xml_string.replace(
    b"<baseURL>http://memory.loc.gov/cgi-bin/oai</baseURL>"
    b"<protocolVersion>2.0</protocolVersion>", b""
)

xml_string_missing_verb = \
    b'<?xml version="1.0" encoding="UTF-8"?>' \
    b'<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" ' \
    b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"' \
    b' xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/' \
    b' http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">' \
    b'<responseDate>2002-02-08T12:00:01Z</responseDate>' \
    b'<request verb="Identify">http://memory.loc.gov/cgi-bin/oai</request>' \
    b'</OAI-PMH>'

xml_string_invalid_datestamp = ok_xml_string.replace(
    b"<earliestDatestamp>1990-02-01T12:00:00Z</earliestDatestamp>",
    b"<earliestDatestamp>1990-02-01</earliestDatestamp>"
)

xml_string_invalid_deleted = ok_xml_string.replace(
    b"<deletedRecord>transient</deletedRecord>",
    b"<deletedRecord>meh</deletedRecord>"
)

xml_string_invalid_granularity = ok_xml_string.replace(
    b"<granularity>YYYY-MM-DDThh:mm:ssZ</granularity>",
    b"<granularity>YYY-MM-DDThh:mm:ssZ</granularity>"
)

xml_string_missing_emails = ok_xml_string.replace(
    b"<adminEmail>somebody@loc.gov</adminEmail>"
    b"<adminEmail>anybody@loc.gov</adminEmail>", b""
)

xml_string_invalid_email = ok_xml_string.replace(
    b"<adminEmail>somebody@loc.gov</adminEmail>"
    b"<adminEmail>anybody@loc.gov</adminEmail>",
    b"<adminEmail>somebody@loc</adminEmail>"
)


class XMLTests(unittest.TestCase):
    def setUp(self) -> None:
        self.xml_check = XMLContent(ok_xml_string)

    def test_read(self):
        self.assertEqual(
            self.xml_check._read(),
            {
                "repositoryName": "Library of Congress Open Archive Initiative "
                                  "Repository 1",
                "baseURL": "http://memory.loc.gov/cgi-bin/oai",
                "protocolVersion": "2.0",
                "earliestDatestamp": "1990-02-01T12:00:00Z",
                "deletedRecord": "transient",
                "granularity": "YYYY-MM-DDThh:mm:ssZ",
                "adminEmail": ["somebody@loc.gov", "anybody@loc.gov"]
            }
        )

    def test_read_with_missing_entries(self):
        xml_check = XMLContent(xml_string_missing_entries)
        self.assertEqual(
            xml_check._read(),
            {
                "repositoryName": "Library of Congress Open Archive Initiative "
                                  "Repository 1",
                "baseURL": None,
                "protocolVersion": None,
                "earliestDatestamp": "1990-02-01T12:00:00Z",
                "deletedRecord": "transient",
                "granularity": "YYYY-MM-DDThh:mm:ssZ",
                "adminEmail": ["somebody@loc.gov", "anybody@loc.gov"]
            }
        )

    def test_read_with_missing_verb(self):
        with self.assertRaises(XMLException) as context:
            XMLContent(xml_string_missing_verb)

        self.assertEqual(
            context.exception.__str__(),
            "Error analysing XML content: Missing 'Identify' element."
        )

    def test_validate_ok(self):
        self.assertEqual(self.xml_check.validate(), None)

    def test_validate_with_missing_entries(self):
        xml_check = XMLContent(xml_string_missing_entries)
        self.assertEqual(
            xml_check.validate(),
            "Missing elements: 'baseURL', 'protocolVersion'."
        )

    def test_validate_with_invalid_earliest_datestamp(self):
        xml_check = XMLContent(xml_string_invalid_datestamp)
        self.assertEqual(
            xml_check.validate(),
            "Invalid element 'earliestDatestamp'. "
            "'earliestDatestamp' must be expressed at the finest granularity "
            "supported by the repository."
        )

    def test_validate_with_invalid_deleted_record(self):
        xml_check = XMLContent(xml_string_invalid_deleted)
        self.assertEqual(
            xml_check.validate(),
            "Invalid element 'deletedRecord'. Legitimate values are 'no', "
            "'transient', 'persistent'."
        )

    def test_validate_with_invalid_granularity(self):
        xml_check = XMLContent(xml_string_invalid_granularity)
        self.assertEqual(
            xml_check.validate(),
            "Invalid element 'earliestDatestamp'. "
            "'earliestDatestamp' must be expressed at the finest granularity "
            "supported by the repository.\n"
            "Invalid element 'granularity'. Legitimate values are 'YYYY-MM-DD',"
            " 'YYYY-MM-DDThh:mm:ssZ'."
        )

    def test_get_admin_emails(self):
        self.assertEqual(
            self.xml_check.get_admin_emails(),
            ["somebody@loc.gov", "anybody@loc.gov"]
        )

    def test_validate_admin_emails(self):
        self.assertEqual(self.xml_check.validate_admin_emails(), None)

    def test_validate_missing_admin_emails(self):
        xml_check = XMLContent(xml_string_missing_emails)
        self.assertEqual(
            xml_check.validate_admin_emails(), "Missing element 'adminEmail'."
        )

    def test_validate_invalid_admin_emails(self):
        xml_check = XMLContent(xml_string_invalid_email)
        self.assertEqual(
            xml_check.validate_admin_emails(),
            "Invalid element 'adminEmail'. Invalid email format."
        )
