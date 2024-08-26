from prefect import flow, tags
from prefect_shell import shell_run_command

import os

#########################################
#              ENV & UTILS              #
#########################################

import sys
from pathlib import Path
from dotenv import load_dotenv

try:
    env_path = Path(__file__).resolve().parents[3] / ".env"  # for local testing
except IndexError:
    env_path = Path(__file__).resolve().parents[1] / ".env"  # for docker worker

utils_path = str(Path(__file__).resolve().parents[1])
load_dotenv(env_path)
sys.path.append(utils_path)


@flow(name="dbt_run_models")
def dbt_run_models(models):
    with tags("dbt"):
        dbt_config_command = "--profiles-dir {0} --project-dir {1}".format(
            os.environ.get("PREFECT_DBT_PROFILES_DIR"),
            os.environ.get("PREFECT_DBT_PROJECT_DIR"),
        )

        result = shell_run_command(
            command="dbt run --select {0} {1}".format(
                " ".join(models), dbt_config_command
            ),
            return_all=True,
        )

        return result


@flow(name="dbt_run_operation")
def dbt_run_operation(macro, args):
    with tags("dbt"):
        dbt_config_command = "--profiles-dir {0} --project-dir {1}".format(
            os.environ.get("PREFECT_DBT_PROFILES_DIR"),
            os.environ.get("PREFECT_DBT_PROJECT_DIR"),
        )

        if args == None:
            arguments = ""
        else:
            arguments = "--args '{}'".format(args)

        result = shell_run_command(
            command="dbt run-operation {0} {1} {2}".format(
                macro, arguments, dbt_config_command
            ),
            return_all=True,
        )

        return result
