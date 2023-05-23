#!/bin/bash

BACKEND_BASE_URL=${BACKEND_BASE_URL:-"https://localhost/api/v1"} 
BACKEND_CLIENT_ID=${BACKEND_CLIENT_ID:-"feasibility-gui"} 
BACKEND_CLIENT_SECRET=${BACKEND_CLIENT_SECRET:-"test"}
KEYCLOAK_TOKEN_URL=${KEYCLOAK_TOKEN_URL:-"https://localhost/auth/realms/feasibility/protocol/openid-connect/token"}
CONFLUENCE_API_BASE_URL=${CONFLUENCE_API_BASE_URL:-"https://myconfluence-rest-api-url"}
CONFLUENCE_PAGE_ID=${CONFLUENCE_PAGE_ID}
CONF_USER=${CONF_USER:-"username"}
CONF_PW=${CONF_PW:-"password"}
WAIT_RESULT_SECS=${WAIT_RESULT_SECS:-60}

if [[ $SEND_TO_CONFLUENCE == "true" ]] || [[ $SEND_TO_CONFLUENCE == "True" ]]
then
SEND_TO_CONFLUENCE="--send_to_confluence"
fi

python3 automatic-connection-test.py --backend_base_url "$BACKEND_BASE_URL" --backend_client_id "$BACKEND_CLIENT_ID" \
--client_secret "$BACKEND_CLIENT_SECRET" --keycloak_token_url "$KEYCLOAK_TOKEN_URL" \
--confluence_api_base_url "$CONFLUENCE_API_BASE_URL" --conf_user "$CONF_USER" --conf_pw "$CONF_PW" --confluence_page_id "$CONFLUENCE_PAGE_ID" \
--wait_result_secs "$WAIT_RESULT_SECS" $SEND_TO_CONFLUENCE
