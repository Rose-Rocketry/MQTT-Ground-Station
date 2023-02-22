FROM debian:sid-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
  direwolf \
  gnuradio \
  hackrf

WORKDIR /app
COPY main.py encode.py ./

CMD python3 main.py
