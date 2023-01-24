## Starting in production "hardware" mode
    docker compose -f docker-compose.base.yaml -f docker-compose.hardware.yaml up --remove-orphans --build

## Starting in local development "simulated" mode
    docker compose -f docker-compose.base.yaml -f docker-compose.simulated.yaml up --remove-orphans --build
