#!/usr/bin/env python3

import json
import requests
import xml.etree.ElementTree as ET
from html import unescape
from OpenSSL import crypto
import argparse

silent = False


def parse_args():
    parser = argparse.ArgumentParser(
        description='If something is unclear, check the source code. ;)',
    )
    parser.add_argument('-d', '--domain', type=str, required=True, help="Search for this domain name")
    parser.add_argument('-q', '--quick', action="store_true", default=False, help="Quick search only")
    parser.add_argument('-l', '--limitsubonly', action="store_true", default=False, help="Search only for subdomains of domain, not linked domains and their subdomains.")
    parser.add_argument('-s', '--silent', action="store_true", default=False, help="Silence progress output.")
    return parser.parse_args()


def filter_only_subdomains(domain, candidates):
    result = []
    for single_domain in candidates:
        if single_domain.endswith("."+domain):
            result.append(single_domain)
    return result


def quick_search(pattern):
    subdomains = {}
    certs_id = {}
    req_url = "https://crt.sh/?q="+pattern+"&output=json"
    req = requests.get(req_url)
    if req.status_code != 200:
        print("! Request for quick/basic search failed.")
        print("! Possible problems: network issues or too many certs match pattern.")
        exit(1)
    req_response = "["+req.text.replace("}{", "},{")+"]"
    data = json.loads(req_response)
    for single_cert in data:
        subdomains[single_cert["name_value"]] = True
        certs_id[single_cert["min_cert_id"]] = True
    return (sorted(subdomains), sorted(certs_id))


def quick_search_for_linked(domain):
    return sorted(quick_search("%."+domain)[0])


def quick_search_for_subdomains(domain):
    domain_names = quick_search_for_linked(domain)
    return filter_only_subdomains(domain, domain_names)


def full_search_via_rss(pattern):
    certs = []
    req_url = "https://crt.sh/atom?q="+pattern
    req = requests.get(req_url)
    if req.status_code != 200:
        print("! Request for full search via RSS failed.")
        print("! Possible problems: network issues or too many certs match pattern.")
        exit(1)
    req_response = req.text
    req_response = req_response.replace('xmlns="http://www.w3.org/2005/Atom"', '')
    root = ET.fromstring(req_response)

    for node in root.iter('summary'):
        node_text = unescape(node.text)
        div_start_pos = node_text.find("<div")
        div_start_pos = node_text.find(">", div_start_pos) + 1
        div_end_pos = node_text.find("</div>")
        cert_text = node_text[div_start_pos:div_end_pos]
        cert_text = cert_text.replace("<br>", "\n")
        certs.append(cert_text)
    return list(set(certs))


def full_search_via_enumerating(id_list):
    certs = []
    for single_id in id_list:
        req_url = "https://crt.sh/?d="+str(single_id)
        req = requests.get(req_url)
        if req.status_code != 200:
            print("! Request for full search via RSS failed.")
            print("! Possible problems: network issues or too many certs match pattern.")
            exit(1)
        req_response = req.text
        certs.append(req_response)
    return certs


def full_search(pattern):
    if not silent:
        print("Starting full search")
        print("Checking if the number of matched certs is low enough for quick search")
    quick_search_result = quick_search(pattern)
    if not silent:
        print("There is", str(len(quick_search_result[1])), "of them,", end=" ")
    if len(quick_search_result[1]) < 1000:
        if not silent:
            print("that is low enough. Searching via RSS feed of crt.sh")
        search_result = full_search_via_rss(pattern)
    else:
        if not silent:
            print("that is too much. Searching via parsing donwloading single certs on crt.sh")
        search_result = full_search_via_enumerating(quick_search_result[1])
    if not silent:
        print("Done downloading search results. Returning all matched certs in PEM.")
    return search_result


def parse_single_cert_for_dns_names(cert_pem):
    dns_names = {}
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_pem)
    subject = cert.get_subject()
    dns_names[subject.CN] = True
    ext_count = cert.get_extension_count()
    for i in range(ext_count):
        ext_str = str(cert.get_extension(i))
        if "DNS:" in ext_str:
            splited_names = ext_str.split(",")
            for x in splited_names:
                dns_names[x.strip()[4:]] = True
    return dns_names


def parse_certs_for_dns_names(certs):
    if not silent:
        print("Starting parsing certs for DNS names")
    result = {}
    for single_cert in certs:
        single_result = parse_single_cert_for_dns_names(single_cert)
        result = {**result, **single_result}
        # prev. line is the new the jazz in Python 3.5. Replace this if you need to be backwards compatible.
    if not silent:
        print("Finished parsing certs for DNS names")
    return result


def search_for_linked(domain):
    certs = full_search("%."+domain)
    return sorted(parse_certs_for_dns_names(certs))


def search_for_subdomains(domain):
    domain_names = search_for_linked(domain)
    return filter_only_subdomains(domain, domain_names)


def output_list(lst):  # modify this to alter output format
    for x in lst:
        print(x)


if __name__ == "__main__":
    args = parse_args()
    domain = args.domain
    silent = args.silent
    if args.quick:
        if args.limitsubonly:
            output_list(quick_search_for_subdomains(domain))
        else:
            output_list(quick_search_for_linked(domain))
    else:
        if args.limitsubonly:
            output_list(search_for_subdomains(domain))
        else:
            output_list(search_for_linked(domain))
