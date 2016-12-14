#!/usr/bin/env python3
import json
import requests

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
    return
