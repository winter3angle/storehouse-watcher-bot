FROM python:3.11.5-bookworm

COPY . /app
WORKDIR /app
RUN apt update && apt install -y libpq-dev
RUN python3 -m pip install -r /app/requirements.txt
RUN chmod 0755 run.sh
ENTRYPOINT ["./run.sh"]