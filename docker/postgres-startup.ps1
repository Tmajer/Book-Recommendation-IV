$networkName = "interview-network"

if (!(docker network ls | select-string $networkName -Quiet )) {
    docker network create $networkName
}
docker run --name datasentics-postgres --net interview-network -e POSTGRES_PASSWORD=secret -p 5432:5432 -v datasentics-postgres-volume:/var/lib/postgresql/data -d postgres