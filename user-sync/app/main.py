import os
import gitlab
import requests
from keycloak import KeycloakAdmin, KeycloakOpenIDConnection
import urllib3

## For the love of god disable the warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

KEYCLOAK_URL = f"https://keycloak-keycloak.{os.getenv('DOMAIN')}/auth/"
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

#############################################
## Make sure the developers group exists and is
## Shared with self-provisioned as internal
#############################################
main_group = gl.groups.list(search='self-provisioned')[0]
dev_group = gl.groups.list(search='developers')

if len(dev_group) < 1:
    group = gl.groups.create({
        'name': 'developers',
        'path': 'developers',
        'visibility': "internal",
        'auto_devops_enabled': False,
        'project_creation_level': "developer"
    })
    main_group.share(group.id, group_access=40)
    print(f"Group created: {group.web_url}\n", flush=True)
else:
    print("Group 'developers' exists.\n", flush=True)


#########################################################
## Create the User & Assign them to the developers group
## Group
#########################################################
print("Syncing: Users\n", flush=True)
for kcuser in kc.get_users({}):

    ########################################################################
    ## TRY to create user, don't check cause search is garbage in gitlab sdk
    ########################################################################
    try:
        gl.users.create(
            email=kcuser['email'],
            username=kcuser['username'],
            name=f"{kcuser['firstName']} {kcuser['lastName']}",
            force_random_password=True,
            can_create_group=False
        )
        print(f"syncing: {kcuser['username']} success", flush=True)
    except:
        print(f"syncing: {kcuser['username']} success", flush=True)


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
            dev_group[0].members.create({
                'user_id': user.id, 
                'access_level': 30
            })
            print(f"syncing: {user.username} success", flush=True)
        except:
            print(f"syncing: {user.username} success", flush=True)