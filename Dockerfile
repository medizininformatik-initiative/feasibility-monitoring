FROM python:3.9

RUN mkdir -p /opt/reportclient
COPY ./docker-entrypoint.sh /opt/reportclient/docker-entrypoint.sh
COPY ./feasibility-monitoring.py /opt/reportclient/feasibility-monitoring.py
COPY ./input-queries.json /opt/reportclient/input-queries.json
RUN pip install requests==2.22.0
RUN pip install psycopg2==2.9.3
RUN pip install prettytable==3.3.0
RUN useradd -r -s /bin/false 10001


WORKDIR /opt/reportclient
RUN mkdir reports
RUN chmod 777 reports
RUN chown -R 10001:10001 /opt/reportclient

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
RUN mkdir certs

USER 10001

ENTRYPOINT ["docker-entrypoint.sh"]