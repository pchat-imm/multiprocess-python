import numpy as np
from bladerf import _bladerf

def setup_receiver(sdr, freq, sample_rate, bandwidth, gain_mode, gain_rx):
    # Configure RX channel
    rx_ch = sdr.Channel(_bladerf.CHANNEL_RX(0))     # 0 = first receive channel

    rx_ch.frequency = center_freq
    rx_ch.sample_rate = sample_rate
    rx_ch.bandwidth = sample_rate/2
    rx_ch.gain_mode = _bladerf.GainMode.Manual
    rx_ch.gain = gain_rx

    sdr.sync_config(layout=_bladerf.ChannelLayout.RX_X1,   # Rx port 1 or port 2
                fmt = _bladerf.Format.SC16_Q11,        # init16s
                num_buffers    = 16,
                buffer_size    = 8192,
                num_transfers  = 8,
                stream_timeout = 3500)
    
    return sdr, rx_ch

def receive_samples(sdr, rx_ch, num_samples):
    # create recieve buffer
    bytes_per_sample = 4    # SC16Q11 use 4 bytes per sample
    buf = bytearray(1024 * bytes_per_sample)

    # enable module: remember before calling sync_rx() or it showed timeouts or other errors
    print("Starting recieve")
    rx_ch.enable = True

    ## Receive loop
    # elif: Limited by either buffer size or remaining samples needed
    x = np.zeros(num_samples, dtype=np.complex64)   # output
    num_samples_read = 0
    while True:
        if num_samples > 0 and num_samples_read == num_samples:
            break
        elif num_samples > 0:
            num = min(len(buf) // bytes_per_sample, num_samples - num_samples_read)
        else:  # case num_samples = 0
            num = len(buf) // bytes_per_sample
        # receive IQ samples, read raw data from ADC of SDR for number of samples (num) into the buffer (buf)
        sdr.sync_rx(buf, num)   # Read into buffer  
        # Converts buffer to 16-bit integers(2 bytes per samples len(samples) = len(buf)/2)
        samples = np.frombuffer(buf, dtype=np.int16)    
        samples = samples[0::2] + 1j * samples[1::2]    # I + jQ
        samples /= 2048.0   # scale to -1 to 1 (its using 12 bit ADC, 2^12 = 4096 => +-2048)
        x[num_samples_read:num_samples_read+num] = samples[0:num]   # store buf in samples array
        num_samples_read += num    # increment num_samples_read by num, by 1024 samples

    print("Stopping")
    rx_ch.enable = False
    print(x[0:10])      # look at first 10 IQ samples


if __name__ == "__main__":
    center_freq = 3410e6
    sample_rate = 10e6
    bandwidth = sample_rate/2
    gain_rx = 35
    gain_mode = _bladerf.GainMode.Manual

    devices = _bladerf.get_device_list()
    rx_sdr = _bladerf.BladeRF(devinfo=devices[0])
    rx_ch = rx_sdr.Channel(_bladerf.CHANNEL_RX(0))     # 0 = first receive channel
    sdr, rx_ch = setup_receiver(rx_sdr, center_freq, sample_rate, bandwidth, gain_mode, gain_rx)

    num_samples = 460800
    rx_IQ = receive_samples(rx_sdr, rx_ch, num_samples)