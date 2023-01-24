FROM rust:1-slim
RUN apt-get update && apt-get install -y git
WORKDIR /src
RUN git clone -b v1.2.0-2 https://github.com/Rose-Rocketry/xbnet .
RUN cargo build
