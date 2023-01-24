FROM rust:1-slim-buster as build
RUN apt-get update && apt-get install -y git
WORKDIR /src
RUN git clone -b v1.2.0-2 https://github.com/Rose-Rocketry/xbnet .
RUN cargo build --release

FROM debian:buster-slim
COPY --from=build /src/target/release/xbnet /bin/xbnet
COPY xb-initfile.txt /etc/xb-initfile.txt

CMD [ "xbnet", \
  "/dev/ttyxbnet", \
  "--serial-speed", "115200", \
  "--initfile", "/etc/xb-initfile.txt", \
  "tun", \
  "--disable-ipv6", \
  "--set-up", \
  "--set-ip", "10.82.104.2/24" ]
