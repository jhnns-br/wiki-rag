FROM "nvidia/cuda:12.0.0-cudnn8-runtime-ubuntu22.04"

WORKDIR /app

COPY . /app
COPY requirements.txt requirements.txt
RUN apt-get update
RUN apt update
RUN apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget -y
RUN apt install python3 -y
RUN apt install python3-pip -y
RUN pip install --no-deps -r requirements.txt

