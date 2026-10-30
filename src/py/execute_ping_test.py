from datetime import datetime, timezone

from prettytable import PrettyTable
import requests
import logging
import base64
import time
import yaml
import json


CONFIG = None
DSF_SITE_IDS = None
CONFIG_FILE = "config/config.yml"
PING_TASK_BASE_PATH = "src/resources/ping-task-"
ENDPOINT_STRING = "Endpoint?status=active&identifier=http://dsf.dev/sid/endpoint-identifier|"

def load_constants():
    load_config()

    global DSF_SITE_IDS
    DSF_SITE_IDS = json.loads(CONFIG["dsf-site-ids"])

def load_config():
    global CONFIG
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        CONFIG = yaml.safe_load(f)


def load_ping_task(task_version):
    file = f'{PING_TASK_BASE_PATH}{task_version}.json'
    try :
        with open(file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Template for Ping Task version {task_version} not found. Please contact your administrator.")
        return None


def convert_report_to_simple_table_ping(input_report):
    table = {
        "header": ['Site', 'Ping Result']
    }

    pTable = PrettyTable(table['header'])
    pTable.add_row(["Total pong-received", list(input_report.values()).count("pong-received")], divider=True)
    pTable.add_row(["Total pong-missing", list(input_report.values()).count("pong-missing")], divider=True)
    pTable.add_row(["Total not-reachable", list(input_report.values()).count("not-reachable")], divider=True)

    pTable.add_row(["Total not-reachable or missing from result", list(input_report.values()).count("not-reachable") + list(input_report.values()).count("missing")], divider=True)
    pTable.add_row(["Total not-allowed",list(input_report.values()).count("not-allowed")], divider=True)
    for site_ident in input_report.keys():
        ping_result = input_report[site_ident]
        table[site_ident] = [site_ident]
        table[site_ident].append(ping_result)
        pTable.add_row(table[site_ident])

    return pTable


def send_result_to_confluence_ping(report_table, confluence_api_base_url, confluence_page_id_ping, conf_user, conf_pw):

    page_info = CONFIG["ping-page-content-html"]

    table_html = report_table.get_html_string()
    page_info = f'{page_info}{table_html}<br></br>'

    base64_bytes = base64.b64encode(f'{conf_user}:{conf_pw}'.encode('ascii'))
    base64_message = base64_bytes.decode('ascii')
    header = {
        'Authorization': f'Basic {base64_message}',
        'Content-Type': 'application/json'
    }

    res = requests.get(f'{confluence_api_base_url}/content/{confluence_page_id_ping}',
                       headers=header)

    version_number = res.json()['version']['number']
    content_update = {
        'title': CONFIG["ping-page-title"],
        'type': 'page',
        'body': {'storage': {'value': page_info,
                             'representation': 'storage'
                             },
                 },
        'version': {'number': version_number + 1}
    }

    res = requests.put(f'{confluence_api_base_url}/content/{confluence_page_id_ping}',
                       headers=header, json=content_update)


def execute_ping_task(dsf_ping_process_version, dsf_hrp_ident, dsf_base_url, wait_result_secs_ping,
                      b_send_results_confluence, confluence_api_base_url, confluence_page_id_ping, conf_user, conf_pw,
                      dsf_cert_path, dsf_key_path, dsf_ping_download_resource_size, dsf_ping_pong_timeout_duration,
                      dsf_endpoint_id):
    load_config()
    load_constants()


    header = {
        'Content-Type': 'application/json',
        'Accept': "application/json"
    }
    ping_task = load_ping_task(dsf_ping_process_version)
    if not ping_task:
        return

    endpoint  = f'{ENDPOINT_STRING}{dsf_endpoint_id}'

    ping_task["authoredOn"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    ping_task["requester"]["identifier"]["value"] = dsf_hrp_ident
    ping_task["restriction"]["recipient"][0]["identifier"]["value"] = dsf_hrp_ident
    ping_task["input"][1]["valueString"] = endpoint

    if dsf_ping_process_version.startswith('2'):
        ping_task["input"][2]["valueDecimal"] = int(dsf_ping_download_resource_size)
        ping_task["input"][3]["valueString"] = dsf_ping_pong_timeout_duration

    if dsf_endpoint_id == "" or dsf_endpoint_id is None:
        dsf_endpoint_id = None
        ping_task["input"].pop(1)
    
    logging.info('Sending ping task to DSF')

    res = requests.post(f'{dsf_base_url}/Task', headers=header,
                        cert=(dsf_cert_path, dsf_key_path), json=ping_task)

    logging.debug(f'Response from DSF sending Ping: {res.text}')
    ping_task_id = res.json()['id']

    logging.debug(f'Sleep for {wait_result_secs_ping} seconds to wait for results')
    time.sleep(int(wait_result_secs_ping))

    res = requests.get(f'{dsf_base_url}/Task/{ping_task_id}?_format=json',
                       headers=header, cert=(dsf_cert_path, dsf_key_path))

    logging.debug(f'Response from DSF Ping Result: {res.text}')
    ping_task_result = res.json()
    ping_results = {}
    site_name_index = 1 if dsf_ping_process_version == '1.0' else 0
    for result in ping_task_result['output']:
        site_ident = result['extension'][0]['extension'][site_name_index]['valueIdentifier']['value']
        if site_ident not in dsf_site_ids:
            logging.info(f'No result requested for {site_ident}, hiding it from results.')
            continue
        ping_result = result['valueCoding']['code']
        ping_results[site_ident] = ping_result
    if not dsf_endpoint_id:
        for site_id in dsf_site_ids:
            if site_id not in ping_results.keys():
                ping_results[site_id] = "missing"
    ping_results = dict(sorted(ping_results.items()))
    report_table = convert_report_to_simple_table_ping(ping_results)
    logging.info(report_table)

    if b_send_results_confluence:
        send_result_to_confluence_ping(report_table, confluence_api_base_url, confluence_page_id_ping, conf_user, conf_pw)
