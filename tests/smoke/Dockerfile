FROM python:3

# Install docker CLI
RUN apt-get update
RUN apt-get install ca-certificates curl --assume-yes
RUN install -m 0755 -d /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
RUN chmod a+r /etc/apt/keyrings/docker.asc

RUN echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

RUN apt-get update
RUN apt-get install docker-ce-cli easy-rsa openssl wget unzip --assume-yes

# Install Terraform agent
RUN cd /tmp; wget https://releases.hashicorp.com/tfc-agent/1.8.0/tfc-agent_1.8.0_linux_amd64.zip; unzip tfc-agent_1.8.0_linux_amd64.zip; cp tfc-agent* /usr/local/bin/

# Install Terraform
RUN cd /tmp; wget https://releases.hashicorp.com/terraform/1.4.5/terraform_1.4.5_linux_amd64.zip; unzip terraform_1.4.5_linux_amd64.zip; cp terraform /usr/local/bin/
