#!/usr/bin/env python

# base64_file_coder.py: Encode (and todo decode) current image to(from) base64 and put it in image directory, option available in menu: File/Base64 Encode

#     Copyright 2015 William Crandell <william@crandell.ws>
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
import mimetypes
from gimpfu import *

def plugin_encode() :
    # great encoing line taken from:
    # http://dev-maziarz.blogspot.com/2015/02/gimp-how-to-export-image-to-base64.html
    # Thanks, Marcin Karpezo <marcin@karpezo.pl> for the plugin framework.

    inFile = None
    dialog = gtk.FileChooserDialog("Choose file to base64 encode...",
                                 None,
                                 gtk.FILE_CHOOSER_ACTION_OPEN,
                                 (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                  gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    dialog.set_default_response(gtk.RESPONSE_OK)

    filter = gtk.FileFilter()
    filter.set_name("Images")
    filter.add_mime_type("image/png")
    filter.add_mime_type("image/jpeg")
    filter.add_mime_type("image/gif")
    filter.add_pattern("*.png")
    filter.add_pattern("*.jpg")
    filter.add_pattern("*.gif")
    dialog.add_filter(filter)

    response = dialog.run()

    message = None
    if response == gtk.RESPONSE_OK:
        message = gtk.MessageDialog(type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK)
        inFile=dialog.get_filename()
    elif response == gtk.RESPONSE_CANCEL:
        message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
        message.set_markup('Closed, no files selected')
        message.destroy()
        gimp.quit()

    dialog.destroy()
    message.set_markup(inFile)
    message.run()

    (prefix, sep, suffix) = inFile.rpartition('.')

    output_file = prefix + '.base64'

    message.set_markup(output_file)
    message.run()
    opened_file = open(output_file, "w")
    mtype = mimetypes.guess_type(inFile)

    openedImage = open(inFile, "rb").read()
    base64_f = base64.b64encode(openedImage)
    opened_file.write(base64_f)
    opened_file.close()

    html_template = """<img src='data:%s;base64,%s' alt='%s' />""" % (mtype[0], base64_f, prefix)
    #<img src="data:image/xxx;base64,XXXX..." alt = "filename">
    output_html = prefix + '.html'
    message.set_markup(output_html)
    message.run()
    opened_html = open(output_html, "w")
    opened_html.write(html_template)
    opened_html.close()
    message.destroy()

    for clip_target in [gtk.gdk.SELECTION_PRIMARY, gtk.gdk.SELECTION_CLIPBOARD]:
      clipboard = gtk.clipboard_get(clip_target)
      clipboard.set_can_store(None)
      clipboard.set_text(base64_f, -1)
      clipboard.store()

    return

register(
    "base64_file_encoder",
    "Base64 encoding",
    "Encodes selected image to base64 and stores it in a text file",
    "William Crandell <william@crandell.ws",
    "William Crandell <william@crandell.ws",
    "2015",
    "Base64 Encode",
    "",
    [],
    [],
    plugin_encode,
    menu = "<Image>/File/Save/"
)

#@TODO add decoder
# register(
#     "base64_file_decoder",
#     "Base64 decoding",
#     "Decodes selected image to base64 and stores it in a text file",
#     "William Crandell <william@crandell.ws",
#     "William Crandell <william@crandell.ws",
#     "2015",
#     "Base64 Decode",
#     "",
#     [],
#     [],
#     plugin_decode,
#     menu = "<Image>/File/Save/"
# )
main()

# ToDo: communication about file save path afterwards
