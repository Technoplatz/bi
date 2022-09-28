FROM python:3.9-slim
RUN DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y cron dirmngr gnupg apt-transport-https ca-certificates software-properties-common wget libmagic-dev curl
RUN wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add -
RUN echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list
RUN apt-get update
RUN apt-get install -y mongodb-org-tools
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR /app
COPY . /app
RUN /opt/venv/bin/python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt
ENTRYPOINT ["/opt/venv/bin/python3"]
CMD ["api.py"]