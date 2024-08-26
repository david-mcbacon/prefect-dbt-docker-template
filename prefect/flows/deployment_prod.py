from prefect.deployments.deployments import Deployment
from prefect.filesystems import RemoteFileSystem
from prefect.infrastructure import DockerContainer
import os
from pathlib import Path
from dotenv import load_dotenv

# env and utils
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

print(f"Connecting to minio storage on: {os.environ.get('MINIO_ENDPOINT_URL')}")

###############################
#####    CONFIG PROD      #####
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
    networks=["prefect-dbt"],
    env={
        "USE_SSL": False,
        "ENDPOINT_URL": os.environ.get("MINIO_ENDPOINT_URL"),
    },
    volumes=[
        f"{os.getenv('PROJECT_ROOT_DIR')}/dbt:/app/dbt",
        f"{os.getenv('PROJECT_ROOT_DIR')}/.env:/app/.env",
        f"{os.getenv('PROJECT_ROOT_DIR')}/bq-credentials.json:/app/bq-credentials.json",
    ],
)


#########################################
#             DEPLOYED FLOWS            #
#########################################


# at the end of the file
print("✅ Deployed successfully")
