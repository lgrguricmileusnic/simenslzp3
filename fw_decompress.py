#!/usr/bin/env python3
import os
from util import *
import siemens_lzp

args = parse_argv()
input_filename = args.input_file
output_filename = args.output_file
keep_output = args.keep_output

if not os.access(input_filename, os.F_OK):
    errx(1, "File {} does not exist.".format(input_filename))
if not os.access(input_filename, os.R_OK):
    errx(1, "Missing read permission for file {}".format(input_filename))
if os.access(output_filename, os.F_OK):
    if not os.access(output_filename, os.W_OK):
        errx(1, "Missing write permission for file {}".format(output_filename))

in_file = open(input_filename, "rb")
success, out = siemens_lzp.decompress_upddata(in_file.read())
in_file.close()

if keep_output or success:
    out_file = open(output_filename, "wb")
    out_file.write(out)
    out_file.close()

if not success:
    errx(2, "Failed.")
    
print("Success.")


