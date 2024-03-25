FROM python:3.9

RUN mkdir -p /opt/reportclient

COPY src/py/feasibility-monitoring.py /opt/reportclient/src/py/feasibility-monitoring.py
COPY src/py/execute_ping_test.py /opt/reportclient/src/py/execute_ping_test.py
COPY src/py/execute_feasibility_test.py /opt/reportclient/src/py/execute_feasibility_test.py
COPY src/py/execute_collect_activity_definitions.py /opt/reportclient/src/py/execute_collect_activity_definitions.py
COPY src/py/execute_collect_activity_definitions.py /opt/reportclient/src/py/execute_collect_report_overview.py
COPY config/input-queries.json /opt/reportclient/config/input-queries.json
COPY config/history-query.json /opt/reportclient/config/history-query.json
COPY config/config.yml /opt/reportclient/config/config.yml
COPY src/resources/ping-task.xml /opt/reportclient/src/resources/ping-task.xml
COPY docker/requirements.txt /tmp/requirements.txt

RUN pip3 install -r /tmp/requirements.txt

WORKDIR /opt/reportclient
RUN mkdir reports
RUN chown -R 1001:1001 /opt/reportclient

COPY docker/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

USER 1001

ENTRYPOINT ["docker-entrypoint.sh"]
