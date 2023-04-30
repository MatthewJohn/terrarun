# terrarun

Open source alternative to Terraform Cloud/Enterprise

Current backend features (all partial):

 * Organisations
 * Workspaces
 * Users
 * Teams
 * Authentication
 * Terraform state management
 * Configuration versions
 * Tasks/Workspace tasks/Task stage/Task results
 * Tags (partial)
 * Support for:
   * Terraform init
   * Terraform plan
   * Terraform apply
   * Terraform state

Current UI implementation:
 * Authentication
 * Organisation create/list
 * User token view/create
 * Workspace create/list
 * Tasks
 * Workspace tasks
 * View runs, plan output, apply output and perform actions on runs

## WARNING

This project is in early development - only use this project for fun purposes

Under no circumstances should this project be used _ANYWHERE_ outside of development of the project.

## Installation

```
git clone ssh://git@gitlab.dockstudios.co.uk:2222/pub/terrarun.git
cd terrarun

# Setup python virtualenv and install dependencies
virtualenv -p python3 venv
. venv/bin/activate
pip install -r requirements.txt

# Upgrade database and add initial organisation/environments
python ./bin/initial_setup.py --migrate-database --organisation-email=test@localhost.com

# Create admin user
python ./bin/create_user.py --username admin --password=password --email=admin@localhost --site-admin                   

# Setup UI packages
pushd ui
npm install  # Verify this
popd
```

## Running inside Docker

```
cp .env-example .env
# Update BASE_URL in .env
# Add SSL certs as public.pem and private.pem to ./ssl directory

docker-compose up

# Wait for DB to startup
docker-compose logs -f

# Perform initial setup
docker-compose exec api python ./bin/initial_setup.py --migrate-database --organisation-email=test@localhost.com --admin-username=admin --admin-email=admin@localhost --admin-password=password --global-agent-pool=default-pool
```

### Save and reuse your local config

    # Copy database file into your repository
    docker cp <CONTAINER_ID>:/app/test.db .

    # Attach local file as a volume into a docker container by adding this to your docker run execution
    -v $PWD/test.db:/app/test.db


## Usage

    # Running without SSL certs (not recommended)
    python ./terrarun.py &
    cd ui
    ng serve -o

    # With SSL Certs (required for running with terraform)
    python ./terrarun.py --ssl-cert-private-key ./private.pem --ssl-cert-public-key ./public.pem
    cd ui
    ng serve -o --public-host=<hostname> --ssl --ssl-cert ../public.pem --ssl-key ../private.pem

## Dev SSL certs

    # An example script to generate CA certificate and SSL certs is in `bin/create_dev_ssl_certs.sh`.
    ./bin/create_dev_ssl_certs.sh localhost  ## Or whichever domain is to be used for local development
    # The private/public key can be found at ./example/ssl-certs/dev.key and ./example/ssl-certs/dev.crt, respectively.
    # The public CA key can be found at ./example/ssl-certs/myCA.pem, which can be added to system trusted certs for browser and verication by Terraform CLI

 
## Contributing

This project is solely based on the API documentation by Hashicorp at https://www.terraform.io/cloud-docs/api-docs/.

To avoid any issues with Hashicorp, it is required that contributors state that they have never used, trialled or viewed any in-depth training/videos of Terraform Cloud or Terraform Enterprise.


## Authors and acknowledgment

 * Matt Comben <matthew@dockstudios.co.uk>

## License

Copyright (c) 2022 Matt Comben <matthew@dockstudios.co.uk>

Terrarun can not be copied and/or distributed without the express
permission of the authors

