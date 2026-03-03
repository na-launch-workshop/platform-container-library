# Sonatype Nexus Community Edition

The upstream Nexus application image is available from [github.com/sonatype](https://github.com/sonatype/docker-nexus3/blob/main/Dockerfile.rh.ubi.java21).  The `redhat/ubi9-minimal` base image from DockerHub was replaced with the Red Hat base image `registry.access.redhat.com/ubi9/ubi-minimal` as we want to use Red Hat base images and Kubernetes v1.34+ enforces fully qualified image names, and changes are maintained in [platform-docker-nexus3](https://github.com/na-launch-workshop/platform-docker-nexus3).

## Update Submodule

Clone Git repo and create dev branch:
```
git clone https://github.com/na-launch-workshop/platform-container-library.git
cd platform-container-library/nexus
git branch dev
git checkout dev
```

Update submodule to tagged version 3.78.1:
```
cd docker-nexus3
git submodule init
git submodule update
git branch
git checkout tags/3.78.1
```

Commit to dev branch:
```
cd ..
git status
git add docker-nexus3
git commit -S -m "Git submodule update to docker-nexus3 v3.78.1-02"
git push origin dev
```
