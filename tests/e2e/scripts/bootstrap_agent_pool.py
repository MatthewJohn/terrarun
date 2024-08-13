#!python

import terrarun
import terrarun.models.user
import terrarun.models.user_token

admin_user = terrarun.User.get_by_username("root")

agent_pool = terrarun.AgentPool.create(name="Global", organisation=None, organisation_scoped=False)

agent_token = terrarun.AgentToken.create(
    agent_pool=agent_pool,
    created_by=admin_user
)

print(agent_token.token)