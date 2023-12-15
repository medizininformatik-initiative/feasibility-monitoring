#!/bin/bash
DSF_CERT_PATH=$LOCAL_DSF_CERT_PATH
DSF_KEY_PATH=$LOCAL_DSF_KEY_PATH
BACKEND_BASE_URL=${BACKEND_BASE_URL:-"https://localhost/api/v1"} 
BACKEND_CLIENT_ID=${BACKEND_CLIENT_ID:-"feasibility-gui"} 
BACKEND_CLIENT_SECRET=${BACKEND_CLIENT_SECRET:-"test"}
KEYCLOAK_TOKEN_URL=${KEYCLOAK_TOKEN_URL:-"https://localhost/auth/realms/feasibility/protocol/openid-connect/token"}
CONFLUENCE_API_BASE_URL=${CONFLUENCE_API_BASE_URL:-"https://myconfluence-rest-api-url"}
CONF_USER=${CONF_USER:-"username"}
CONF_PW=${CONF_PW:-"password"}
WAIT_RESULT_SECS_FEAS=${WAIT_RESULT_SECS_FEAS:-60}
WAIT_RESULT_SECS_PING=${WAIT_RESULT_SECS_PING:-600}

SEND_TO_CONFLUENCE=${SEND_TO_CONFLUENCE:-"false"}
DSF_BASE_URL=${DSF_BASE_URL:-""}
EXECUTE_FEAS_TEST=${EXECUTE_FEAS_TEST:-"false"}
CONFLUENCE_PAGE_ID_FEAS=$CONFLUENCE_PAGE_ID_FEAS
EXECUTE_HISTORY_TEST=${EXECUTE_HISTORY_TEST:-"false"}
CONFLUENCE_PAGE_ID_HIST=${CONFLUENCE_PAGE_ID_HIST:-""}
HISTORY_TABLE_LEN=${HISTORY_TABLE_LEN:-14}
EXECUTE_DSF_PING_TEST=${EXECUTE_DSF_PING_TEST:-"false"}
CONFLUENCE_PAGE_ID_PING=$CONFLUENCE_PAGE_ID_PING

python src/py/feasibility-monitoring.py --dsf_cert_path $DSF_CERT_PATH --dsf_key_path $DSF_KEY_PATH --backend_base_url "$BACKEND_BASE_URL" --backend_client_id "$BACKEND_CLIENT_ID" \
 --client_secret "$BACKEND_CLIENT_SECRET" --keycloak_token_url "$KEYCLOAK_TOKEN_URL" \
 --confluence_api_base_url "$CONFLUENCE_API_BASE_URL" --conf_user "$CONF_USER" --conf_pw "$CONF_PW"\
 --send_results_confluence $SEND_TO_CONFLUENCE  --wait_result_secs_feas "$WAIT_RESULT_SECS_FEAS"\
 --dsf_base_url $DSF_BASE_URL --execute_feas_test $EXECUTE_FEAS_TEST --confluence_page_id_feas $CONFLUENCE_PAGE_ID_FEAS\
 --execute_history_test $EXECUTE_HISTORY_TEST --confluence_page_id_hist $CONFLUENCE_PAGE_ID_HIST --history_table_len $HISTORY_TABLE_LEN\
 --execute_ping_test $EXECUTE_DSF_PING_TEST --confluence_page_id_ping $CONFLUENCE_PAGE_ID_PING  --wait_result_secs_ping "$WAIT_RESULT_SECS_PING"
