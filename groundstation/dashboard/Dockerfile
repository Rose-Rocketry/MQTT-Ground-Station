FROM node:slim as build_client
WORKDIR /build
COPY client/package.json client/yarn.lock /build/
RUN yarn --frozen-lockfile
COPY client /build/
RUN yarn build

FROM python:slim
WORKDIR /app
RUN pip install quart paho-mqtt
COPY server/app.py ./
COPY --from=build_client /build/dist dist

CMD [ "quart", "run", "-p", "5000", "--host", "0.0.0.0" ]
