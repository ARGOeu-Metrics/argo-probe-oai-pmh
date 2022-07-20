import requests
from argo_probe_oai_pmh.exceptions import RequestException, \
    XMLRequestException, XMLSchemaRequestException
from argo_probe_oai_pmh.xml import parse_xml


def fetchData(url, timeout):
    try:
        response = requests.get(url, timeout=timeout)

        return response

    except (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError,
        requests.exceptions.RequestException,
        requests.exceptions.Timeout,
        requests.exceptions.TooManyRedirects
    ) as e:
        raise RequestException(e)


def fetchXML(url, timeout):
    try:
        response = fetchData(url, timeout)
        response.raise_for_status()

        tree, root, namespace = parse_xml(response.content)
        for item in root.iter():
            if item.tag == f"{namespace}error":
                msg = f"{item.text}"

                if item.get("code"):
                    msg = f"{item.get('code')}: {item.text}"

                raise XMLRequestException(msg=msg, title=url)

    except RequestException as e:
        raise XMLRequestException(msg=e, title=url)

    return response.content


def fetchXMLSchema(url, timeout):
    try:
        response = fetchData(url, timeout)
        response.raise_for_status()

        return response.content

    except RequestException as e:
        raise XMLSchemaRequestException(msg=e, title=url)
