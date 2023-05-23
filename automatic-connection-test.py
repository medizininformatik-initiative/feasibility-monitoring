import requests
import time
import base64
import argparse
from prettytable import PrettyTable
import json
from datetime import datetime
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--backend_base_url', help='base url of the feasibility backend',
                    default="https://localhost/api/v2")
parser.add_argument('--backend_client_id', help='backend client id',
                    nargs="?", default="feasibility-gui")
parser.add_argument('--backend_user', help='', nargs="?", default="test")
parser.add_argument('--client_secret', help='', nargs="?", default="test")
parser.add_argument('--keycloak_token_url', help='keycloak token url',
                    default="https://localhost/auth/realms/feasibility/protocol/openid-connect/token")
parser.add_argument('--confluence_api_base_url', help='', nargs="?",
                    default='https://myconfluence-rest-api-url')
parser.add_argument('--confluence_page_id', help='', nargs="?",
                    default='')
parser.add_argument('--send_results_confluence', help='', action='store_true',
                    default=False)
parser.add_argument('--conf_user', help='username of confluence account', nargs="?", default='username')
parser.add_argument('--conf_pw', help='password of confluence account', nargs="?", default='password')
parser.add_argument('--wait_result_secs', help='number of seconds to wait before results for a query are fetched', nargs="?", default='60')

args = vars(parser.parse_args())

backend_base_url = args["backend_base_url"]
backend_client_id = args["backend_client_id"]
backend_user = args["backend_user"]
client_secret = args["client_secret"]
keycloak_token_url = args["keycloak_token_url"]
confluence_api_base_url = args["confluence_api_base_url"]
confluence_page_id = args["confluence_page_id"]
send_results_confluence = args["send_results_confluence"]
conf_user = args["conf_user"]
conf_pw = args["conf_pw"]
wait_result_secs = args["wait_result_secs"]

site_list = ["UKA", "UKAU", "Charite", "UKB", "UKDD", "UKEr", "UKF", "UKFR","UKGI", "UMG", "UKH", "MHH", "UKHD", "UKJ", "UKL", "UKSH",
             "UMM", "KUM", "MRI", "UKR", "UKS", "UKT", "UKW", "UKU", "UKRUB","UKD", "UME", "UKE", "UKK", "UMMD", "UKMR", "UKM", "UM", "UKG", "UMR"]

site_list.sort()

site_consortia_mapping = {"Charite": "HiGHmed", "KUM": "DIFUTURE", "MHH": "HiGHmed", "MRI": "DIFUTURE", "UKA": "SMITH", "UKAU": "DIFUTURE", "UKB": "SMITH",
                          "UKD": "SMITH", "UKDD": "MIRACUM", "UKE": "SMITH", "UKEr": "MIRACUM", "UKF": "MIRACUM", "UKFR": "MIRACUM", "UKG": "MIRACUM", "UKGI": "MIRACUM",
                          "UKH": "SMITH", "UKHD": "HiGHmed", "UKJ": "SMITH", "UKK": "HiGHmed", "UKL": "SMITH", "UKM": "HiGHmed", "UKMR": "MIRACUM", "UKR": "DIFUTURE",
                          "UKRUB": "SMITH", "UKS": "DIFUTURE", "UKSH": "HiGHmed", "UKT": "DIFUTURE", "UKU": "DIFUTURE", "UKW": "HiGHmed", "UM": "MIRACUM",
                          "UME": "SMITH", "UMG": "HiGHmed", "UMM": "MIRACUM","UMMD": "MIRACUM", "UMR": "SMITH"}

site_list_ident_mapping = {"charite.de": "Charite", "unimedizin-mainz.de": "UM", "uniklinikum-jena.de": "UKJ", "uni-giessen.de": "UKGI", "ukhd.de": "UKHD", "ukm.de": "UKM", "kgu.de": "", "umm.de": "UMM", "umg.eu": "UMG", "uk-koeln.de": "UKK", "uk-augsburg.de": "UKAU", "ukaachen.de": "UKA", "mh-hannover.de": "MHH", "uksh.de": "UKSH", "uk-halle.de": "UKH", "ukw.de": "UKW",
                           "uniklinik-ulm.de": "UKU", "uke.de": "UKE", "uniklinik-freiburg.de": "UKFR", "medizin.uni-tuebingen.de": "UKT", "ukdd.de": "UKDD", "ukbonn.de": "UKB", "uniklinikum-leipzig.de": "UKL", "mri.tum.de": "MRI", "uni-marburg.de": "UKMR", "www.med.uni-magdeburg.de": "UMMD", "lmu-klinikum.de": "KUM", "uk-erlangen.de": "UKEr", "uk-essen.de": "UME", "www.medizin.uni-greifswald.de": "UKG", "ukr.de": "UKR"}


def connect_to_keycloak():
    backend_user_login = {'client_id': backend_client_id,
                          'grant_type': 'client_credentials',
                          'client_secret': client_secret,

                          }

    print(f'Getting access token from {keycloak_token_url}')
    resp = requests.post(keycloak_token_url, data=backend_user_login)
    print(f'Token Status code: {resp.status_code}')
    access_token = resp.json()['access_token']
    return access_token


def send_test_query_and_get_id(access_token, sq):

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


def get_results(query_id, access_token):

    run_query_path = "/query"
    header = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    resp = requests.get(
        f'{backend_base_url}{run_query_path}/{query_id}/detailed-result', headers=header)
    return resp.json()


def convert_results(results):

    result_list = {}
    for site in site_list:
        result_list[site] = -1

    for result in results['resultLines']:
        site_name = result['siteName']

        n_patients = result['numberOfPatients']

        if n_patients >= 20:
            n_patients = 20
        elif n_patients == 10:
            n_patients = 0

        if site_name in site_list_ident_mapping.keys():
            mapped_site_name = site_list_ident_mapping[site_name]
            result_list[mapped_site_name] = n_patients
        elif site_name in result_list:
            result_list[site_name] = n_patients

    return result_list


def save_results_to_disk(query_report):

    report_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    with open(f'reports/feasibility_results-{report_time}.json', 'a+') as f:
        new_entry = json.dumps(query_report)
        f.write(new_entry)
        f.write("\n")


def load_queries():
    with open('input-queries.json', 'r') as f:
        return json.load(f)


def create_info_result(number):
    if number == 20:
        return "YES"
    elif number == 0:
        return "no"
    else:
        return "."


def order_module_list(module_list, dict):
    ordered_list = []

    for module in module_list:
        ordered_list.append(dict[module])

    ordered_list.append(dict['overall'])
    return ordered_list


def convert_report_to_table(input_report):
    module_list = ["Patient", "Condition", "Laboratory",
                   "Procedure", "Consent", "Medication", "Specimen"]
    mandatory_modules = ["Patient", "Condition",
                         "Laboratory", "Procedure", "Consent"]
    table = {
        "header": ['Consortium', 'Site']
    }

    table['overall'] = {}
    table['totalYes'] = {"overall": 0}
    table['totalNo'] = {"overall": 0}
    table['totalNa'] = {"overall": 0}

    for query in input_report['queries']:
        header_entry = query['module']
        if query['module'] not in mandatory_modules:
            header_entry = f'{header_entry} (optional)'

        table['header'].append(header_entry)
        table['totalYes'][query['module']] = 0
        table['totalNo'][query['module']] = 0
        table['totalNa'][query['module']] = 0

    table['header'].append("% fulfilled non-optional")

    for site in site_list:
        table['overall'][site] = 0
        table[site] = [site_consortia_mapping[site], site]

        for query in input_report['queries']:

            if query['result'][site] == 20:
                if query['module'] in mandatory_modules:
                    table['overall'][site] = table['overall'][site] + 1
                table['totalYes'][query['module']
                                  ] = table['totalYes'][query['module']] + 1
            elif query['result'][site] == 0:
                table['totalNo'][query['module']
                                 ] = table['totalNo'][query['module']] + 1
            else:
                table['totalNa'][query['module']
                                 ] = table['totalNa'][query['module']] + 1

            table[site].append(create_info_result(query['result'][site]))

        percentage_fulfilled = (
            table['overall'][site] / len(mandatory_modules)) * 100
        table[site].append(percentage_fulfilled)

        if percentage_fulfilled == 100.0:
            table['totalYes']['overall'] = table['totalYes']['overall'] + 1
        elif percentage_fulfilled > 0:
            table['totalNo']['overall'] = table['totalNo']['overall'] + 1
        else:
            table['totalNa']['overall'] = table['totalNa']['overall'] + 1

    pTable = PrettyTable(table['header'])

    pTable.add_row(['Total Yes', "100% fulfilled"] +
                   order_module_list(module_list, table['totalYes']))
    pTable.add_row(['Total No', ">0% fullfilled"] +
                   order_module_list(module_list, table['totalNo']))
    pTable.add_row(['Total Na', "0% fulfilled"] +
                   order_module_list(module_list, table['totalNa']))

    for site in site_list:
        pTable.add_row(table[site])

    return pTable


def send_result_to_confluence(report_table):
    
    page_info = '''
                <div>
                <strong>Ausgewählte automatische Abfragen des FDPG Machbarkeitsportal</strong><br></br>
                Für Öffnung vorausgesetzt:<br></br>
                <strong>Patient</strong>: code=263495000 (female|male) <br></br>
                <strong>Condition</strong>: code=E10-E14 (Diabetes mellitus)<br></br>
                <strong>Labor</strong>: code=718-7|17856-6|4548-4|4549-2 (Hemoglobin)<br></br>
                <strong>Prozedur</strong>: code=3-20|8-19 (CT,nativ| Verbände Gewebe)<br></br>
                <strong>Konsent</strong>: code=central-consent (MDAT wissenschaftlich nutzen)<br></br>
                <br></br>
                <strong>Für Öffnung nicht vorausgesetzt:</strong><br></br>
                Medikation (admin): code=A10 (Antidiabetika)<br></br>
                Specimen: code=119297000|119361006|119376003|441652008|441479001|420135007<br></br>
                (Blood|Plasma|Tissue|fixed Tissue|fresh Tissue|Whole blood)<br></br>
                </div>

                <div>
                <br></br><br></br>
                Standorte die nicht angeschlossen sind finden die Anleitungen zum Anschluss ans Feasibility-Portal
                mit Aktin hier:<br></br>
                https://github.com/medizininformatik-initiative/feasibility-deploy/tree/v2.0.0<br></br>
                Für das Triangle-Update der Readme hier folgen: https://github.com/medizininformatik-initiative/feasibility-deploy/tree/v2.0.0/feasibility-triangle#updating-the-feasibility-triangle<br></br>
                Die neue Ontologie muss hier runtergeladen werden: https://confluence.imi.med.fau.de/display/MIIC/Ontologie<br></br>
                <br></br>
                mit DSF hier:<br></br>
                https://github.com/medizininformatik-initiative/feasibility-deploy/wiki/DSF-Middleware-Setup<br></br>
<br></br>
                Informationen zum Feasibility Portal, DIZ-Dashboard und zur Datenausleitung mit DSF finden Sie hier:<br></br>
                https://xdash.forschen-fuer-gesundheit.de/?readme<br></br>
<br></br>
                Kontakt: info@forschen-fuer-gesundheit.de <br></br>
                </div>
                <br></br>
                <div>
                <strong>Legende</strong>:<br></br>
                <strong>„YES“</strong>: mehr als 20 Datenpunkte<br></br>
                <strong>„no“</strong>: weniger als 20 Datenpunkte<br></br>
                <strong>„.“</strong>: keine Antwort<br></br>
                </div>
    '''

    table_html = report_table.get_html_string()
    page_info = f'{page_info}{table_html}<br></br>'

    base64_bytes = base64.b64encode(f'{conf_user}:{conf_pw}'.encode('ascii'))
    base64_message = base64_bytes.decode('ascii')
    header = {
        'Authorization': f'Basic {base64_message}',
        'Content-Type': 'application/json'
    }

    res = requests.get(f'{confluence_api_base_url}/content/{confluence_page_id}',
                       headers=header)

    version_number = res.json()['version']['number']
    content_update = {
        'title': 'Status Erfüllung Umsetzung Module Machbarkeit Standorte',
        'type': 'page',
        'body': {'storage': {'value': page_info,
                             'representation': 'storage'
                             },
                 },
        'version': {'number': version_number + 1}
    }
    res = requests.put(f'{confluence_api_base_url}/content/{confluence_page_id}',
                       headers=header, json=content_update)


def execute_queries(queries):

    for query in queries['queries']:
        access_token = connect_to_keycloak()
        print(f'Sending query: {query["sq"]}')
        query_id = send_test_query_and_get_id(access_token, query['sq'])
        print(f'Query ID: {query_id}')
        print(f'Sleep for {wait_result_secs} seconds to wait for results')
        sys.stdout.flush()
        time.sleep(int(wait_result_secs))
        access_token = connect_to_keycloak()
        results = get_results(query_id, access_token)
        result = convert_results(results)
        query['result'] = result


queries = load_queries()
execute_queries(queries)
save_results_to_disk(queries)

if send_results_confluence:
    report_table = convert_report_to_table(queries)
    send_result_to_confluence(report_table)
