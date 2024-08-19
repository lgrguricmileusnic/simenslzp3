# Siemens LZP3

Siemens compresses firmware for its programmable logic controllers with a modified version of the LZP3 algorithm. The obscurity of this variant presents an obstacle in security research and analysis because the firmware is impossible to decompress with standard decompression tools. Therefore, researchers can only apply a black box approach to analysis, which requires access to the PLC hardware on which the firmware will be loaded.

This repo contains **siemens_lzp.py** python module and accompanying python script **fw_decompress.py** which can be used for decompressing Siemens PLC firmware. \

Note:\
The script was tested on compressed firmware made for S7-1200 PLCs.


## Usage
```
usage: fw_decompress.py [-h] [-k] input_file output_file

positional arguments:
  input_file         compressed firmware file name
  output_file        decompressed firmware output file name

options:
  -h, --help         show this help message and exit
  -k, --keep-output  keep output in case of failure
```
