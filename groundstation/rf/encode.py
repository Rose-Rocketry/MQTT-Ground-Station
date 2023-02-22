#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr

class encode(gr.top_block):
    def __init__(self, wav_path: str, iq_fd: int, samp_rate: int, audio_rate: int):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        assert samp_rate % audio_rate == 0
        interpolate = samp_rate // audio_rate

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=interpolate,
                decimation=1,
                taps=[],
                fractional_bw=0)
        self.blocks_wavfile_source_0 = blocks.wavfile_source(wav_path, False)
        self.blocks_file_descriptor_sink_0 = blocks.file_descriptor_sink(gr.sizeof_char*1, iq_fd)
        self.blocks_complex_to_interleaved_char_0 = blocks.complex_to_interleaved_char(False, 127.0)
        self.analog_nbfm_tx_0 = analog.nbfm_tx(
        	audio_rate=(audio_rate * interpolate),
        	quad_rate=samp_rate,
        	tau=(75e-6),
        	max_dev=5e3,
        	fh=(-1.0),
                )


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_nbfm_tx_0, 0), (self.blocks_complex_to_interleaved_char_0, 0))
        self.connect((self.blocks_complex_to_interleaved_char_0, 0), (self.blocks_file_descriptor_sink_0, 0))
        self.connect((self.blocks_wavfile_source_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.analog_nbfm_tx_0, 0))
