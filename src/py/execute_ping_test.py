from prettytable import PrettyTable
import requests
import logging
import base64
import time
import yaml


CONFIG = None
CONFIG_FILE = "config/config.yml"
PING_TASK_FILE = "src/resources/ping-task.xml"


def load_config():
    global CONFIG
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        CONFIG = yaml.safe_load(f)


def load_ping_task():
    with open(PING_TASK_FILE, 'r') as f:
        return f.read()


def convert_report_to_simple_table_ping(input_report):
    table = {
        "header": ['Site', 'Ping Result']
    }

    pTable = PrettyTable(table['header'])
    pTable.add_row(["Total Responders", list(input_report.values()).count("pong-received")], divider=True)

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


def execute_ping_task(dsf_base_url, wait_result_secs_ping, b_send_results_confluence, confluence_api_base_url, confluence_page_id_ping, conf_user, conf_pw, dsf_cert_path, dsf_key_path):
    load_config()

    header = {
        'Content-Type': 'application/xml',
        'Accept': "application/json"
    }

    ping_task = load_ping_task()
    logging.info('Sending ping task to DSF')

    res = requests.post(f'{dsf_base_url}/Task', headers=header,
                        cert=(dsf_cert_path, dsf_key_path), data=ping_task)
    ping_task_id = res.json()['id']

    logging.info(f'Sleep for {wait_result_secs_ping} seconds to wait for results')
    time.sleep(int(wait_result_secs_ping))

    res = requests.get(f'{dsf_base_url}/Task/{ping_task_id}?_format=json',
                       headers=header, cert=(dsf_cert_path, dsf_key_path))
    ping_task_result = res.json()
    ping_results = {}

    for result in ping_task_result['output']:
        site_ident = result['extension'][0]['extension'][1]['valueIdentifier']['value']
        ping_result = result['valueCoding']['code']
        ping_results[site_ident] = ping_result

    ping_results = dict(sorted(ping_results.items()))
    report_table = convert_report_to_simple_table_ping(ping_results)
    logging.info(report_table)

    if b_send_results_confluence:
        send_result_to_confluence_ping(report_table, confluence_api_base_url, confluence_page_id_ping, conf_user, conf_pw)
