from prettytable import PrettyTable
import requests
import logging
import csv
import json


def get_next_link(link_elem):
    for elem in link_elem:
        if elem["relation"] == "next":
            return elem["url"]

    return None


def page_through_results_and_collect(resp, dsf_cert_path, dsf_key_path):

    result_entry = []

    if resp.status_code != 200:
        return result_entry

    next_link = get_next_link(resp.json()["link"])
    if "entry" not in resp.json().keys():
        return result_entry
    if len(resp.json()["entry"]) > 0:
        result_entry = result_entry + resp.json()["entry"]

    if next_link:
        logging.debug(f"Getting next page {next_link}")
        resp = requests.get(next_link, cert=(dsf_cert_path, dsf_key_path))
        if "entry" not in resp.json().keys():
            return result_entry

        return result_entry + page_through_results_and_collect(resp, dsf_cert_path, dsf_key_path)

    return result_entry


def create_results_table(reports):

    table = []

    table.append(["Site Identifier", "Last Report"])

    for site_ident in reports.keys():
        table.append([site_ident, reports[site_ident]])

    return table


def save_results_to_disk(table):

    with open("reports/last_kds_reports.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for row in table:
            writer.writerow(row)


def execute_collect_report_overview(dsf_base_url, dsf_cert_path, dsf_key_path):

    report_list = {}
    report_req_res = requests.get(
        f"{dsf_base_url}/Bundle?_format=json&_profile=http://medizininformatik-initiative.de/fhir/Bundle/search-bundle-response-report|1.0",
        cert=(dsf_cert_path, dsf_key_path),
        timeout=20,
    )

    print(report_req_res.status_code)

    reports = page_through_results_and_collect(
        report_req_res, dsf_cert_path, dsf_key_path
    )

    for report in reports:
        report_list[report['resource']['identifier']['value']] = report['resource']['meta']['lastUpdated'][0:10]

    results_table = create_results_table(report_list)
    save_results_to_disk(results_table)

    print(json.dumps(report_list))
