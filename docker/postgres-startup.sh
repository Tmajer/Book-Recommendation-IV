#! /bin/bash

docker network ls|grep interview-network > /dev/null || docker network create interview-network
docker run --name datasentics-postgres --net interview-network -e POSTGRES_PASSWORD=secret -p 5432:5432 -v datasentics-postgres-volume:/var/lib/postgresql/data -d postgres

exit 0