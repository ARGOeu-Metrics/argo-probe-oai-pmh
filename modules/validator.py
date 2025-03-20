import sys

from argo_probe_oai_pmh.data import get_xml_schema, get_xml, SCHEMA_URL
from argo_probe_oai_pmh.exceptions import XMLSchemaRequestException, \
    XMLRequestException, XMLException
from argo_probe_oai_pmh.output import Output
from argo_probe_oai_pmh.xml import XMLContent, xml_schema_validation


class Validator:
    def __init__(self, url, timeout, schema, verbose):
        self.url = url
        self.timeout = timeout
        self.output = Output()
        self.schema = schema
        self.verbose = verbose

    def _schema(self):
        return get_xml_schema(schema=self.schema)

    def _xml(self):
        return get_xml(url=self.url, timeout=self.timeout)

    def _xml4schema(self):
        return get_xml(url=self.url.split("?")[0], timeout=self.timeout)

    def validate(self):
        perfdata = ""
        try:
            xml, content_type, perfdata = self._xml()

            content = XMLContent(xml=xml)
            self.output.set_ok("HTTP status OK")

            if "text/xml" in content_type:
                self.output.set_ok("Content type text/xml")

                msgs = content.validate()

                if msgs:
                    self.output.set_critical(
                        "Content XML not valid - {}".format(msgs.strip("\n"))
                    )

                else:
                    self.output.set_ok("Content XML valid")

                xml2 = self._xml4schema()
                schema = self._schema()

                if xml_schema_validation(xml=xml2[0], schema=schema):
                    self.output.set_ok(
                        f"XML complies with OAI-PMH XML Schema {SCHEMA_URL}"
                    )

                else:
                    self.output.set_critical(
                        f"XML does not comply with OAI-PMH XML Schema "
                        f"{SCHEMA_URL}"
                    )

                if content.validate_admin_emails():
                    self.output.set_critical(content.validate_admin_emails())

                else:
                    admin_emails = content.get_admin_emails()
                    self.output.set_ok(
                        f"Valid adminEmail: {', '.join(admin_emails)}"
                    )

            else:
                self.output.set_critical(
                    "Content type not text/xml; charset=UTF-8"
                )

        except XMLSchemaRequestException as e:
            self.output.set_critical(
                f"Unable to read OAI-PMH XML Schema {self.schema} - "
                f"schema compliance not tested: {e}"
            )

        except XMLRequestException as e:
            self.output.set_critical(e)

        except XMLException as e:
            self.output.set_critical(e)

        output = self.output.get_message()
        output = output.split("\n")
        output[0] = f"{output[0]}{perfdata}"
        if not self.verbose and self.output.get_code() == self.output.OK:
            print(output[0])

        else:
            print("\n".join(output))

        sys.exit(self.output.get_code())
