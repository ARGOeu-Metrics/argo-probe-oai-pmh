import unittest

from argo_probe_oai_pmh.nagios import NagiosResponse


class NagiosResponseTests(unittest.TestCase):
    def setUp(self):
        self.nagios = NagiosResponse()

    def test_ok_msg(self):
        self.nagios.set_ok("Response XML is valid.")
        self.assertEqual(self.nagios.get_code(), 0)
        self.assertEqual(
            self.nagios.get_message(),
            "OK - XML is valid.\nResponse XML is valid."
        )

    def test_multiline_ok_msg(self):
        self.nagios.set_ok("\nResponse XML is valid.\nContent is valid.\n")
        self.assertEqual(self.nagios.get_code(), 0)
        self.assertEqual(
            self.nagios.get_message(),
            "OK - XML is valid.\nResponse XML is valid.\nContent is valid."
        )

    def test_multiple_ok_msgs(self):
        self.nagios.set_ok("Response XML is OK.")
        self.nagios.set_ok("Content is valid.")
        self.nagios.set_ok("XML complies with schema.")
        self.assertEqual(self.nagios.get_code(), 0)
        self.assertEqual(
            self.nagios.get_message(),
            "OK - XML is valid.\nResponse XML is OK.\nContent is valid.\n"
            "XML complies with schema."
        )

    def test_warning_msg(self):
        self.nagios.set_warning("Response XML is not completely valid.")
        self.assertEqual(self.nagios.get_code(), 1)
        self.assertEqual(
            self.nagios.get_message(),
            "WARNING - Response XML is not completely valid."
        )

    def test_warning_multiline_msg(self):
        self.nagios.set_warning(
            "\nResponse XML is not completely valid.\nNot valid."
        )
        self.assertEqual(self.nagios.get_code(), 1)
        self.assertEqual(
            self.nagios.get_message(),
            "WARNING - Response XML is not completely valid.\nNot valid."
        )

    def test_critical_msg(self):
        self.nagios.set_critical("Response XML is not completely valid.")
        self.assertEqual(self.nagios.get_code(), 2)
        self.assertEqual(
            self.nagios.get_message(),
            "CRITICAL - Response XML is not completely valid."
        )

    def test_critical_multiline_msg(self):
        self.nagios.set_critical(
            "\nResponse XML is not completely valid.\nNot valid."
        )
        self.assertEqual(self.nagios.get_code(), 2)
        self.assertEqual(
            self.nagios.get_message(),
            "CRITICAL - Response XML is not completely valid.\nNot valid."
        )

    def test_unknown_msg(self):
        self.nagios.set_unknown("An unexpected error has occurred.")
        self.assertEqual(self.nagios.get_code(), 3)
        self.assertEqual(
            self.nagios.get_message(),
            "UNKNOWN - An unexpected error has occurred."
        )

    def test_unknown_multiline_msg(self):
        self.nagios.set_unknown(
            "\nAn unexpected error has occurred.\n"
            "Something unexpected happened."
        )
        self.assertEqual(self.nagios.get_code(), 3)
        self.assertEqual(
            self.nagios.get_message(),
            "UNKNOWN - An unexpected error has occurred.\n"
            "Something unexpected happened."
        )

    def test_mixed_msgs_crit_ok(self):
        self.nagios.set_ok("The response HTTP status is OK.")
        self.nagios.set_ok("Content XML OK.")
        self.nagios.set_critical("XML format does not comply with the schema.")
        self.nagios.set_ok("Valid adminEmail test@example.com.")
        self.assertEqual(self.nagios.get_code(), 2)
        self.assertEqual(
            self.nagios.get_message(),
            "CRITICAL - XML format does not comply with the schema."
        )

    def test_mixed_msgs_crit_warn_ok(self):
        self.nagios.set_ok("The response HTTP status is OK.")
        self.nagios.set_warning("Content XML warning.")
        self.nagios.set_critical("XML format does not comply with the schema.")
        self.nagios.set_ok("Valid adminEmail test@example.com.")
        self.assertEqual(self.nagios.get_code(), 2)
        self.assertEqual(
            self.nagios.get_message(),
            "CRITICAL - XML format does not comply with the schema."
        )

    def test_mixed_msgs_warn_ok(self):
        self.nagios.set_ok("The response HTTP status is OK.")
        self.nagios.set_ok("Content XML OK.")
        self.nagios.set_warning("XML format does not comply with the schema.")
        self.nagios.set_ok("Valid adminEmail test@example.com.")
        self.assertEqual(self.nagios.get_code(), 1)
        self.assertEqual(
            self.nagios.get_message(),
            "WARNING - XML format does not comply with the schema."
        )

    def test_mixed_msgs_unknown(self):
        self.nagios.set_warning("The response HTTP status is 201.")
        self.nagios.set_ok("Content XML OK.")
        self.nagios.set_critical("XML format does not comply with the schema.")
        self.nagios.set_unknown("An unexpected error has occurred.")
        self.nagios.set_ok("Valid adminEmail test@example.com.")
        self.assertEqual(self.nagios.get_code(), 3)
        self.assertEqual(
            self.nagios.get_message(),
            "UNKNOWN - An unexpected error has occurred."
        )
