FROM debian:buster-slim as build
RUN apt-get update && apt-get install -y \
  git \
  build-essential

WORKDIR /src
RUN git clone -b v1.3.2 https://github.com/Rose-Rocketry/mosquitto.rsmb .
WORKDIR /src/rsmb/src
RUN make broker_mqtts

FROM debian:buster-slim
COPY --from=build /src/rsmb/src/broker_mqtts /bin/rsmb
COPY rsmb.conf /etc/rsmb.conf

EXPOSE 10883 1883

CMD [ "rsmb", "/etc/rsmb.conf" ]
