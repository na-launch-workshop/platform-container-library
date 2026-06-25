import os
import gitlab
import gitlab.exceptions
import requests
from keycloak import KeycloakAdmin, KeycloakOpenIDConnection
import urllib3

## For the love of god disable the warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

KEYCLOAK_URL = f"https://keycloak.{os.getenv('DOMAIN')}/"
KEYCLOAK_REALM = "openshift"
KEYCLOAK_USER = os.getenv('KEYCLOAK_USERNAME')
KEYCLOAK_PASSWORD = os.getenv('KEYCLOAK_PASSWORD')
KEYCLOAK_CLIENT_ID = "admin-cli"

GITLAB_URL = f"https://gitlab.{os.getenv('DOMAIN')}"
GITLAB_USERNAME = os.getenv('GITLAB_USERNAME')
GITLAB_PASSWORD = os.getenv('GITLAB_PASSWORD')

#############################################
## Get OAuth Token for GitLab
#############################################
ACCESS_TOKEN = requests.post(
    f"{GITLAB_URL}/oauth/token", 
    json={
        "grant_type": "password",
        "username": GITLAB_USERNAME,
        "password": GITLAB_PASSWORD
    }, 
    headers={ 
        "Content-Type": "application/json"
    }, 
    verify=False
).json()["access_token"]


#############################################
## Connect to Keycloak as admin-cli
#############################################
kc = KeycloakAdmin(
    server_url=KEYCLOAK_URL,
    username=KEYCLOAK_USER,
    password=KEYCLOAK_PASSWORD,
    realm_name="openshift",  # login realm
    user_realm_name="master",
    verify=True,
)

#############################################
## Connect to GitLab
#############################################
gl = gitlab.Gitlab(
    url=GITLAB_URL,
    ssl_verify=False,
    api_version="4",
    oauth_token=ACCESS_TOKEN
)


def get_group_by_path(path):
    try:
        return gl.groups.get(path, lazy=False)
    except gitlab.exceptions.GitlabGetError:
        return None


def confirm_user_email(user_id, email):
    """Mark a user's email as verified (new or existing account)."""
    user = gl.users.get(user_id)
    if user.confirmed_at:
        return

    try:
        gl.http_post(
            f'/users/{user_id}/emails',
            post_data={'email': email, 'skip_confirmation': True},
        )
        if gl.users.get(user_id).confirmed_at:
            return
    except gitlab.exceptions.GitlabHttpError as err:
        if 'already been taken' not in str(err).lower():
            raise

    _, domain = email.rsplit('@', 1)
    temp_email = f"{user.username}+gitlab-sync@{domain}"

    try:
        gl.http_post(
            f'/users/{user_id}/emails',
            post_data={'email': temp_email, 'skip_confirmation': True},
        )
    except gitlab.exceptions.GitlabHttpError as err:
        if 'already been taken' not in str(err).lower():
            raise

    gl.http_put(
        f'/users/{user_id}',
        post_data={'email': temp_email, 'skip_reconfirmation': True},
    )

    try:
        gl.http_post(
            f'/users/{user_id}/emails',
            post_data={'email': email, 'skip_confirmation': True},
        )
    except gitlab.exceptions.GitlabHttpError as err:
        if 'already been taken' not in str(err).lower():
            raise

    gl.http_put(
        f'/users/{user_id}',
        post_data={'email': email, 'skip_reconfirmation': True},
    )

    if not gl.users.get(user_id).confirmed_at:
        try:
            gl.http_post(f'/users/{user_id}/approve')
        except gitlab.exceptions.GitlabHttpError:
            pass


def ensure_group_share(group, shared_group_id, access_level):
    """Ensure group is shared with shared_group_id at access_level."""
    group = gl.groups.get(group.id, lazy=False)
    for share in group.shared_with_groups or []:
        if share['group_id'] == shared_group_id:
            if share['group_access_level'] == access_level:
                return False
            group.unshare(shared_group_id)
            break

    group.share(shared_group_id, group_access=access_level)
    return True


#############################################
## Make sure the developers group exists and is
## Shared with self-provisioned as internal
#############################################
main_group = get_group_by_path('self-provisioned')
if not main_group:
    raise RuntimeError("Group 'self-provisioned' not found")

developers_group = get_group_by_path('developers')
if not developers_group:
    developers_group = gl.groups.create({
        'name': 'developers',
        'path': 'developers',
        'visibility': "internal",
        'auto_devops_enabled': False,
        'project_creation_level': "developer"
    })
    print(f"Developers group created: {developers_group.web_url}\n", flush=True)
else:
    print("Group 'developers' exists.\n", flush=True)

if ensure_group_share(main_group, developers_group.id, 40):
    print(
        f"Developers group added as maintainer of self-provisioned group: {developers_group.web_url}\n",
        flush=True,
    )

if ensure_group_share(developers_group, main_group.id, 50):
    print("Self-provisioned group added as owner of developers group\n", flush=True)

#########################################################
## Create the User & Assign them to the developers group
## Group
#########################################################
print("Syncing: Users\n", flush=True)
for kcuser in kc.get_users({}):
    email = kcuser.get('email')
    if not email:
        print(f"syncing: {kcuser['username']} skipped (no email in Keycloak)", flush=True)
        continue

    ########################################################################
    ## TRY to create user, don't check cause search is garbage in gitlab sdk
    ########################################################################
    try:
        gl.users.create({
            'email': email,
            'username': kcuser['username'],
            'name': f"{kcuser['firstName']} {kcuser['lastName']}",
            'force_random_password': True,
            'can_create_group': False,
            'skip_confirmation': True,
        })
        print(f"syncing: {kcuser['username']} created", flush=True)
    except gitlab.exceptions.GitlabCreateError:
        print(f"syncing: {kcuser['username']} exists", flush=True)

    matches = gl.users.list(username=kcuser['username'])
    if not matches:
        print(f"syncing: {kcuser['username']} failed (user not found in GitLab)", flush=True)
        continue

    try:
        confirm_user_email(matches[0].id, email)
        print(f"syncing: {kcuser['username']} email verified", flush=True)
    except gitlab.exceptions.GitlabError as err:
        print(f"syncing: {kcuser['username']} email verification failed: {err}", flush=True)


########################################################################
## Users are in there now one way or the other & since search is garbage
## and requires needless code just 
########################################################################
print("\nSyncing Users to Group: developers\n", flush=True)
glusers = gl.users.list()
for user in glusers:
    if user.username not in ["root", "ghost"] and not user.bot:

        ################################################################
        ## Add the user to developers group
        ################################################################
        try:
            developers_group.members.create({
                'user_id': user.id,
                'access_level': 30
            })
            print(f"syncing: {user.username} added to developers", flush=True)
        except gitlab.exceptions.GitlabCreateError:
            print(f"syncing: {user.username} already in developers", flush=True)
