# argo-probe-oai-pmh

The package contains a generic probe for checking the validity of OAI-PMH response and an internal probe that is checking if the schema stored in the default location `/var/spool/argo/probe/oai_pmh/OAI-PMH.xsd` is up-to-date. 


## Synopsis

### `check_oai_pmh`

The probe is checking if the return HTTP status code is ok, if the response is of the content type `text/xml`, and if the content has all the required elements described in [this document](http://www.openarchives.org/OAI/openarchivesprotocol.html#Identify). Furthermore, it is also tested if the response complies with the OAI-PMH XML schema defined in a file located by default at `/var/spool/argo/probes/oai_pmh/OAI-PMH.xsd`, and which should reflect the contents defined at https://www.openarchives.org/OAI/2.0/OAI-PMH.xsd. The probe is using such schema defined in a file in order to avoid potential failures in case the page might be down.

The probe has two mandatory arguments, the endpoint URL, and timeout, which defaults to 30 s if not specified otherwise. You can also pass a file containing an XML schema for validating responses to OAI-PMH requests. By default, the package installs a file with such schema (as is defined at https://www.openarchives.org/OAI/2.0/OAI-PMH.xsd) to the default location `/var/spool/argo/probes/oai_pmh/OAI-PMH.xsd`. There is also an option to increase the verbosity of the probe's output by using `-v` flag.

```
# /usr/libexec/argo/probes/oai_pmh/check_oai_pmh -h
usage: Probe that checks the validity of OAI-PMH response -u URL [-t TIMEOUT] [-s SCHEMA] [-v] [-h]

required arguments:
  -u URL, --url URL     endpoint URL
  -t TIMEOUT, --timeout TIMEOUT
                        timeout

optional arguments:
  -s SCHEMA, --schema SCHEMA
                        File containing XML Schema for Validating Responses to OAI-PMH Requests (default: /var/spool/argo/probes/oai_pmh/OAI-PMH.xsd)
  -v, --verbose         verbose output
  -h, --help            Show this help message and exit
```

Example execution of the probe:

```
# /usr/libexec/argo/probes/oai_pmh/check_oai_pmh -u https://dabar.srce.hr/oai?verb=Identify -t 30
OK - XML is valid|time=1.617129s;size=1347B
```

Example execution of the probe with increased verbosity:

```
# /usr/libexec/argo/probes/oai_pmh/check_oai_pmh -u https://dabar.srce.hr/oai?verb=Identify -t 30 -v
OK - XML is valid|time=1.617129s;size=1347B
HTTP status OK
Content type text/xml
Content XML valid
XML complies with OAI-PMH XML Schema http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd
Valid adminEmail: dabar@srce.hr
```

### `check_xml_schema`

Probe `check_xml_schema` is designed to be an internal probe that is checking if the contents of the default (located at `/var/spool/argo/probes/oai_pmh/OAI-PMH.xsd`) file that contains XML validation schema are up-to-date with the definition at https://www.openarchives.org/OAI/2.0/OAI-PMH.xsd. The probe has a single required argument, `--user-agent`, which is the header entry for the request. The remaining two arguments have default values: `--url` defaults to `https://www.openarchives.org/OAI/2.0/OAI-PMH.xsd`, and the timeout defaults to 30 s.

```
# /usr/libexec/argo/probes/oai_pmh/check_xml_schema -h
usage: Internal probe that keeps OAI-PMH.xsd file up-to-date -a USER_AGENT [-u URL] [-t TIMEOUT] [-h]

required arguments:
  -a USER_AGENT, --user-agent USER_AGENT
                        user-agent entry for the request header

optional arguments:
  -u URL, --url URL     URL of the XML schema (default: https://www.openarchives.org/OAI/2.0/OAI-PMH.xsd)
  -t TIMEOUT, --timeout TIMEOUT
                        timeout
  -h, --help            Show this help message and exit
```

Example execution of the probe:

```
# /usr/libexec/argo/probes/oai_pmh/check_xml_schema --user-agent 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
OK - XML schema is up-to-date
```
