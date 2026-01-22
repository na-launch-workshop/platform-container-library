FROM registry.access.redhat.com/ubi9/python-311:latest

USER root

# Install dependencies required for Terraform, make, and other tools
RUN curl -L https://github.com/openshift/rosa/releases/download/v1.2.48/rosa_Linux_x86_64.tar.gz -o rosa.tar.gz \
        && tar -xvzf rosa.tar.gz \
        && mv rosa /usr/local/bin/rosa \
        && chmod +x /usr/local/bin/rosa

USER 1001
