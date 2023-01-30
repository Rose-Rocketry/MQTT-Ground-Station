FROM debian:buster-slim as build
RUN apt-get update && apt-get install -y \
  git \
  build-essential

WORKDIR /src
RUN git clone -b v1.3.3 --depth 1 --single-branch https://github.com/Rose-Rocketry/mosquitto.rsmb .
WORKDIR /src/rsmb/src
RUN make broker_mqtts

FROM debian:buster-slim
COPY --from=build /src/rsmb/src/broker_mqtts /bin/rsmb
COPY rsmb.hardware.conf rsmb.simulated.conf /etc/

EXPOSE 10883 1883
