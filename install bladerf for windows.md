# install bladerf for windows
might not be worth it, windows super slow now
have problem with opening vscode and sublime text

from https://github.com/Nuand/bladeRF/wiki/Getting-Started:-Windows/1a1a1a6285e9af6df2c9e6b2d8f66afbb4192751
- install bladerf for windows
- install library
not successful update driver bladerf into `libusbK USB Devices.`
```
Installing libusb
Download the latest Windows binary release of libusb, which also include development headers http://sourceforge.net/projects/libusb/files/libusb-1.0/libusb-1.0.20/libusb-1.0.20.7z/download
Note: you may need to download and install 7-zip from 7-zip.org to open this file.
Extract the contents to a location of your choice. Make note of this location so that you can later provide it to CMake. The default configuration assumes that files will be in C:/Program Files (x86)/libusb-1.0.20 If you wish to change the directory, use the -DLIBUSB_PATH= option for CMake.
Get the device driver installer (zadig): http://sourceforge.net/projects/libwdi/files/zadig/
Open Zadig.
Go to Device->Create New Device.
Type a device name (i.e., "bladeRF") in the text box. In the driver spinbox, select libusbK. Specify the VID/PID (2cf0/5246) in the USB ID fields.
Plug the device into the computer and open Device Manager. A new device called bladeRF should show up with a yellow bang next to it in device manager.
Right-click on the bladeRF entry and select "Update Driver Software...".
Choose "Browse my computer for driver software"
"Let me pick from a list of device drivers on my computer".
Click "Have Disk..." and point it to the location that Zadig installed the driver to (C:\usb_driver).
```