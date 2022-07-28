# argo-probe-oai-pmh

The package contains generic probe for checking the validity of OAI-PMH response. The probe is checking if the return HTTP status code is ok, if the response is of the content type `text/xml`, and if the content has all the required elements described in [this document](http://www.openarchives.org/OAI/openarchivesprotocol.html#Identify). Furthermore, it is also tested if the response complies with the OAI-PMH XML Schema http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd.

## Synopsis

The probe has two mandatory argument, the endpoint URL, and timeout, which defaults 30 s if not specified otherwise. Verbosity of the output can be increased by using `-v` flag.

```
# /usr/libexec/argo/probes/oai_pmh/check_oai_pmh -h
usage: Probe that checks the validity of OAI-PMH response -u URL [-t TIMEOUT]
                                                          [-v] [-h]

required arguments:
  -u URL, --url URL     endpoint URL
  -t TIMEOUT, --timeout TIMEOUT
                        timeout

optional arguments:
  -v, --verbose         verbose output
  -h, --help            Show this help message and exit
```

Example execution of the probe:

```
# /usr/libexec/argo/probes/oai_pmh/check_oai_pmh -u https://dabar.srce.hr/oai?verb=Identify -t 30
OK - XML is valid.
```

Example execution of the probe with increased verbosity:

```
# /usr/libexec/argo/probes/oai_pmh/check_oai_pmh -u https://dabar.srce.hr/oai?verb=Identify -t 30 -v
OK - XML is valid.
HTTP status OK.
Content type text/xml
Content XML valid.
XML complies with OAI-PMH XML Schema http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd
Valid adminEmail: dabar@srce.hr
```
