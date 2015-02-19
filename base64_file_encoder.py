#!/usr/bin/env python

# base64_file_encoder.py: Encode current image to base64 and put it in image directory, option available in menu: File/Encode to base64

#     Copyright 2015 Marcin Karpezo <marcin@karpezo.pl>
#
#     This program is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 2 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program; if not, write to the Free Software
#     Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import base64
import re
from gimpfu import *

def plugin_main() :
    # great encoing line taken from:
    # http://dev-maziarz.blogspot.com/2015/02/gimp-how-to-export-image-to-base64.html
    # Thanks!

    file = gimp.image_list()[0].filename
    output_file = re.sub(r'png$', 'base64', file)

    opened_file = open(output_file, "w")
    opened_file.write(base64.b64encode(open(file, "rb").read()))
    opened_file.close()

register(
    "base64_file_encoder",
    "Base64 encoding",
    "Encodes current image to base64 and stores it in a text file",
    "Marcin Karpezo <marcin@karpezo.pl>",
    "Marcin Karpezo <marcin@karpezo.pl>",
    "2015",
    "Encode to base64",
    "*",
    [
    ],
    [],
    plugin_main,
    menu = "<Image>/File/Save/"
)

main()
