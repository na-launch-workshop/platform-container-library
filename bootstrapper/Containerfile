FROM python:3.11-slim

# Install dependencies required for Terraform, make, and other tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    virtualenv \
    ansible \
    git \
    j2cli \
    curl \
    unzip \
    sshpass \
    libcrack2 \
    make \
    azure-cli \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install OC CLI
RUN curl -LO https://mirror.openshift.com/pub/openshift-v4/clients/ocp/stable/openshift-client-linux.tar.gz && \
    tar -xvf openshift-client-linux.tar.gz && \
    mv oc /usr/local/bin/oc && \
    mv kubectl /usr/local/bin/kubectl && \
    chmod +x /usr/local/bin/oc /usr/local/bin/kubectl && \
    rm -f openshift-client-linux.tar.gz

# Install Terraform
ENV TERRAFORM_VERSION=1.6.0

RUN curl -fsSL https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip -o terraform.zip && \
    unzip terraform.zip && \
    mv terraform /usr/local/bin/terraform && \
    rm terraform.zip