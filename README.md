# Prefect DBT Docker Template

This repository serves as a template for orchestrating Prefect and DBT within Docker containers. It is tailored as a starting point for data engineering projects, leveraging Prefect for workflow orchestration and DBT for data transformation. In this setup, DBT is configured to work with Google BigQuery, but the template can be easily adapted to other databases.

The project is designed for local development and single-server deployment but can be extended for Kubernetes cluster deployment if required.

## Prerequisites

- Docker
- Docker Compose
- Python 3.9 with conda/miniconda (for local development)
- Google Cloud Platform (GCP) account

## Useful Links

- [Prefect Documentation](https://docs.prefect.io/2.11.3/)
- [DBT Documentation](https://docs.getdbt.com/docs/introduction)

## Project Structure

- [`/dbt`](./dbt) - DBT project folder
- [`/prefect`](./prefect) - Prefect project folder
- [`/prefect/flows/src/<subfolder>`](./prefect/flows/src) - Prefect flow scripts
- [`docker-compose.yml`](./docker-compose.yml) - Docker Compose file for running Prefect and DBT in development
- [`docker-compose-prod.yml`](./docker-compose-prod.yml) - Docker Compose file for running Prefect and DBT in production
- [`Makefile`](./Makefile) - Utility commands for running the project

## Getting Started - Local Development

1. **Clone this repository:**

   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Create a new Google Cloud Platform project.**
3. **Enable the BigQuery API in GCP.**
4. **Create a new service account with the BigQuery Admin role.**
5. **Download the service account key:**

   - Save it as `bq-credentials.json` in the root of the project.
   - Copy the same file to the `dbt` folder.

6. **Create environment files:**

   - Create `.env`, `dev-worker.env`, and `prod.env` in the root of the project.
   - Use the corresponding `.example` files as templates.

7. **Configure DBT:**

   - Create `profiles.yaml` in the `dbt` folder using [`profiles.example.yaml`](./dbt/profiles.example.yaml) as a template.

8. **Set up the Conda environment and install dependencies:**

   ```bash
   conda create -n prefect-dbt python=3.9 -y
   conda activate prefect-dbt
   pip install -r prefect/requirements.txt
   ```

9. **Run the project locally:**

   ```bash
   make start-app-local
   ```

10. **Access the Prefect UI:**

    - Open your browser and go to [http://localhost:4200](http://localhost:4200).

11. **Deploy pre-built flows to Prefect:**

    ```bash
    make deploy-local
    ```

12. **Verify deployed flows:**

    - Go to [http://localhost:4200/deployments](http://localhost:4200/deployments) and confirm that your flow is deployed. You can run it manually or schedule it.

## Running Flows from the Local Terminal

1. **Ensure Prefect server and agent are running locally:**

   ```bash
   make start-app-local
   ```

2. **Activate the Conda environment:**

   ```bash
   conda activate prefect-dbt
   ```

3. **Set the Prefect API URL environment variable:**

   ```bash
   export PREFECT_API_URL=http://0.0.0.0:4200/api/
   ```

4. **Run the flow:**

   ```bash
   python prefect/flows/src/pokemon/pokemon_elt.py
   ```

## Running DBT Models from the Local Terminal

1. **Activate the Conda environment:**

   ```bash
   conda activate prefect-dbt
   ```

2. **Navigate to the `dbt` folder:**

   ```bash
   cd dbt
   ```

3. **Check DBT configuration and connection (optional):**

   ```bash
   dbt debug
   ```

   - If everything is configured correctly, you should see:

     ```
     Connection test: [OK connection ok]
     All checks passed!
     ```

4. **Run DBT models:**

   ```bash
   dbt run -s pokemons.pokemons
   ```

## DBT Development and Production Configuration

DBT uses the `profiles.yaml` file for database connection configuration. Create this file in the `dbt` folder, using [`profiles.example.yaml`](./dbt/profiles.example.yaml) as a template. The template includes both `dev` and `prod` configurations. The default target is `dev`, but you can switch to `prod` by changing the `target` parameter in `profiles.yaml` or directly in the DBT command.

To run the production configuration:

```bash
dbt run -s pokemons.pokemons --target prod
```

**Development vs. Production Configurations:**

- **Development (`dev` target):** DBT uses the `dev_` prefix for schema/dataset names.
- **Production (`prod` target):** No prefix is used; the dataset name remains as defined.

For example, if you run the `dev` target, the table will be created as `dev_pokemons.pokemons`. For `prod`, it will be `pokemons.pokemons`.

Schema naming is configured in the [`dbt_project.yml`](./dbt/dbt_project.yml) file:

```yaml
models:
  app:
    pokemons:
      dataset: "{{ 'pokemons' if target.name == 'prod' else 'dev_pokemons' }}"
```

Additionally, the `generate_schema_name.sql` macro in the [`macros`](./dbt/macros) folder automatically generates the schema name based on the target.

**Recommended Setup:**

- **Local development:** Use the `dev` target in `profiles.yaml`.
- **Production:** Use the `prod` target in `profiles.yaml` on the server.

## Running DBT Documentation UI Locally

DBT includes a built-in documentation UI. To run it locally:

```bash
cd dbt
dbt docs generate
dbt docs serve --port 8081
```

Then open [http://localhost:8081](http://localhost:8081) in your browser.

## Deploying New Flows to Prefect - Local Development

1. **Ensure Prefect server and agent are running locally:**

   ```bash
   make start-app-local
   ```

2. **Create a new flow script:**

   - Add the script in the `prefect/flows/src/pokemon` folder (e.g., `new_flow.py`).
   - Define the main flow function (e.g., `run_new_flow`).

3. **Register the new flow:**

   - Modify the [`deployment_dev.py`](./prefect/flows/deployment_dev.py) file:

   ```python
   from src.pokemon.new_flow import run_new_flow

   new_flow_dep = Deployment.build_from_flow(
     name="New Pokemon Flow",
     flow=run_new_flow,
     storage=minio_block.load("minio"),
     infrastructure=worker_infrastructure,
     work_queue_name="default",
     tags=["pokemon", "new_flow"],
     apply=True,
   )
   ```

4. **Deploy the flow:**

   ```bash
   make deploy-local
   ```

5. **Verify deployment:**

   - Check the Prefect UI at [http://localhost:4200/deployments](http://localhost:4200/deployments) to confirm the new flow is deployed.

## Production Deployment of Prefect and DBT in Docker

1. **Set up SSH access to your VPS server.**
2. **(Optional but recommended) Configure Nginx as a reverse proxy with authentification for Prefect UI.**
3. **Clone the repository to the VPS server.**
4. **Prepare environment files:**

   - Ensure `.env` and `prod.env` are correctly configured on your local machine.
   - Set `SSH_USER`, `SSH_HOST`, and `SSH_PATH_TO_PROJECT` environment variables.

5. **Copy environment file to the server:**

   ```bash
   make copy-env-to-server
   ```
   - This command let you select the environment file to copy to the server and rename it to `.env`. Select `prod.env` for production.

6. **Prepare necessary files on the server:**

   - Copy `bq-credentials.json` and `profiles.yaml` to the server in the appropriate locations.

7. **Start Prefect on the server:**

   ```bash
   make start-app-prod
   ```

## Deploying New Flows to Prefect - Production

1. **Ensure Prefect server and agent are running on the server:**

   ```bash
   make start-app-prod
   ```

2. **Create and register the new flow:**

   - Similar to local deployment, add the new flow to the [`deployment_prod.py`](./prefect/flows/deployment_prod.py) file.

3. **Commit and push changes to the GitHub repository**
   

4. **Deploy to production:**

   - Option 1: From your local machine:

     ```bash
     make deploy-prod-from-local
     ```

   - Option 2: SSH into the server, navigate to the project folder, and run:

     ```bash
     make git
     make deploy-prod
     ```

5. **Verify deployment:**

   - Check the Prefect UI at `http://your-domain.com/deployments` to confirm the new flow is deployed.

## Typical Development to Production Workflow

1. **Local Development:** 

   - Start with pure Python (without Docker or Prefect), develop and test functions, then create a main function for the script.

2. **Integrate with Prefect:**

   - Add `@task` decorators to functions, and `@flow` to the main function (renamed as `run_<filename>`, e.g. `run_pokemon_elt`).
   - Add Prefect logging (optional).

3. **Run Prefect Locally:**

   - Start Prefect server locally and test the script from the terminal.

4. **Deploy and Test Locally:**

   - Register the script in [`deployment_dev.py`](./prefect/flows/deployment_dev.py) and deploy locally.
   - Check the Prefect UI and run the flow manually from the UI.

5. **Production Deployment:**

   - Register the script in [`deployment_prod.py`](./prefect/flows/deployment_prod.py), push changes to the repository, and deploy to production.

6. **Deploy from Local to Production:**

   ```bash
   make deploy-prod-from-local
   ```

