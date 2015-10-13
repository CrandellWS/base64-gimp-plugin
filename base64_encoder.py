#!/usr/bin/env python

# base64_file_coder.py: Encode (and todo decode) current image to(from) 
# base64 and put it in image directory, option available in menu: File/Base64 Encode

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

from os.path import dirname, basename, exists, split, isfile
from os import getcwd, sep, makedirs, remove, rmdir
from mimetypes import guess_type
from base64 import b64encode
import pygtk
pygtk.require('2.0')
import gtk
from gimpfu import *

# from gimpenums import *

def check_file_by_mime_type(argument, process_mime_types):
    switcher = {
        "image/png": process_mime_types["png"],
        "image/jpeg": process_mime_types["jpeg"],
        "image/pjpeg": process_mime_types["jpeg"],
        "image/gif": process_mime_types["gif"],
    }
    use_file = switcher.get(argument, False)
    return use_file

def FixupMimeType(argument):
    """Helper function that normalizes platform differences in the mime type
        returned by the Python's mimetypes.guess_type API.
        from https://android.googlesource.com/platform/external/chromium_org/tools/grit/+/android-cts-5.0_r3%5E1..android-cts-5.0_r3/
    """
    mappings = {
        'image/x-png': 'image/png',
        'image/pjpeg': 'image/jpeg'
    }
    return mappings[argument] if argument in mappings else argument
    
def check_file(found_file, process_mime_types):
    mtype = FixupMimeType(guess_type(found_file)[0])
    if(mtype != None):
        if(check_file_by_mime_type(mtype, process_mime_types)):
            return process_file(found_file, mtype)
    return False

def get_base64_string(file_name):
    openedImage = open(file_name, "rb").read()
    return b64encode(openedImage)

def make_base64_file(prefix, base64_string):
    output_file = prefix + '.base64'
    opened_file = open(output_file, "w")
    opened_file.write(base64_string)
    opened_file.close()

def process_file(file_name, mtype):
    ret = {}
    ret["base64_string"] = get_base64_string(file_name)
    (ret["prefix"], ret["sep"], ret["suffix"]) = basename(file_name).rpartition('.')
    ret["dir_name"] = dirname(file_name)
    ret["mtype"] = mtype
    return ret
    
def process_xcf(file_name, keep_png):
    ret = {}
    xcf_image = pdb.gimp_file_load(file_name, file_name.encode("UTF-8"))
    (prefix, file_sep, suffix) = basename(file_name).rpartition('.')
    layer = pdb.gimp_image_merge_visible_layers(xcf_image, CLIP_TO_IMAGE)
    ret["dir_name"] = dirname(file_name)
    png_file = ret["dir_name"]+sep+'b64_png'+sep+prefix+".png"
    pdb.file_png_save2(xcf_image, layer, png_file, png_file, 1, 9, 1, 1, 0, 1, 1, 1, 1)
    openedImage = open(png_file, "rb").read()
    ret["base64_string"] = b64encode(openedImage)
    if(not keep_png):
        remove(png_file)
    (ret["prefix"], ret["sep"], ret["suffix"]) = basename(file_name).rpartition('.')
    ret["mtype"] = "image/png"
    return ret
    
def multiple_html_files(data, overwrite):
    html_template = """<img src='data:%s;base64,%s' alt='%s' />""" % (data["mtype"], data["base64_string"], data["prefix"])
    #<img src="data:image/xxx;base64,XXXX..." alt = "filename">
    output_file = data["dir_name"]+sep+"b64_html"+sep+data["prefix"] + '.html'
    if(isfile(output_file)):
        if(not overwrite):
            o = 1
            while True:
                output_file = data["dir_name"]+sep+"b64_html"+sep+data["prefix"] + str(o) + '.html'
                if(isfile(output_file)):
                    o = o + 1
                else:
                    break
                
    opened_html = open(output_file, "w")
    opened_html.write(html_template)
    opened_html.close()
    
def single_html_file(data, overwrite):
    output_file = data[0]["dir_name"]+sep+split(data[0]["dir_name"])[1] + '.html'
    if(isfile(output_file)):
        if(not overwrite):
            o = 1
            while True:
                output_file = data[0]["dir_name"]+sep+split(data[0]["dir_name"])[1] + str(o) + '.html'
                if(isfile(output_file)):
                    o = o + 1
                else:
                    break
    opened_html = open(output_file, "a+")
    for file_data in data:
        html_template = """
        <br/>
        <img src='data:%s;base64,%s' alt='%s' />""" % (data[file_data]["mtype"], data[file_data]["base64_string"], data[file_data]["prefix"])
        #<img src="data:image/xxx;base64,XXXX..." alt = "filename">
        opened_html.write(html_template)
    opened_html.close()

def base64_file(data, overwrite):
    output_file = data["dir_name"]+sep+"b64_data"+sep+data["prefix"] + '.base64'
    if(isfile(output_file)):
        if(not overwrite):
            o = 1
            while True:
                output_file = data["dir_name"]+sep+"b64_data"+sep+data["prefix"] + str(o) + '.base64'
                if(isfile(output_file)):
                    o = o + 1
                else:
                    break
    opened_file = open(output_file, "w")
    opened_file.write(data["base64_string"])
    opened_file.close()
    
def plugin_batch_encoder( source, b64_output, html_output, xcf, keep_png, png, jpeg, gif, overwrite) :
    # great encoing line taken from:
    # http://dev-maziarz.blogspot.com/2015/02/gimp-how-to-export-image-to-base64.html
    # Thanks, Marcin Karpezo <marcin@karpezo.pl> for the plugin framework.
    #
    #
    # tfunctions = {0:one,1:two,2:three}
    # func = tfunctions[v1]
    # func(dialog)
    
    pdb.gimp_progress_pulse();
    
    process_mime_types = {"png":png,"jpeg":jpeg,"gif":gif}
    glob_result = pdb.file_glob(source+sep+'*.*',  1)
    # filecount = glob_result[0]
    file_data = {}
    i = 0 
    for found_file in glob_result[1]:
        include_file = check_file(found_file, process_mime_types)
        if(include_file != False):
            file_data[i] = include_file
            i = i + 1 
    if(xcf): 
        if not exists(source+sep+"b64_png"):
            makedirs(source+sep+"b64_png")   
        glob_result = pdb.file_glob(source+sep+'*.xcf',  1)
        for found_file in glob_result[1]:
            file_data[i] = process_xcf(found_file, keep_png)
            i = i + 1
        if(not keep_png):
            rmdir(source+sep+"b64_png")
        
    if(html_output == "single_html_file"):
        single_html_file(file_data, overwrite)
    if(html_output == "multiple_html_files"):
        if not exists(source+sep+"b64_html"):
            makedirs(source+sep+"b64_html")
        for data in file_data:
            multiple_html_files(file_data[data], overwrite)
    if(b64_output):
        if not exists(source+sep+"b64_data"):
            makedirs(source+sep+"b64_data")
        for data in file_data:
            base64_file(file_data[data], overwrite)
    return

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
    mtype = guess_type(inFile)

    openedImage = open(inFile, "rb").read()
    base64_f = b64encode(openedImage)
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

    for clip_target in [gtk.gdk.SELECTION_PRIMARY, gtk.gdk.SELECTION_CLIPBOARD]:
        clipboard = gtk.clipboard_get(clip_target)
        clipboard.set_can_store(None)
        clipboard.set_text(base64_f, -1)
        clipboard.store()
    message.destroy()
    gtk.main()
    return

register(
    "base64_batch_encoder",
    "Base64 batch encoding all png/gif/jpeg from directory",
    "Encodes all png/jpeg/gif in a folder to base64 saving the results",
    "William Crandell <william@crandell.ws",
    "William Crandell <william@crandell.ws",
    "2015",
    "Base64 _Batch Encode",
    "",
    [
        (PF_DIRNAME, "directory", "Directory", getcwd()),
        (PF_TOGGLE,"b64_output",   "Base64 Output:", 1),
        (PF_RADIO, "html_output", "HTML Output:", 'single_html_file', (("None", False),("1 HTML file", 'single_html_file'),("1 HTML file per Image", 'multiple_html_files'))),
        (PF_TOGGLE, "xcf",   "Process XCF Files:", 1),
        (PF_TOGGLE, "keep_png",   "Save PNGs from XCFs:", 0),
        (PF_TOGGLE, "png",   "Process PNG Files:", 1),
        (PF_TOGGLE, "jpeg",   "Process JPEG Files:", 1),
        (PF_TOGGLE, "gif",   "Process GIF Files:", 1),
        (PF_OPTION,"overwrite",   "Collision Method:", 0, ["Rename","Overwrite"]),
    ],
    [],
    plugin_batch_encoder,
    menu = "<Image>/File/Export/Base_64/"
)

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
    menu = "<Image>/File/Export/Base_64/"
)


main()
