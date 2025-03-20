import requests
from argo_probe_oai_pmh.exceptions import RequestException, \
    XMLRequestException, XMLSchemaRequestException

SCHEMA_URL = "https://www.openarchives.org/OAI/2.0/OAI-PMH.xsd"


def _get_data(url, timeout):
    try:
        response = requests.get(url, timeout=timeout)

        perfdata = (f"|time={response.elapsed.total_seconds()}s;"
                    f"size={len(response.content)}B")

        return response, perfdata

    except (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError,
        requests.exceptions.RequestException,
        requests.exceptions.Timeout,
        requests.exceptions.TooManyRedirects
    ) as e:
        raise RequestException(e)


def get_xml(url, timeout):
    try:
        response, perfdata = _get_data(url, timeout)
        content_type = response.headers["content-type"]
        response.raise_for_status()

    except RequestException as e:
        raise XMLRequestException(msg=e, title=url)

    return response.content, content_type, perfdata


def get_xml_schema(schema):
    try:
        with open(schema, "rb") as f:
            data = f.read()

        return data

    except FileNotFoundError:
        raise XMLSchemaRequestException(f"File {schema} does not exist")

