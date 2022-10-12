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
parser.add_argument('--environment', type=str, default="default")

args = parser.parse_args()

if not (org := terrarun.Organisation.get_by_name_id(name_id=args.organisation)):
    org = terrarun.Organisation.create(name=args.organisation, email=args.organisation_email)

lifecycle = terrarun.Lifecycle.create(organisation=org, name=args.lifecycle)
environment = terrarun.Environment.create(organisation=org, name=args.environment)
lifecycle.associate_environment(environment=environment, order=0)
