docker-compose -f docker-compose-prod.yaml run --rm dbt docs generate
docker-compose -f docker-compose-prod.yaml run --rm -d -p 8081:8080 dbt docs serve 