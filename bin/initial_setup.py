#!python

"""Create initial data"""

import subprocess
import sys
sys.path.append('.')

from argparse import ArgumentParser

import terrarun
import terrarun.models.user
from terrarun.database import Database

parser = ArgumentParser()
parser.add_argument('--organisation', type=str, default="default")
parser.add_argument('--organisation-email', dest="organisation_email", type=str, required=True)
parser.add_argument('--admin-username', dest='admin_username', type=str, required=True, help='Username of default admin user', default='builtin-admin')
parser.add_argument('--admin-email', dest='admin_email', type=str, required=True, help='Email of default admin user')
parser.add_argument('--admin-password', dest='admin_password', type=str, required=True, help='Password of default admin user')
parser.add_argument('--lifecycle', type=str, default="default")
parser.add_argument('--environment', type=str, nargs="+", default=["dev", "prod"])
parser.add_argument('--migrate-database', action='store_true', dest='migrate_database')
parser.add_argument('--global-agent-pool', dest="global_agent_pool", type=str, default=None, help="Name of global agent pool to be created")

args = parser.parse_args()

if args.migrate_database:
    res = subprocess.check_call(['alembic', 'upgrade', 'head'])
    if res:
        print('Failure during DB migration')
        sys.exit(1)


if not (org := terrarun.Organisation.get_by_name_id(name_id=args.organisation)):
    org = terrarun.Organisation.create(name=args.organisation, email=args.organisation_email)
    print('Created organisation:', org.api_id)

# Create built-in admin user
if not (admin_user := terrarun.User.get_by_username(args.admin_username)):
    print(f'Creating admin user: {args.admin_username}')
    admin_user = terrarun.User.create_user(
        username=args.admin_username,
        email=args.admin_email,
        password=args.admin_password,
        site_admin=True
    )
    print(f'Created admin user: {admin_user.api_id}')

if not (lifecycle := terrarun.Lifecycle.get_by_name_and_organisation(organisation=org, name=args.lifecycle)):
    lifecycle = terrarun.Lifecycle.create(organisation=org, name=args.lifecycle)
    print('Created lifecycle:', lifecycle.name, lifecycle.api_id)

    org.update_attributes(default_lifecycle=lifecycle)
    print('Updated organisation default lifecycle')

for environment_name in args.environment:
    if not terrarun.Environment.get_by_name_and_organisation(organisation=org, name=environment_name):
        # Create environment lifecycle group
        lifecycle_environment_group = terrarun.LifecycleEnvironmentGroup.create(
            lifecycle=lifecycle
        )
        print('Created lifecycle environment group:', lifecycle_environment_group.api_id)
        environment = terrarun.Environment.create(organisation=org, name=environment_name)
        print('Created environment:', environment.name, environment.api_id)

        lifecycle_environment_group.associate_environment(environment=environment)
        print('Added environment to lifecycle environment group')

## Create default agent pool
if args.global_agent_pool and not terrarun.AgentPool.get_by_name_and_organisation(name=args.global_agent_pool, organisation=None):
    print("Creating agent pool")
    agent_pool = terrarun.AgentPool.create(name=args.global_agent_pool, organisation=None, organisation_scoped=False)
    print(f"Created agent pool: {agent_pool.name}")
    print("Creating agent token")
    agent_token = terrarun.AgentToken.create(
        agent_pool=agent_pool,
        created_by=admin_user
    )
    print(f"Created agent token: {agent_token.token}")


print('Done')
