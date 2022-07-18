# This exercise goal

July 18, 2022. This [Back to main](../README.md)

The purpose of this exercise is to install all the tools locally (on-premise) and run a DAG that creates a table in a PostgreSQL database and ingest data from a CSV file.

The DAG will ingest a portion of the CSV (a number of rows from a given row index).

For this exercise, once you have Airflow up and running, copy the dags folder inside `0_local/airflow_project/dags` (including `sql` subfolder) inside `~/airflow/`. Run the DAG in Airflow, and verify the PostgreSQL database has the ingested CSV records.

# Installation on Ubuntu 22.04

| OS | Tool | Version | Installation |
|----|------|---------|--------------|
| Ubuntu | Chrome | 103.0.5060.114 | [Instructions](#UbuntuChrome) |
| Ubuntu | Git | 2.34.1 | [Instructions](#UbuntuGit) |
| Ubuntu | Visual Code | 1.69.1 | [Instructions](#UbuntuVisualCode) |
| Ubuntu | Python | 3.10.4 | [Instructions](#UbuntuPython) |
| Ubuntu | PostgreSQL, PGAdmin4 | 14.4, 6.11 | [Instructions](#UbuntuPostgreSQL) |
| Ubuntu | Docker, docker-compose | 20.10.17, 1.29.2 | [Instructions](#UbuntuDocker) |
| Ubuntu | Airflow (locally) | 2.3.3 | [Instructions](#UbuntuAirflow) |


## <a name="UbutuChrome"></a>Chrome (optional)

```
cd ~/Downloads
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

## <a name="UbuntuGit"></a>Git 2.34.1

```sh
git apt install git

git --version

# Configure git global settings
git config --global user.name "Your full name"
git config --global user.email "your@email.com"
git config --global core.autocrlf false
```

## <a name="UbuntuVisualCode"></a>Visual Code (optional)

```sh
# Add Code repository
sudo apt-get install wget gpg apt-transport-https
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
rm -f packages.microsoft.gpg

# Install Visual Code
sudo apt update
sudo apt install code

code --version
```

## <a name="UbuntuPython"></a>Python

```sh
sudo apt update

# Install Python3 and its virtual environment
sudo apt install python3 python3-venv

python3 --version
```

## <a name="UbuntuPostgreSQL"></a>PostgreSQL

```sh
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib postgresql-client

psql --version

# Check if PostgreSQL is installed
sudo dpkg --status postgresql
sudo systemctl status postgresql.service
```

### PostgreSQL create an user, a DB and grant privileges

Enter psql command line terminal

```sh
sudo su - postgres
psql
```

Replace theUsername, thePassword and theDB

> ***postgres=#*** CREATE USER theUsername WITH PASSWORD 'thePassword';\
> *CREATE ROLE*
>
> ***postgres=#*** CREATE DATABASE theDB;\
> *CREATE DATABASE*
>
> ***postgres=#*** GRANT ALL PRIVILEGES ON DATABASE theDB TO theUsername;\
> *GRANT*
>
> ***postgres=#*** \q

## PostgreSQL install PGAdmin4

```sh
curl https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo apt-key add
sudo sh -c 'echo "deb https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list && apt update'

# Install pyadmin4
sudo apt install pgadmin4
sudo /usr/pgadmin4/bin/setup-web.sh
```

Access PGADmin4 in http://localhost/pgadmin4 (or open the app)

1. Add new server.
2. General tab \
  *Name:* localhost-servers
3. Connection tab \
  *Host:* localhost \
  *Port:* 5432 \
  *Maintenance database:* postgres \
  *Username:* theUsername
4. Advanced tab
  *Host address:* localhost


## <a name="UbuntuDocker"></a>Docker and docker-compose

```sh
# Update the apt package index
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg lsb-release

# Add dockers official gpg key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin docker-compose docker-desktop

docker --version
docker-compose --version

sudo groupadd docker
sudo usermod -aG docker $USER

gpg --generate-key
pass init <pub>
```

## <a name="UbuntuAirflow"></a>Airflow

You can follow instructions on https://airflow.apache.org/docs/apache-airflow/stable/start/local.html

```sh
mkdir airflow_project
cd airflow_project

# Create a virtual environment
python3 -m venv py_env
source py_env/bin/activate
```

Create a file install_airflow.sh

```sh
#!/bin/bash

# Airflow needs a home. `~/airflow` is the default, but you can put it
# somewhere else if you prefer (optional)
export AIRFLOW_HOME=~/airflow

# Install Airflow using the constraints file
AIRFLOW_VERSION=2.3.3
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
# For example: 3.7
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
```

Run it

```sh
chmod 775 install_airflow.sh
./install_airflow.sh

# Show airflow version
airflow version
```

### Initialize Airflow DB

Before you can use Airflow you have to initialize its database. The database contains information about historical & running workflows, connections to external data sources, user management, etc. Once the database is set up, Airflow's UI can be accessed by running a web server and workflows can be started.

The default database is a SQLite database, which is fine for this exercuse. In a production setting you'll probably be using something like MySQL or PostgreSQL. You'll probably want to back it up as this database stores the state of everything related to Airflow.

Airflow will use the directory set in the environment variable `AIRFLOW_HOME` to store its configuration and our SQlite database. This directory will be used after your first Airflow command. If you don't set the environment variable `AIRFLOW_HOME`, Airflow will create the directory `~/airflow/` to put its files in.

```sh
#export AIRFLOW_HOME=$(pwd)
export AIRFLOW_HOME=~/airflow

airflow db init

# Change username, firstname and lastname.
# It will ask for a password
airflow users create --username admin --firstname Ricardo --lastname Gzz --role Admin --email admin@domain.com

# Make sure the PostgreSQL is enabled
pip install apache-airflow-providers-postgres
pip install pandas
```

Then you need to open two terminals at `0_local/airflow_project/` path.

```sh
# Create a new terminal at 0_local/airflow_project/. Run airflow webserver
# export AIRFLOW_HOME=$(pwd)
export AIRFLOW_HOME=~/airflow
source py_env/bin/activate
airflow webserver -p 8088

# Create a new terminal at 0_local/airflow_project/. Run airflow scheduler.
# export AIRFLOW_HOME=$(pwd)
export AIRFLOW_HOME=~/airflow
source py_env/bin/activate
airflow scheduler
```

All you need to do, is to go to http://localhost:8088 to check out the user interface. You will have to login entering the username and password you created before (`airflow users create`).

To configure Database connection, follow the steps:

1. Go to Admin / Connections
2. Click (+) Add new record
3. ***Connection id:*** postgres_conn_id \
   ***Connection type:*** Postgres \
   ***Host:*** \
   ***Schema:*** (table name) \
   ***Login:*** (username) \
   ***Password:*** (password) \
   ***Port:*** (Postgres default port is 5432)

Now you are ready to place your dags inside $AIRFLOW_HOME/dags/ directory (`~/airflow/dags/`).

For this exercise, once you have Airflow up and running, copy the dags folder inside `0_local/airflow_project/dags` (including `sql` subfolder) inside `~/airflow/`. Run the DAG in Airflow, and verify the PostgreSQL database has the ingested CSV records.