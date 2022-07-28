from distutils.core import setup


NAME = "argo-probe-oai-pmh"


def get_ver():
    try:
        for line in open(NAME + '.spec'):
            if "Version:" in line:
                return line.split()[1]

    except IOError:
        raise SystemExit(1)


setup(
    name=NAME,
    version=get_ver(),
    author="SRCE",
    author_email="kzailac@srce.hr",
    description="ARGO probe that checks validity of OAI-PMH XML response.",
    url="https://github.com/ARGOeu-Metrics/argo-probe-oai-pmh",
    package_dir={'argo_probe_oai_pmh': 'modules'},
    packages=['argo_probe_oai_pmh'],
    data_files=[('/usr/libexec/argo/probes/oai_pmh', ['src/check_oai_pmh'])]
)
