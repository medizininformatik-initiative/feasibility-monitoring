from prettytable import PrettyTable
import requests
import logging
import csv

process_name_to_plugin_map = {
    "Report Autostart": "mii-process-report",
    "Report Send": "mii-process-report",
    "Report Receive": "mii-process-report",
    "FeasibilityRequest": "mii-process-feasibility",
    "ExecuteFeasibility": "mii-process-feasibility",
    "dataSend": "mii-process-data-transfer",
    "dataReceive": "mii-process-data-transfer",
    "Ping": "dsf-process-ping-pong",
    "Pong": "dsf-process-ping-pong",
    "PingAutostart": "dsf-process-ping-pong",
    "DownloadAllowList": "dsf-process-allowlist",
    "UpdateAllowList": "dsf-process-allowlist",
}


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


def convert_process_info_to_process_name(process):
    return f"{process['plugin']}|{process['name']}|{process['version']}"


def create_results_table(activity_information):

    process_list = []

    for site_ident in activity_information.keys():
        site_info = activity_information[site_ident]

        for process in site_info["installedProcesses"]:

            process_name_version = convert_process_info_to_process_name(process)

            if process_name_version not in process_list:
                process_list.append(process_name_version)

        process_list_overall = [0] * len(process_list)
        site_process_lists = []

    process_list = sorted(process_list)

    for site_ident in activity_information.keys():
        site_info = activity_information[site_ident]
        site_process_list = [0] * len(process_list)

        for process_index in range(0, len(process_list)):

            process = process_list[process_index]
            for installed_process in site_info["installedProcesses"]:

                process_name_version = convert_process_info_to_process_name(installed_process)

                if process == process_name_version:
                    site_process_list[process_index] = 1
                    process_list_overall[process_index] = process_list_overall[process_index] + 1
                    break

        site_process_lists.append([site_ident] + site_process_list)

    table = []

    table.append(["Site Identifier"] + process_list)
    table.append(["Overall"] + process_list_overall)

    for site_process_list in site_process_lists:
        table.append(site_process_list)

    return table


def map_process_name_to_plugin(process_name):

    if process_name not in process_name_to_plugin_map:
        return "unknown-process"
    else:
        return process_name_to_plugin_map[process_name]


def create_activity_list_and_add_to_org(
    organization_list, organization, endpoint, activity_definitions
):
    activity_definition_list = []

    for activity_definition in activity_definitions:

        activity_definition = activity_definition["resource"]

        if "url" not in activity_definition:
            logging.error(f"ERROR - broken activity defnition in endpoint {endpoint}")
            continue

        activity_definition_list.append(
            {
                "url": activity_definition["url"],
                "name": activity_definition["name"],
                "plugin": map_process_name_to_plugin(activity_definition["name"]),
                "version": activity_definition["version"],
                "status": activity_definition["status"],
            }
        )

    organization_list[organization["resource"]["identifier"][0]["value"]] = {
        "endpoint": endpoint,
        "installedProcesses": activity_definition_list,
    }


def generate_activity_list_for_orgs(
    organization_list, organizations, dsf_base_url, dsf_cert_path, dsf_key_path
):
    for organization in organizations:

        org_ident = organization["resource"]["identifier"][0]["value"]

        if "endpoint" not in organization["resource"]:
            continue

        endpoint = requests.get(
            f'{dsf_base_url}/{organization["resource"]["endpoint"][0]["reference"]}?_format=json',
            cert=(dsf_cert_path, dsf_key_path),
        ).json()["address"]

        logging.info(f"Querying endpoint: {endpoint} for org: {org_ident}")

        try:
            activity_def_req_res = requests.get(
                f"{endpoint}/ActivityDefinition?_format=json",
                cert=(dsf_cert_path, dsf_key_path),
                timeout=10,
            )
            activity_definitions = page_through_results_and_collect(
                activity_def_req_res, dsf_cert_path, dsf_key_path
            )

        except requests.exceptions.RequestException:
            logging.debug(f"Could not connect to endpoint {endpoint}")
            organization_list[org_ident] = {
                "endpoint": endpoint,
                "installedProcesses": [],
                "errors": [
                    {
                        "code": "connection-error",
                        "display": "Could not connect to endpoint",
                    }
                ],
            }

            continue

        create_activity_list_and_add_to_org(
            organization_list, organization, endpoint, activity_definitions
        )


def save_results_to_disk(table):

    with open("reports/dsf_installed_plugins.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for row in table:
            writer.writerow(row)


def execute_collect_activity_definitions(dsf_base_url, dsf_cert_path, dsf_key_path):

    organization_list = {}
    organizations_req_res = requests.get(
        f"{dsf_base_url}/Organization?_format=json",
        cert=(dsf_cert_path, dsf_key_path),
        timeout=20,
    )
    organizations = page_through_results_and_collect(
        organizations_req_res, dsf_cert_path, dsf_key_path
    )

    generate_activity_list_for_orgs(
        organization_list, organizations, dsf_base_url, dsf_cert_path, dsf_key_path
    )
    sorted_orgs_list = dict(sorted(organization_list.items()))
    table = create_results_table(sorted_orgs_list)
    save_results_to_disk(table)
