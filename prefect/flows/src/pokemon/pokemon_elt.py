import requests
from typing import List, Dict
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import os
from prefect import task, flow
from prefect.task_runners import SequentialTaskRunner

# -------------------------------------- #
#               ENV & UTILS              #
# -------------------------------------- #

import sys
from pathlib import Path
from dotenv import load_dotenv

try:
    env_path = Path(__file__).resolve().parents[4] / ".env"  # for local testing
except IndexError:
    env_path = Path(__file__).resolve().parents[2] / ".env"  # for docker worker

utils_path = str(Path(__file__).resolve().parents[2])
load_dotenv(env_path)
sys.path.append(utils_path)

from utils.dbt_subflows import dbt_run_models

# -------------------------------------- #
#                CONSTANTS               #
# -------------------------------------- #

credentials = service_account.Credentials.from_service_account_file(
    os.environ.get("GOOGLE_BIG_QUERY_CREDENTIALS_PATH")
)
project_id = os.environ.get("GOOGLE_BIG_QUERY_PROJECT_ID")
bqclient = bigquery.Client(project=project_id, credentials=credentials)

# -------------------------------------- #
#                  TASKS                 #
# -------------------------------------- #


@task
def fetch_all_pokemons() -> List[Dict]:
    try:
        url = "https://pokeapi.co/api/v2/pokemon?limit=10000"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            pokemons = data["results"]

            return pokemons
            # [{'name': 'bulbasaur', 'url': 'https://pokeapi.co/api/v2/pokemon/1/'}, ...]

        else:
            raise ValueError(f"Failed to fetch data: {response.status_code}")
    except Exception as e:
        raise ValueError(f"Failed to fetch data: {e}")


def convert_pokemons_to_dataframe(pokemons: List[Dict]) -> pd.DataFrame:
    return pd.DataFrame(pokemons)


@task
def load_pokemons_to_big_query(pokemons_df: pd.DataFrame):
    try:
        pokemons_df.to_gbq(
            destination_table="pokemons.stg_pokemons",
            project_id=project_id,
            if_exists="replace",
            credentials=credentials,
            chunksize=10000,
        )
    except Exception as e:
        raise ValueError(f"Failed to load data to BigQuery: {e}")


@flow(task_runner=SequentialTaskRunner())
def run_pokemon_elt():
    pokemons = fetch_all_pokemons()
    pokemons_df = convert_pokemons_to_dataframe(pokemons)
    load_pokemons_to_big_query(pokemons_df)
    dbt_run_models(["pokemons.pokemons"])


if __name__ == "__main__":
    run_pokemon_elt()
