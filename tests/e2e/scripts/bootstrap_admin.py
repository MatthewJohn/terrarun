#!python

import terrarun
import terrarun.models.user
import terrarun.models.user_token

admin_user = terrarun.User.get_by_username("root")
if not admin_user:
    admin_user = terrarun.User.create_user(
        username="root",
        email="root@internal",
        password="randomstring",
        site_admin=True
    )

user_token = terrarun.models.user_token.UserToken.create(
    user=admin_user,
    type=terrarun.models.user_token.UserTokenType.USER_GENERATED,
    description='Created via initial setup'
)

print(user_token.token)
