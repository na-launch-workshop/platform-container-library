# Exporting Custom Plugins

[Package and publish a custom plugin] for `@backstage/plugin-scaffolder-backend-module-gitea`.

Refer to the [npm plugin docs] and [scaffolder actions docs] for additional details on the plugin.

Install dependencies, download code, and export custom plugin:
```
sudo dnf install -y node npm yarn
sudo npm install -g typescript
git clone https://github.com/backstage/backstage/
cd backstage/plugins/scaffolder-backend-module-gitea/
git checkout v1.47.0   # specify branch for release version of plugin, i.e. 0.2.17

# increase Javascript heap size to perform yarn build
yarn install
export NODE_OPTIONS="--max-old-space-size=6144"
npx tsc
npx @red-hat-developer-hub/cli@latest plugin export
```

Create an OCI image with dynamic packages.  The tag corresponds to the version field in `package.json`:
```
npx @red-hat-developer-hub/cli@latest plugin package --tag quay.io/na-east-launch/scaffolder-backend-module-gitea:0.2.17
podman login quay.io
podman push quay.io/na-east-launch/scaffolder-backend-module-gitea:0.2.17
```

** Don't forget to set the quay.io image to public. **

Custom plugins must use image digest to pass the integrity check.  Run the following:
```
skopeo inspect docker://quay.io/na-east-launch/scaffolder-backend-module-gitea:0.2.17
```

Using the digest, add this snippet to your values.yaml file:
```
plugins:
  - package: oci://quay.io/na-east-launch/scaffolder-backend-module-gitea@sha256:fc6faebce073c29410cc5f1f6c8595147fef5c1fac31170214bfd6dc0f36c0bf!backstage-plugin-scaffolder-backend-module-gitea
    disabled: false
```

[Package and publish a custom plugin]: https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.8/html/installing_and_viewing_plugins_in_red_hat_developer_hub/assembly-third-party-plugins#proc-export-third-party-plugins-rhdh_assembly-third-party-plugins
[npm plugin docs]: https://www.npmjs.com/package/@backstage/plugin-scaffolder-backend-module-gitea/
[scaffolder actions docs]: https://roadie.io/backstage/scaffolder-actions/publish-gitea/