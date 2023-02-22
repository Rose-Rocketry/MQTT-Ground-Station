import subprocess
import os
import threading
from encode import encode as GREncoder
from tempfile import NamedTemporaryFile
from time import sleep

IQ_RATE = 2_000_000
AUDIO_RATE = 100_000
FREQ = int(144.390e6)

with NamedTemporaryFile(suffix=".wav") as file_wav:
    print("Generating packet audio")
    subprocess.run(
        ["gen_packets", "-r", str(AUDIO_RATE), "-o", file_wav.name],
        stdout=subprocess.DEVNULL,
        check=True,
    )

    iq_r, iq_w = os.pipe()

    print("Generating IQ samples")
    encoder = GREncoder(file_wav.name, iq_w, IQ_RATE, AUDIO_RATE)
    encoder.start()

    def encode_and_close():
        with os.fdopen(iq_w):
            encoder.wait()

    encode_thread = threading.Thread(target=encode_and_close)
    encode_thread.start()

    with os.fdopen(iq_r) as iq_r:
        print("Send data to SDR")
        sdr = subprocess.run(
            [
                "hackrf_transfer",
                "-t", "-",
                "-f", str(FREQ),
                "-s", str(IQ_RATE),
                "-x", "40"
            ],
            stdin=iq_r,
            check=True,
            timeout=10,
        )

    print("Exiting...")
    encode_thread.join()

    print(file_wav.name)
