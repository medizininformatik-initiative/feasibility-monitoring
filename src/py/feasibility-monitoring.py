import argparse
import execute_ping_test
import execute_feasibility_test
import execute_collect_activity_definitions
import execute_collect_report_overview
import logging
import sys


def str_to_bool(s):
    return s.lower() in ["true", "yes", "1"]


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backend_base_url",
        help="base url of the feasibility backend",
        default="https://localhost/api/v2",
    )
    parser.add_argument(
            "--dsf_ping_process_version", help="the version of the ping process", nargs="?", default="1.0"
        )
    parser.add_argument(
            "--dsf_hrp_ident", help="ident of the hrp", nargs="?", default="forschen-fuer-gesundheit.de"
        )
    parser.add_argument(
        "--backend_client_id", help="backend client id", nargs="?", default="feasibility-gui"
    )
    parser.add_argument(
        "--dsf_base_url",
        help="base url of the feasibility backend",
        default="https://localhost/api/v2",
    )
    parser.add_argument(
        "--dsf_cert_path", help="path to the dsf cert", nargs="?", default="certs/dsf-cert.cer"
    )
    parser.add_argument(
        "--dsf_key_path", help="path to the dsf key", nargs="?", default="certs/dsf-key.key"
    )
    parser.add_argument("--backend_user", help="", nargs="?", default="test")
    parser.add_argument("--client_secret", help="", nargs="?", default="test")
    parser.add_argument(
        "--keycloak_token_url",
        help="keycloak token url",
        default="https://localhost/auth/realms/feasibility/protocol/openid-connect/token",
    )
    parser.add_argument(
        "--confluence_api_base_url", help="", nargs="?", default="https://myconfluence-rest-api-url"
    )
    parser.add_argument("--confluence_page_id_feas", help="", nargs="?", default="")
    parser.add_argument("--confluence_page_id_hist", help="", nargs="?", default="")
    parser.add_argument("--confluence_page_id_ping", help="", nargs="?", default="")
    parser.add_argument("--send_results_confluence", help="", type=str_to_bool, default="false")
    parser.add_argument(
        "--conf_user", help="username of confluence account", nargs="?", default="username"
    )
    parser.add_argument(
        "--conf_pw", help="password of confluence account", nargs="?", default="password"
    )
    parser.add_argument(
        "--wait_result_secs_feas",
        help="number of seconds to wait before results for a query are fetched",
        nargs="?",
        default="60",
    )
    parser.add_argument(
        "--wait_result_secs_ping",
        help="number of seconds to wait before results for the ping task fetched",
        nargs="?",
        default="600",
    )
    parser.add_argument(
        "--history_table_len",
        help="length of the history table that is sent to confluence",
        nargs="?",
        default="14",
    )
    parser.add_argument("--execute_feas_test", help="", type=str_to_bool, default="false")
    parser.add_argument("--execute_history_test", help="", type=str_to_bool, default="false")
    parser.add_argument("--execute_ping_test", help="", type=str_to_bool, default="false")
    parser.add_argument(
        "--execute_collect_activity_definition", help="", type=str_to_bool, default="false"
    )
    parser.add_argument(
        "--execute_collect_report_overview", help="", type=str_to_bool, default="false"
    )
    parser.add_argument("--log_level", help="", default="INFO")

    args = vars(parser.parse_args())
    dsf_ping_process_version = args["dsf_ping_process_version"]
    dsf_hrp_ident = args["dsf_hrp_ident"]
    backend_base_url = args["backend_base_url"]
    backend_client_id = args["backend_client_id"]
    dsf_base_url = args["dsf_base_url"]
    dsf_cert_path = args["dsf_cert_path"]
    dsf_key_path = args["dsf_key_path"]
    backend_user = args["backend_user"]
    client_secret = args["client_secret"]
    keycloak_token_url = args["keycloak_token_url"]
    confluence_api_base_url = args["confluence_api_base_url"]
    confluence_page_id_feas = args["confluence_page_id_feas"]
    confluence_page_id_hist = args["confluence_page_id_hist"]
    confluence_page_id_ping = args["confluence_page_id_ping"]
    b_send_results_confluence = args["send_results_confluence"]
    conf_user = args["conf_user"]
    conf_pw = args["conf_pw"]
    wait_result_secs_feas = args["wait_result_secs_feas"]
    wait_result_secs_ping = args["wait_result_secs_ping"]
    history_table_len = args["history_table_len"]
    b_execute_feas_test = args["execute_feas_test"]
    b_execute_history_test = args["execute_history_test"]
    b_execute_ping_test = args["execute_ping_test"]
    b_execute_activity_config_collection = args["execute_collect_activity_definition"]
    b_execute_collect_report_overview = args["execute_collect_report_overview"]
    log_level = args["log_level"]

    logging.basicConfig(stream=sys.stdout, level=log_level)
    logging.info(f"Running Feasibility Monitoring with log level {log_level}")

    if b_execute_history_test:
        logging.info("Executing history test")
        execute_feasibility_test.execute_history_query(
            backend_base_url,
            backend_client_id,
            client_secret,
            keycloak_token_url,
            wait_result_secs_feas,
            conf_user,
            conf_pw,
            confluence_api_base_url,
            confluence_page_id_hist,
            b_send_results_confluence,
            history_table_len,
        )
        logging.info("Finished executing history test")

    if b_execute_feas_test:
        logging.info("Executing feasibility test")
        execute_feasibility_test.execute_feas_test_queries(
            backend_base_url,
            backend_client_id,
            client_secret,
            keycloak_token_url,
            conf_user,
            conf_pw,
            confluence_api_base_url,
            confluence_page_id_feas,
            wait_result_secs_feas,
            b_send_results_confluence,
        )
        logging.info("Finished executing feasibility test")

    if b_execute_ping_test:
        logging.info("Executing ping test")
        execute_ping_test.execute_ping_task(
            dsf_ping_process_version,
            dsf_hrp_ident,
            dsf_base_url,
            wait_result_secs_ping,
            b_send_results_confluence,
            confluence_api_base_url,
            confluence_page_id_ping,
            conf_user,
            conf_pw,
            dsf_cert_path,
            dsf_key_path,
        )
        logging.info("Finished executing ping test")

    if b_execute_activity_config_collection:
        logging.info("### Executing the collection of activity definitions (installed processes at sites)")

        execute_collect_activity_definitions.execute_collect_activity_definitions(
            dsf_base_url, dsf_cert_path, dsf_key_path
        )

        logging.info("### Finished executing the collection of activity definitions")

    if b_execute_collect_report_overview:
        logging.info("### Executing the collection of report overview")

        execute_collect_report_overview.execute_collect_report_overview(
            dsf_base_url, dsf_cert_path, dsf_key_path
        )

        logging.info("### Finished executing the collection of report overview")
