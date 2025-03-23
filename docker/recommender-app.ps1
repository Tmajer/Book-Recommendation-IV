function Run-App {
    docker network create interview-network
    docker run -d --name recommender-app --net interview-network -p 80:80 --mount type=bind,src=${pwd}/config.yml,dst=/code/src/config.yml recommender-app-image
}

function Build-App($argz) {
    docker build -t recommender-app-image ..
    if ((!$argz[1]) -or ($argz[1] -ne "skip-save")) {
        docker save recommender-app-image -o recommender-app.tar
    }
}

function Stop-App {
    docker stop recommender-app
    docker rm recommender-app
}

function Load-App {
    docker load --input recommender-app.tar
}

switch ($args[0]) {
    Run-App { Run-App }
    Build-App { Build-App($args) }
    Stop-App { Stop-App }
    Load-App { Load-App }
    default { Write-Output "Possible functions: recommender-app.ps1 Run-App | Build-App | Stop-App | Load-App"}
}
