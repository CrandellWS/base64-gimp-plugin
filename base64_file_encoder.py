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
import subprocess
import pygtk
pygtk.require('2.0')
import gtk
import gtk.gdk
import gobject
from gimpfu import *

def plugin_main(img) :
    # great encoing line taken from:
    # http://dev-maziarz.blogspot.com/2015/02/gimp-how-to-export-image-to-base64.html
    # Thanks!

    file = img.filename

    if not file:
      message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
      message.set_markup("Please save your file first!")
      message.run()

    (prefix, sep, suffix) = file.rpartition('.')

    output_file = prefix + '.base64'

    opened_file = open(output_file, "w")
    base64_f = base64.b64encode(open(file, "rb").read())
    opened_file.write(base64_f)

    for clip_target in [gtk.gdk.SELECTION_PRIMARY, gtk.gdk.SELECTION_CLIPBOARD]:
      clipboard = gtk.clipboard_get(clip_target)
      clipboard.set_can_store(None)
      clipboard.set_text(base64_f, -1)
      clipboard.store()

    #gobject.timeout_add(10000, gtk.main_quit)
    gtk.main()

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
      (PF_IMAGE, "image", "Input image", None),
    ],
    [],
    plugin_main,
    menu = "<Image>/File/Save/"
)

main()

# ToDo: communication about file save path afterwards
