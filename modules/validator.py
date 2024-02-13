import sys

from argo_probe_oai_pmh.data import get_xml_schema, get_xml
from argo_probe_oai_pmh.exceptions import XMLSchemaRequestException, \
    XMLRequestException, XMLException
from argo_probe_oai_pmh.nagios import NagiosResponse
from argo_probe_oai_pmh.xml import XMLContent, xml_schema_validation


class Validator:
    def __init__(self, url, timeout, verbose):
        self.url = url
        self.timeout = timeout
        self.nagios = NagiosResponse()
        self.schema = "http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd"
        self.verbose = verbose

    def _schema(self):
        return get_xml_schema(url=self.schema, timeout=self.timeout)

    def _xml(self):
        return get_xml(url=self.url, timeout=self.timeout)

    def _xml4schema(self):
        return get_xml(url=self.url.split("?")[0], timeout=self.timeout)

    def validate(self):
        perfdata = ""
        try:
            xml, content_type, perfdata = self._xml()

            content = XMLContent(xml=xml)
            self.nagios.set_ok("HTTP status OK")

            if "text/xml" in content_type:
                self.nagios.set_ok("Content type text/xml")

                msgs = content.validate()

                if msgs:
                    self.nagios.set_critical(
                        "Content XML not valid - {}".format(msgs.strip("\n"))
                    )

                else:
                    self.nagios.set_ok("Content XML valid")

                xml2 = self._xml4schema()[0]
                schema = self._schema()[0]

                if xml_schema_validation(xml=xml2[0], schema=schema):
                    self.nagios.set_ok(
                        f"XML complies with OAI-PMH XML Schema {self.schema}"
                    )

                else:
                    self.nagios.set_critical(
                        f"XML does not comply with OAI-PMH XML Schema "
                        f"{self.schema}"
                    )

                if content.validate_admin_emails():
                    self.nagios.set_critical(content.validate_admin_emails())

                else:
                    admin_emails = content.get_admin_emails()
                    self.nagios.set_ok(
                        f"Valid adminEmail: {', '.join(admin_emails)}"
                    )

            else:
                self.nagios.set_critical(
                    "Content type not text/xml; charset=UTF-8"
                )

        except XMLSchemaRequestException as e:
            self.nagios.set_critical(
                f"Unable to fetch OAI-PMH XML Schema {self.schema} - "
                f"schema compliance not tested: {e}"
            )

        except XMLRequestException as e:
            self.nagios.set_critical(e)

        except XMLException as e:
            self.nagios.set_critical(e)

        output = self.nagios.get_message()
        output = output.split("\n")
        output[0] = f"{output[0]}{perfdata}"
        if not self.verbose and self.nagios.get_code() == self.nagios.OK:
            print(output[0])

        else:
            print("\n".join(output))

        sys.exit(self.nagios.get_code())
