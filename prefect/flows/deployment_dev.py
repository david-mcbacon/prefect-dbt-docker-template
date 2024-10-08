from prefect.deployments.deployments import Deployment
from prefect.filesystems import RemoteFileSystem
from prefect.infrastructure import DockerContainer
import os
from pathlib import Path
from dotenv import load_dotenv

# env and utils
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

print(f"Connecting to minio storage on URL: {os.environ.get('MINIO_ENDPOINT_URL')}")

###############################
#####     CONFIG DEV      #####
###############################

minio_block = RemoteFileSystem(
    basepath="s3://prefect-flows",
    key_type="hash",
    settings=dict(
        use_ssl=False,
        key=os.environ.get("MINIO_KEY"),
        secret=os.environ.get("MINIO_SECRET"),
        client_kwargs=dict(endpoint_url=os.environ.get("MINIO_ENDPOINT_URL")),
    ),
)

minio_block.save("minio", overwrite=True)
print("✅ Minio Connection OK")

"""
this will create new docker container as a "worker", load the code from minio and execute the code
"""
worker_infrastructure = DockerContainer(
    auto_remove=True,
    image="prefect-orion:2.11.3",
    image_pull_policy="IF_NOT_PRESENT",
    networks=["prefect-dbt"],  # network name from docker-compose file
    env={
        "USE_SSL": False,
        "ENDPOINT_URL": os.environ.get("MINIO_ENDPOINT_URL"),
    },
    volumes=[
        f"{os.getenv('PROJECT_ROOT_DIR')}/dbt:/app/dbt",
        f"{os.getenv('PROJECT_ROOT_DIR')}/dev-worker.env:/app/.env",  # dev-worker env file
        f"{os.getenv('PROJECT_ROOT_DIR')}/bq-credentials.json:/app/bq-credentials.json",
    ],
)


#########################################
#             DEPLOYED FLOWS            #
#########################################

from src.pokemon.pokemon_elt import run_pokemon_elt

pokemon_elt_dep = Deployment.build_from_flow(
    name="Pokemon ELT",
    flow=run_pokemon_elt,
    storage=minio_block.load("minio"),
    infrastructure=worker_infrastructure,
    work_queue_name="default",
    tags=["pokemon", "elt"],
    apply=True,
)

# pokemon_elt_dep.apply()

# at the end of the file
print("✅ Deployed successfully")
