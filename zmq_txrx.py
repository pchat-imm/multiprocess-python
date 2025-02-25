## Toturial: https://pysdr.org/content/bladerf.html

from bladerf import _bladerf
import numpy as np
import zmq
import csv


def setup_transmitter(freq, sample_rate, bandwidth, gain_tx):
    "setup bladeRF transmitter"

    devices = _bladerf.get_device_list()
    sdr = _bladerf.BladeRF(devinfo=devices[0])
    sdr.enable_module(_bladerf.CHANNEL_TX(0), True)
    print("sdr serials: ", sdr.get_serial())

    # Configure TX channel
    tx_ch = sdr.Channel(_bladerf.CHANNEL_TX(0))
    tx_ch.frequency = freq
    tx_ch.sample_rate = sample_rate
    tx_ch.bandwidth = bandwidth
    tx_ch.gain = gain_tx

        # Set up synchronous stream configuration
    sdr.sync_config(
        layout=_bladerf.ChannelLayout.TX_X1,
        fmt=_bladerf.Format.SC16_Q11,
        num_buffers=16,
        buffer_size=8192,
        num_transfers=8,
        stream_timeout=3500
    )

    return sdr, tx_ch

def transmit_tone(sdr, tx_ch, buf, num_samples, repeat):
    """
    Transmit the generated tone repeatedly.
    """
    repeat_remaining = repeat - 1
    tx_ch.enable = True
    print("Starting Transmit!")
    
    while repeat_remaining >= 0:
        sdr.sync_tx(buf, num_samples)  # Write to bladeRF
        print(f"Repeat remaining: {repeat_remaining}")
        if repeat_remaining > 0:
            repeat_remaining -= 1
        else:
            break

    print("Stopping Transmit")
    tx_ch.enable = False

def load_rx_srsRAN(input_file):
    #'''load a file of receive signal from base station (SDR) using srsRAN'''
    
    # count number of rows to pre-allocate memory
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        num_samples = sum(1 for _ in f)

    # create empty array for stored IQ samples in complex type
    waveform = np.zeros(num_samples, dtype=np.complex64)

    # read the file, strip, change i -> j, convert to complex
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        for i,row in enumerate(reader):
            IQComplex = row[0].strip().replace('i','j')
            waveform[i] = complex(IQComplex)
            
    # scale to int16 representation, convert to int16 samples
    waveform *= 32767
    samples = waveform.view(np.int16)

    # return bytes
    return samples.tobytes(), num_samples


def transmit_file(sdr, tx_ch, samples, num_samples):
    """
    Transmit the generated tone repeatedly.
    """
    tx_ch.enable = True
    print("Starting Transmit!")
    
    sdr.sync_tx(samples, num_samples)  # Write to bladeRF

    print("Stopping Transmit")
    tx_ch.enable = False

if __name__ == "__main__":
    center_freq = 3410e6
    sample_rate = 10e6
    bandwidth = sample_rate/2
    gain_tx = 0
    num_samples = int(1e6)

    sdr, tx_ch = setup_transmitter(center_freq, sample_rate, bandwidth, gain_tx)
    samples, num_samples = load_rx_srsRAN('waveform_IQComplex_fllay.csv')
    transmit_file(sdr, tx_ch, samples, num_samples)