<?php

function getCertsFromAPI($search = "")
{
    if (empty($search)) {
        die("empty search pattern");
    }
    $string = file_get_contents("https://crt.sh/atom?q=" . $search);
    return $string;
}

function extractFromRSS($rssFeed)
{
    $offset = 0;
    $certs = array();
    while ($startPos = strpos($rssFeed, "-----BEGIN CERTIFICATE-----", $offset)) {
        $endPos = strpos($rssFeed, "-----END CERTIFICATE-----", $startPos);
        $lenght = $endPos - $startPos + strlen("-----END CERTIFICATE-----");
        $offset = $endPos;
        array_push($certs, substr($rssFeed, $startPos, $lenght));
    }
    return $certs;
}

function parseCert($certString)
{
    $certString = urldecode($certString);
    $certString = str_replace("&lt;br&gt;", "\n", $certString);
    $certString = str_replace(" ", "+", $certString);
    $certString = str_replace("+CERTIFICATE-----", " CERTIFICATE-----", $certString);
    $cert = openssl_x509_read($certString);
    $certInfo = openssl_x509_parse($cert);
    return $certInfo;
}

function getSubjectAndAltNames($certInfo)
{
    $names = array();
    array_push($names, $certInfo["subject"]["CN"]);
    if (isset($certInfo["extensions"]["subjectAltName"])) {
        $altNames = explode(",", $certInfo["extensions"]["subjectAltName"]);
        foreach ($altNames as $key => $value) {
            $nameToAdd = trim($value);
            $nameToAdd = str_replace("DNS:", "", $nameToAdd);
            array_push($names, $nameToAdd);
        }
    }
    return array_unique($names);
}

function getUniqueDomains($names)
{
    $domains = array();
    foreach ($names as $key => $value) {
        $components = explode(".", $value);
        $numberOfComponents = count($components);
        if ($numberOfComponents < 2) {
            die("one of the cert domain names is not valid (or is TLD)");
        }
        $domainToAdd = $components[$numberOfComponents - 2] . "." . $components[$numberOfComponents - 1];
        array_push($domains, $domainToAdd);
    }
    $domains = array_unique($domains);
    sort($domains);
    return $domains;
}

function searchForSubDomains($search = "")
{
    $domains = array();
    $certs = extractFromRSS(getCertsFromAPI($search));
    foreach ($certs as $key => $cert) {
        $domainList = getSubjectAndAltNames(parseCert($cert));
        foreach ($domainList as $key => $singleDomain) {
            array_push($domains, $singleDomain);
        }
    }
    $uniqueSubDomains = array_unique($domains);
    return $uniqueSubDomains;
}

function searchForDomains($search = "")
{
    $domains = getUniqueDomains(searchForSubDomains($search));
    return $domains;
}

function outputJSON($a1)
{
    $a2 = array_merge($a1); // reseting the indexes in array
    return json_encode($a2);
}

function subdomainsOfSpecificDomain($searchDomain)
{
    $initialList = searchForSubDomains("%." . $searchDomain);
    $subdomains = array();
    $domainLenght = strlen($searchDomain);
    foreach ($initialList as $key => $value) {
        $offset = strlen($value) - $domainLenght - 1;
        if ($offset < 0) {
            $offset = 0;
        }
        if (strpos($value, "." . $searchDomain, $offset)) {
            array_push($subdomains, $value);
        }
    }
    return $subdomains;
}
