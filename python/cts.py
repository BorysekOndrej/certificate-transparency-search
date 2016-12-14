#!/usr/bin/env python3
import json
import requests
import xml.etree.ElementTree as ET
from html import unescape

debug = False

def quick_search(pattern = ""):
    subdomains = {}
    certs_id = {}
    req_url = "https://crt.sh/?q="+pattern+"&output=json"
    if not debug:
        req = requests.get(req_url)
        if req.status_code != 200:
            print("! Request for quick/basic search failed.")
            print("! Possible problems: network issues or too many certs match pattern.")
            exit(1)
        req_response = "["+req.text.replace("}{", "},{")+"]"
    else:
        with open('quick_search.json', 'r') as f:
            file_contents = f.read()
            req_response = "["+file_contents.replace("}{", "},{")+"]"
    data = json.loads(req_response)
    for single_cert in data:
        subdomains[single_cert["name_value"]] = True
        certs_id[single_cert["min_cert_id"]] = True 
    return (sorted(subdomains), sorted(certs_id))

def quick_search_print_subdomains(pattern = ""):
    subdomains = sorted(quick_search(pattern)[0])
    for single in subdomains:
        print(single)
    return subdomains

def full_search_via_rss(pattern = ""):
    certs = []
    if not debug:
        req_url = "https://crt.sh/atom?q="+pattern
        req = requests.get(req_url)
        if req.status_code != 200:
            print("! Request for full search via RSS failed.")
            print("! Possible problems: network issues or too many certs match pattern.")
            exit(1)
        req_response = req.text
    else:
        with open('rss.xml', 'r') as f:
            req_response = f.read()
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


