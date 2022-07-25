# terrarun

Open source alternative to Terraform cloud, enabling remote terraform plan/applies

## Installation

    git clone ssh://git@gitlab.dockstudios.co.uk:2222/pub/terrarun.git
    cd terrarun
    virtualenv -p python3 venv
    . venv/bin/activate
    pip install -r requirements.txt

## Usage

    python ./terrarun.py


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
