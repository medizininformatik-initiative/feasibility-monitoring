# automatic-connection-test-feasibility

## Goal

The goal of this repository is to test the overall connectedness and what data the sites offer.
The results of the test are saved on disk and can optionally be uploaded to a Confluence page.

* The Feasibility test sends SQ's to the Backend and cheks which sites have enough data fitting the SQ's
* The History test sends one SQ to the Backend and saves multiple results over time on disk
* The Ping test sends a ping to the DSF and checks which sites answer with a pong (see [ping-task.xml](src/resources/ping-task.xml)) 

## Setup

For the Feasibility test, the SQ's of the [input-queries.json](config/input-queries.json) are used. This JSON has one field "queries", which contains a list where each element must have the following fields:

| Name             | Description                                                                                  | 
|:-----------------|:---------------------------------------------------------------------------------------------|
| query-name       | A custom name for the query, which is used in the table on Confluence to identify the query. |
| Module           | The module of the query (e.g. Procedure).                                                    |
| optional         | Boolean: whether or not the sites must have data fitting this SQ - used to calculate the percentage of required modules a site fulfills in the confluence table. | 
| sq               | The Structured Query.                                                                        | 

For the History test, the [history-query.json](config/history-query.json) must contain one single SQ.

### Config

Additionally, the following fields in the [config.yml](config/config.yml) can be configured:

| Name                          | Description                                                                | 
|:------------------------------|:---------------------------------------------------------------------------|
| feas-page-title               | The title of the Confluence page for the Feasibility test.                 |
| feas-page-content-html        | The HTML content of the Confluence page for the Feasibility test.          |
| hist-page-title               | The title of the Confluence page for the Feasibility history test.         | 
| hist-page-content-html        | The HTML content of the Confluence page for the Feasibility history test.  | 
| ping-page-title               | The title of the Confluence page for the Feasibility history test.         |
| ping-page-content-html        | The HTML content of the Confluence page for the ping test.                 |
| dsf-site-ids                  | A list of all sites that are expected to respont to the test.              |


## Run

```sh
docker-compose -f docker/docker-compose.yml up
```


## Environment Variables

| Name                          | Default                               | Description                                                                                      |
|:------------------------------|:--------------------------------------|:-------------------------------------------------------------------------------------------------|
| LOCAL_DSF_CERT_PATH           | ./cert/dsf-cert.cer                   | The local path of the DSF certificate.                                                           |
| LOCAL_DSF_KEY_PATH            | ./cert/dsf-key.key                    | The local path of the DSF key.                                                                   |
| BACKEND_BASE_URL              | https://localhost/api/v1              | The URL of the Feasibility Backend.                                                              |
| BACKEND_CLIENT_ID             |                                       | The client ID for the Feasibility Backend.                                                       |
| BACKEND_CLIENT_SECRET         |                                       | The client secret for the Feasibility Backend.                                                   |
| KEYCLOAK_TOKEN_URL            |                                       | The token URL for Keycloak.                                                                      |
| CONFLUENCE_API_BASE_URL       | https://myconfluence-rest-api-url     | The base URL of the Confluence API, where the results will be uploaded.                          |
| CONF_USER                     |                                       | The username of the account that is used to upload the result to Confluence.                     |
| CONF_PW                       |                                       | The password of the account that is used to upload the result to Confluence.                     |
| WAIT_RESULT_SECS_FEAS         | 60                                    | The seconds to wait for the response of the Feasibility Backend for the feasibility test.        |
| WAIT_RESULT_SECS_PING         | 60                                    | The seconds to wait for the response of the DSF for the ping test.                               |
| SEND_TO_CONFLUENCE            | false                                 | Boolean: Whether to send the results to confluence.                                              |
| DSF_BASE_URL                  |                                       | The Base URL of the DSF - used to execute the ping test against.                                 |
| EXECUTE_FEAS_TEST             | false                                 | Boolean: Whether to execute the Feasibility test.                                                |
| CONFLUENCE_PAGE_ID_FEAS       |                                       | The Confluence page ID where the Feasibility test result will be uploaded.                       |
| EXECUTE_HISTORY_TEST          | false                                 | Boolean: Whether to execute the Feasibility history test.                                        |
| CONFLUENCE_PAGE_ID_HIST       |                                       | The Confluence page ID where the Feasibility history test result will be uploaded.               |
| HISTORY_TABLE_LEN             | 14                                    | The maximum amount of history repots displayed in the Confluence table.                          |
| EXECUTE_DSF_PING_TEST         | false                                 | Boolean: Whether to execute the DSF ping test.                                                   |
| CONFLUENCE_PAGE_ID_PING       |                                       | The Confluence page ID where the ping test result will be uploaded.                              |
