# Certificate Transparency Search
[Certificate Transparency](https://www.certificate-transparency.org/) log contains a lot of information about issued SSL certificates. This data is public and accessible without any restrictions. Possibly used for research or for example for subdomain listing, as does this PoC.

It's based on [crt.sh](https://crt.sh/).

## PHP version (just PoC)

It's a quick and dirty botch, but it works.

Live: [https://borysek.eu/ct/](https://borysek.eu/ct/)

## Python version

Requires Python 3.5 or newer.

### Instalation
```bash
git clone https://github.com/BorysekOndrej/certificate-transparency-search.git
cd certificate-transparency-search/python
pip3 install -r requirements.txt
```

### Usage
```
python cts.py -h
usage: cts.py [-h] -d DOMAIN [-q] [-l] [-s]

If something is unclear, check the source code. ;)

optional arguments:
  -h, --help            show this help message and exit
  -d DOMAIN, --domain DOMAIN
                        Search for this domain name
  -q, --quick           Quick search only
  -l, --limitsubonly    Search only for subdomains of domain, not linked
                        domains and their subdomains.
  -s, --silent          Silence progress output.
```

### Example
```
python cts.py -d borysek.net --limitsubonly
```