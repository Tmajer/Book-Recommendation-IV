#! /bin/bash

function build {
	docker build -t recommender-app-image ..
  docker save recommender-app-image -o recommender-app.tar
}

function load {
  docker load --input recommender-app.tar
}

function run {
  docker network create interview-network
  docker run -d --name recommender-app \
    --net interview-network \
    --mount 'type=bind,src='$(pwd)'/config.yml,dst=/code/src/config.yml' \
    -p 80:80 \
    recommender-app-image
}

function stop {
  docker stop recommender-app
  docker rm recommender-app
}

case "$1" in
build)
	build
	;;
run)
	run
	;;
stop)
	stop
	;;
load)
	load
	;;
*)
	echo "Possible functions: recommender-app.sh build | load | run | stop"
	;;
esac

exit 0
