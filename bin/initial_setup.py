#!python

"""Create initial data"""

import sys
sys.path.append('.')

from argparse import ArgumentParser

import terrarun
from terrarun.database import Database

parser = ArgumentParser()
parser.add_argument('--organisation', type=str, default="default")
parser.add_argument('--organisation-email', dest="organisation_email", type=str, required=True)
parser.add_argument('--lifecycle', type=str, default="default")
parser.add_argument('--environment', type=str, nargs="+", default=["dev", "prod"])

args = parser.parse_args()

if not (org := terrarun.Organisation.get_by_name_id(name_id=args.organisation)):
    org = terrarun.Organisation.create(name=args.organisation, email=args.organisation_email)
    print('Created organisation:', org.api_id)

lifecycle = terrarun.Lifecycle.create(organisation=org, name=args.lifecycle)
print('Created lifecycle:', lifecycle.name, lifecycle.api_id)

org.update_attributes(default_lifecycle=lifecycle)
print('Updated organisation default lifecycle')

for environment_name in args.environment:
    environment = terrarun.Environment.create(organisation=org, name=environment_name)
    print('Created environment:', environment.name, environment.api_id)

    lifecycle.associate_environment(environment=environment, order=0)
    print('Added environment to lifecycle')

print('Done')
