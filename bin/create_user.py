#!python

"""Create user"""

import sys
sys.path.append('.')

from argparse import ArgumentParser

import terrarun
import terrarun.models.user
from terrarun.database import Database

parser = ArgumentParser()
parser.add_argument('--username', type=str, required=True)
parser.add_argument('--password', type=str, required=True)
parser.add_argument('--email', type=str, required=True)
parser.add_argument('--site-admin', action='store_true')

args = parser.parse_args()

user = terrarun.User(username=args.username, email=args.email, site_admin=args.site_admin, user_type=terrarun.models.user.UserType.NORMAL)
user.password = args.password
session = Database.get_session()
session.add(user)
session.commit()
