# Book Recommendation

Welcome to the Book Recommendation repository. 
This repository contains code build for recommending books from the [Book Recommendation Dataset](https://www.kaggle.com/datasets/arashnic/book-recommendation-dataset).

## Requirements

- Docker
- Python (to import data)

## Installation

To run the app, just spin up Docker on your device. 
There are pre-made Powershell scripts for platforms running Windows and pre-made bash script for platforms running Linux.
These scripts are located in the `docker` directory.

### Installing Python dependencies

The project contains standard `requirements.txt` file, use it to install the requirements with

```
pip install -r requirements.txt
```

### Starting PostgreSQL database

The app communicates with PostgreSQL server - if you never ran it on your platform, pull the PostgreSQL Docker Image using the following command:

`docker pull postgres`

Then `cd` into the `docker` directory and run either the `postgres-startup.ps1` or the `postgres-startup.sh` script to start the database.

### Starting the application

After starting the database, you can use the scripts to build the application image.

<details>
  <summary>Windows start-up</summary>
  
  To start the application on Windows, run the following commands:
    
  ```
  ./recommender-app.ps1 Build-App skip-save
  ./recommender-app.ps1 Run-App
  ```
  
  The `Build-App` function builds the application image (and saves it on disk). 
  If you don't want to save the image on disk, call the function with the `skip-save` argument, if you want to save the image, call the function as follows: 

  ```
  ./recommender-app.ps1 Build-App
  ```
  If you saved the image to disk, you can use the `./recommender-app.ps1 Load-App` function. This can be ommited if you ran the build on your device as the image gets loaded during the build.

  The `Run-App` runs the application.

  To stop the application, you can call the `Stop-App` function as follows:

  ```
  ./recommender-app.ps1 Stop-App
  ```
</details>

<details>
  <summary>Linux start-up</summary>
  
  To start the application on Linux, run the following commands:
    
  ```
  ./recommender-app.sh build skip-save
  ./recommender-app.sh run
  ```
  
  The `build` function builds the application image (and saves it on disk). 
  If you don't want to save the image on disk, call the function with the `skip-save` argument, if you want to save the image, call the function as follows: 

  ```
  ./recommender-app.sh build
  ```

  If you saved the image to disk, you can use the `./recommender-app.sh load` function. This can be ommited if you ran the build on your device as the image gets loaded during the build.

  The `run` runs the application.

  To stop the application, you can call the `stop` function as follows:

  ```
  ./recommender-app.sh stop
  ```
</details>

### Importing data

After you start the application, you will need to init the database tables and import data into them.

To create the tables, `cd` into `/src/postgres/` directory and run the `init_tables.py` script.

You are expected to have the data in the `data` directory. To import the data, run the `import_data.py` script.

### Checking the app

Now you are all set and done - the application should be running on http://localhost.
