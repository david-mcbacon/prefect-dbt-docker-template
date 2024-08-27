# this docker file is used to build a docker image for DBT documentation

FROM python:3.8

COPY . /dbt

RUN apt update && \
    pip install dbt-bigquery

