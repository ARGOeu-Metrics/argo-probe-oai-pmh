import datetime
import io
import re

from argo_probe_oai_pmh.exceptions import XMLException
from lxml import etree


def namespace(element):
    m = re.match(r"\{.*\}", element.tag)
    return m.group(0) if m else ""


def xml_schema_validation(xml, schema):
    tree = etree.parse(io.BytesIO(xml))
    schema = etree.parse(io.BytesIO(schema))
    xml_schema = etree.XMLSchema(schema)

    return xml_schema.validate(tree.getroot())


class XMLContent:
    def __init__(self, xml, verb="Identify"):
        self.tree = etree.parse(io.BytesIO(xml))
        self.root = self.tree.getroot()
        self.namespace = namespace(self.root)
        self.verb = verb
        self.xml_string = xml
        self.elements = self._read()

    def _find_element(self, element):
        if self.verb not in [
            item.tag[len(self.namespace):] for item in self.root
        ]:
            raise XMLException(f"Missing '{self.verb}' element.")

        if element == "adminEmail":
            value = list()

        else:
            value = None

        for item in self.root:
            if item.tag[len(self.namespace):] == self.verb:
                for i in item:
                    if i.tag[len(self.namespace):] == element:
                        if element == "adminEmail":
                            value.append(i.text)

                        else:
                            value = i.text

        return value

    def _read(self):
        return {
            "repositoryName": self._find_element("repositoryName"),
            "baseURL": self._find_element("baseURL"),
            "protocolVersion": self._find_element("protocolVersion"),
            "earliestDatestamp": self._find_element("earliestDatestamp"),
            "deletedRecord": self._find_element("deletedRecord"),
            "granularity": self._find_element("granularity"),
            "adminEmail": self._find_element("adminEmail")
        }

    def is_present(self, element):
        if self.elements[element]:
            return True

        else:
            return False

    def validate(self):
        valid = True
        msg = ""

        elements = self._read()
        must_be_present = [
            "repositoryName", "baseURL", "protocolVersion", "earliestDatestamp",
            "deletedRecord", "granularity"
        ]

        missing_elements = list()
        for item in must_be_present:
            if not self.is_present(item):
                valid = False
                missing_elements.append(item)
                continue

            if item == "earliestDatestamp":
                date_format = ""
                if elements["granularity"] == "YYYY-MM-DD":
                    date_format = "%Y-%m-%d"
                elif elements["granularity"] == "YYYY-MM-DDThh:mm:ssZ":
                    date_format = "%Y-%m-%dT%H:%M:%SZ"
                try:
                    datetime.datetime.strptime(elements[item], date_format)

                except ValueError:
                    valid = False
                    msg = f"{msg}\nInvalid element '{item}'. " \
                          f"'{item}' must be expressed at the finest " \
                          f"granularity supported by the repository."
                    msg.strip("\n")

            if item == "deletedRecord":
                allowed_values = ["no", "transient", "persistent"]
                allowed_values_str = ", ".join(f"'{w}'" for w in allowed_values)
                if elements[item] not in allowed_values:
                    valid = False
                    msg = f"{msg}\nInvalid element '{item}'. Legitimate " \
                          f"values are {allowed_values_str}."
                    msg.strip("\n")

            if item == "granularity":
                allowed_values = ["YYYY-MM-DD", "YYYY-MM-DDThh:mm:ssZ"]
                allowed_values_str = ", ".join(f"'{w}'" for w in allowed_values)
                if elements[item] not in allowed_values:
                    valid = False
                    msg = f"{msg}\nInvalid element '{item}'. Legitimate " \
                          f"values are {allowed_values_str}."
                    msg.strip("\n")

        if len(missing_elements) == 1:
            msg = f"Missing element '{missing_elements[0]}.\n{msg}'"
            msg.strip("\n")

        elif len(missing_elements) > 1:
            msg_str = ", ".join(f"'{w}'" for w in missing_elements)
            msg = f"Missing elements: {msg_str}.\n{msg}"
            msg.strip("\n")

        if valid:
            return None

        else:
            return msg.strip("\n")

    def get_admin_emails(self):
        elements = self._read()
        return elements["adminEmail"]

    def validate_admin_emails(self):
        def validate_email_address(address):
            pat = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"

            if re.match(pat, address):
                return True

            else:
                return False

        valid = True
        msg = ""

        if self.is_present("adminEmail"):
            for email in self.elements["adminEmail"]:
                if not validate_email_address(email):
                    valid = False
                    msg = f"{msg}\nInvalid element 'adminEmail'. " \
                          f"Invalid email format."
                    msg.strip("\n")

        else:
            valid = False
            msg = f"{msg}\nMissing element 'adminEmail'."
            msg.strip("\n")

        if valid:
            return None

        else:
            return msg.strip("\n")
