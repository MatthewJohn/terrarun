# terrarun

Open source alternative to Terraform Cloud/Enterprise

Current features:

 * Organisations
 * Workspaces
 * Users
 * Teams
 * Authentication
 * Terraform state management
 * Configuration versions
 * Support for:
 ** Terraform init
 ** Terraform plan
 ** Terraform apply

Current UI implementation:
 * Authentication
 * Organisation create/list
 * User token view/create

## WARNING

This project is in early development - only use this project for fun purposes

Under no circumstances should this project be used _ANYWHERE_ outside of development of the project.

## Installation

    git clone ssh://git@gitlab.dockstudios.co.uk:2222/pub/terrarun.git
    cd terrarun
    
    # Setup python virtualenv and install dependencies
    virtualenv -p python3 venv
    . venv/bin/activate
    pip install -r requirements.txt
    
    # Upgrade database
    alembic upgrade head
    
    # Create admin user
    python ./bin/create_user.py --username admin --password=password --email=admin@localhost --site-admin                   
    
    # Setup UI packages
    pushd ui
    npm install  # Verify this
    popd

## Usage

    # Running without SSL certs (not recommended)
    python ./terrarun.py &
    cd ui
    ng serve -o

    # With SSL Certs (required for running with terraform)
    python ./terrarun.py --ssl-cert-private-key ./private.pem --ssl-cert-public-key ./public.pem
    cd ui
    ng serve -o --public-host=<hostname> --ssl --ssl-cert ../public.pem --ssl-key ../private.pem
    


## Authors and acknowledgment

 * Matt Comben <matthew@dockstudios.co.uk>

## License

Copyright (c) 2022 Matt Comben <matthew@dockstudios.co.uk>

Terrarun can not be copied and/or distributed without the express
permission of the authors

## Project status

This is a proof-of-concept implementation of Terraform Cloud, attempting to implement:
 * Authentication
 * Terraform plan
 * Terraform apply
