from prettytable import PrettyTable
from datetime import datetime
import requests
import base64
import json
import yaml
import time
import sys
import os


CONFIG = None
DSF_SITE_IDS = None
HISTORY_REPORT_FILE = "reports/history-report.json"
HISTORY_QUERY_FILE = "config/history-query.json"
INPUT_QUERIES_FILE = "config/input-queries.json"
CONFIG_FILE = "config/config.yml"


def load_config():
    global CONFIG
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        CONFIG = yaml.safe_load(f)


def load_constants():
    load_config()

    global DSF_SITE_IDS
    DSF_SITE_IDS = json.loads(CONFIG["dsf-site-ids"])


def load_json_file(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


def get_results(query_id, access_token, backend_base_url):
    run_query_path = "/query"
    header = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    resp = requests.get(
        f'{backend_base_url}{run_query_path}/{query_id}/detailed-result', headers=header)
    return resp.json()


def connect_to_keycloak(backend_client_id, client_secret, keycloak_token_url):
    backend_user_login = {'client_id': backend_client_id,
                          'grant_type': 'client_credentials',
                          'client_secret': client_secret,

                          }

    print(f'Getting access token from {keycloak_token_url}')
    resp = requests.post(keycloak_token_url,
                         data=backend_user_login)
    print(f'Token Status code: {resp.status_code}')
    access_token = resp.json()['access_token']
    return access_token


def send_test_query_and_get_id(access_token, sq, backend_base_url):
    header = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    run_query_path = "/query"
    print(f'Running query on backend: {backend_base_url}{run_query_path}')
    resp = requests.post(
        f'{backend_base_url}{run_query_path}', headers=header, json=sq)

    result_location = resp.headers['Location']
    query_id = result_location.rsplit('/', 1)[-1]
    return query_id


def convert_results(results):
    converted_results = {}

    for site in DSF_SITE_IDS:
        converted_results[site] = '.'

    for result in results["resultLines"]:
        if result["siteName"] not in DSF_SITE_IDS:
            continue

        n_patients = result['numberOfPatients']

        if n_patients >= 20:
            n_patients = "Yes"
        else:
            n_patients = "No"

        converted_results[result["siteName"]] = n_patients

    return dict(sorted(converted_results.items()))


def save_results_to_disk(query_report):

    report_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    with open(f'reports/feasibility_results-{report_time}.json', 'a+') as f:
        json.dump(query_report, f)


def append_percentage_fulfilled_column(site_module_yes_no_map, modules, optional_modules):
    fulfilled_100 = 0
    fulfilled_gt0 = 0
    fulfilled_0 = 0

    for site_url in DSF_SITE_IDS:
        site_yes_count = 0
        for column_name in modules:
            if site_module_yes_no_map[column_name][site_url] == "Yes" and column_name not in optional_modules:
                site_yes_count += 1

        non_optional_modules = (len(modules) - len(optional_modules))
        site_fulfilled = 100 if non_optional_modules == 0 else int(100 * site_yes_count / non_optional_modules)

        site_module_yes_no_map["percentage_fulfilled"][site_url] = str(site_fulfilled) + " %"
        if site_fulfilled == 100:
            fulfilled_100 += 1
        elif site_fulfilled > 0:
            fulfilled_gt0 += 1
        else:
            fulfilled_0 += 1
    site_module_yes_no_map["percentage_fulfilled"]["total_yes"] = fulfilled_100
    site_module_yes_no_map["percentage_fulfilled"]["total_no"] = fulfilled_gt0
    site_module_yes_no_map["percentage_fulfilled"]["total_na"] = fulfilled_0


def create_columns(query_reports, column_names, optional_modules, column_attribute):
    site_module_yes_no_map = {column_name: {"total_yes": 0, "total_no": 0, "total_na": 0} for column_name in column_names}

    for query_report in query_reports:
        column_name = query_report[column_attribute]

        for site_url, converted_query_result in query_report["result"].items():

            if converted_query_result == "Yes":
                site_module_yes_no_map[column_name]["total_yes"] += 1
            elif converted_query_result == "No":
                site_module_yes_no_map[column_name]["total_no"] += 1
            else:
                site_module_yes_no_map[column_name]["total_na"] += 1

            site_module_yes_no_map[column_name][site_url] = converted_query_result

    if column_attribute == "module":
        module_names = list(filter(lambda x: x != "percentage_fulfilled", column_names))
        append_percentage_fulfilled_column(site_module_yes_no_map, module_names, optional_modules)
    return site_module_yes_no_map


def get_column_keys(report_results, column_attribute):
    column_keys = [report[column_attribute] for report in report_results]

    if column_attribute == "module":
        optional_modules = [query_report["module"] for query_report in filter(lambda x: x["optional"] is True, report_results)]
        sorted_query_modules = []
        for module in column_keys:
            if module not in optional_modules:
                sorted_query_modules.append(module)

        sorted_query_modules += optional_modules
        sorted_query_modules += ["percentage_fulfilled"]

        return sorted_query_modules, optional_modules
    else:
        return column_keys, []


# column_attribute can be date or module
def convert_to_table(report_results, column_attribute):
    row_keys = ["total_yes", "total_no", "total_na"] + list(DSF_SITE_IDS)
    column_keys, optional_column_keys = get_column_keys(report_results, column_attribute)
    columns = create_columns(report_results, column_keys, optional_column_keys, column_attribute)

    pTable = PrettyTable()
    first_column = ["Total Yes | 100% fullfilled", "Total No | >0% fullfilled", "Total Na | 0% fullfilled"] + list(DSF_SITE_IDS)
    pTable.add_column("Site URL", first_column)

    for column_key in column_keys:
        column = []
        for row_key in row_keys:
            column.append(columns[column_key][row_key])

        column_name = column_key + " (optional)" if column_key in optional_column_keys else column_key
        if column_name == "percentage_fulfilled":
            column_name = "% fulfilled"
        pTable.add_column(column_name, column)

    return pTable


def load_history_report():
    history_query = load_json_file(HISTORY_QUERY_FILE)

    if not os.path.isfile(HISTORY_REPORT_FILE):
        open(HISTORY_REPORT_FILE, "x")
    if os.path.isfile(HISTORY_REPORT_FILE) and os.path.getsize(HISTORY_REPORT_FILE) == 0:
        history_report = {"reports": [], "query": history_query}
        return history_report

    with open(HISTORY_REPORT_FILE, "r") as f:
        history_report = json.load(f)

        if history_report["query"] != history_query:
            raise ValueError("history report contains query that is not equal to the current history query")

        history_report["reports"].sort(key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"))
        return history_report


def update_and_save_history_report(history_report, new_result):
    now = datetime.now().strftime("%Y-%m-%d")
    new_history_result = {"date": now, "result": new_result}

    reports = history_report["reports"]
    most_recent_date = reports[len(reports)-1]["date"] if len(reports) > 0 else None

    if most_recent_date == now:
        reports[len(reports)-1] = new_history_result
    else:
        history_report["reports"].append(new_history_result)

    with open(HISTORY_REPORT_FILE, "w") as f:
        json.dump(history_report, f)


def send_table_to_conf(table, conf_user, conf_pw, conf_api_base_url, conf_page_id, page_title, page_content):
    table_html = table.get_html_string()
    page_content = f'{page_content}{table_html}<br></br>'

    base64_bytes = base64.b64encode(f'{conf_user}:{conf_pw}'.encode('ascii'))
    base64_message = base64_bytes.decode('ascii')
    header = {
        'Authorization': f'Basic {base64_message}',
        'Content-Type': 'application/json'
    }

    res = requests.get(f'{conf_api_base_url}/content/{conf_page_id}',
                       headers=header)

    version_number = res.json()['version']['number']
    content_update = {
        'title': page_title,
        'type': 'page',
        'body': {'storage': {'value': page_content,
                             'representation': 'storage'
                             },
                 },
        'version': {'number': version_number + 1}
    }
    res = requests.put(f'{conf_api_base_url}/content/{conf_page_id}',
                       headers=header, json=content_update)


def send_query_and_get_results(query, backend_base_url, backend_client_id, client_secret, keycloak_token_url, wait_result_secs_feas):
    access_token = connect_to_keycloak(backend_client_id, client_secret, keycloak_token_url)
    print(f'Sending query: {query}')
    query_id = send_test_query_and_get_id(access_token, query, backend_base_url)
    print(f'Query ID: {query_id}')
    print(f'Sleep for {wait_result_secs_feas} seconds to wait for results')
    sys.stdout.flush()
    time.sleep(int(wait_result_secs_feas))
    access_token = connect_to_keycloak(backend_client_id, client_secret, keycloak_token_url)
    return get_results(query_id, access_token, backend_base_url)


def execute_history_query(backend_base_url, backend_client_id, client_secret, keycloak_token_url, wait_result_secs_feas, conf_user, conf_pw,
                          confluence_api_base_url, confluence_page_id_hist, send_results_confluence, history_table_len):
    load_constants()
    history_report = load_history_report()
    history_query = load_json_file(HISTORY_QUERY_FILE)
    results = send_query_and_get_results(history_query, backend_base_url, backend_client_id, client_secret, keycloak_token_url, wait_result_secs_feas)
    converted_result = convert_results(results)

    update_and_save_history_report(history_report, converted_result)

    history_table = convert_to_table(history_report["reports"][-int(history_table_len):], "date")
    print(history_table)

    if send_results_confluence:
        send_table_to_conf(history_table, conf_user, conf_pw, confluence_api_base_url, confluence_page_id_hist, CONFIG["hist-page-title"], CONFIG["hist-page-content-html"])


def execute_feas_test_queries(backend_base_url, backend_client_id, client_secret, keycloak_token_url, conf_user, conf_pw,
                              confluence_api_base_url, confluence_page_id_feas, wait_result_secs_feas, send_results_confluence):
    load_constants()
    queries = load_json_file(INPUT_QUERIES_FILE)

    for query in queries['queries']:
        results = send_query_and_get_results(query["sq"], backend_base_url, backend_client_id, client_secret, keycloak_token_url, wait_result_secs_feas)
        query['result'] = convert_results(results)

    report_table = convert_to_table(queries["queries"], "module")
    print(report_table)

    if send_results_confluence:
        send_table_to_conf(report_table, conf_user, conf_pw, confluence_api_base_url, confluence_page_id_feas, CONFIG["feas-page-title"], CONFIG["feas-page-content-html"])

    save_results_to_disk(queries)
