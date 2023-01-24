FROM debian:buster-slim as build
RUN apt-get update && apt-get install -y \
  git \
  build-essential \
  cmake \
  libasound2-dev

WORKDIR /src
RUN git clone -b 1.6 --depth 1 --single-branch https://github.com/wb2osz/direwolf .
WORKDIR /src/build
RUN cmake -DCMAKE_INSTALL_PREFIX=/install .. && make -j4 install

FROM debian:buster-slim
RUN apt-get update && apt-get install -y \
  libasound2

COPY --from=build /install/ /usr/
COPY direwolf.simulated.conf /etc/
