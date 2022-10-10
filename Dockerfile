FROM python:3.10

WORKDIR /

RUN apt-get update && apt-get install --assume-yes curl unzip git && apt-get clean all

RUN bash -c 'git clone --depth=1 https://github.com/tfutils/tfenv.git ~/.tfenv; \
    ln -s ~/.tfenv/bin/* /usr/local/bin'


WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .


ENTRYPOINT [ "bash", "scripts/entrypoint.sh" ]
