#! /usr/bin/python
# -*- coding: iso-8859-15 -*-
#
__author__='atareao'
__date__ ='$12/10/2010'
#
# <Un script para instalar una impresora PDF en Ubuntu.>
#
# Copyright (C) 2010 Lorenzo Carbonell
# lorenzo.carbonell.cerezo@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#

import shlex, subprocess
import os
import shutil
import gtk

def ejecuta(comando):
	args = shlex.split(comando)
	p = subprocess.call(args)
	return p

def mod_config_file(dire):
	config_file="/etc/cups/cups-pdf.conf"
	input = open(config_file)
	output = open("~cups-pdf.conf",'w')
	if dire[1:]!="/":
		dire=dire+"/"
	for s in input.xreadlines():
		if s[:3]=="Out":
			output.write("Out "+dire+"\n")
		else:
			output.write(s)
	output.close()
	input.close()
	#shutil.copyfile("~cups-pdf.conf",config_file)
	ejecuta("gksu mv ~cups-pdf.conf /etc/cups/cups-pdf.conf")

if __name__ == "__main__":
	HOME=os.getenv("HOME")+"/"
	os.chdir(HOME)
	ejecuta("gksu apt-get install cups-pdf")
	ejecuta("gksu chmod +s /usr/lib/cups/backend/cups-pdf")
	dialog = gtk.FileChooserDialog("Selecciona el directorio de destino de tus PDFs", None, gtk.FILE_CHOOSER_ACTION_CREATE_FOLDER, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
	dialog.set_default_response(gtk.RESPONSE_OK)
	filter = gtk.FileFilter()
	filter.set_name("All files")
	filter.add_pattern("*")
	dialog.add_filter(filter)
	response = dialog.run()
	dirname=HOME+"PDF"
	if response == gtk.RESPONSE_OK:
		dirname=dialog.get_filename()
		if not os.path.exists(dirname):
			os.makedirs(dirname)
	elif response == gtk.RESPONSE_CANCEL:
		if not os.path.exists(HOME+"PDF/"):
			os.makedirs(HOME+"PDF/")
	dialog.destroy()
	mod_config_file(dirname)
	ejecuta("sudo chown -hR root /usr/lib/cups/filter")
	ejecuta("sudo chown -hR root /usr/lib/cups/backend")
	ejecuta("sudo chgrp -hR root /usr/lib/cups/filter")
	ejecuta("sudo chgrp -hR root /usr/lib/cups/backend")
	exit(0)

