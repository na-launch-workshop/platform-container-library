# Instructions

From the [following documentation](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/html/installing_ansible_plug-ins_for_red_hat_developer_hub/rhdh-install-ocp-helm_aap-plugin-rhdh-installing) for configuring the Ansible plug-ins for Developer Hub, we opted to copy the required registry.redhat.io images to our publicly hosted repository to bypass the authentication process needed to fetch the images:

```
skopeo copy docker://registry.redhat.io/ansible-automation-platform/automation-portal:2.1 docker://quay.io/na-east-launch/automation-portal:2.1
```
