#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygtk
pygtk.require('2.0')
import gtk
from gtk import  MessageDialog, Dialog, Window

class dlgAviso(MessageDialog):

    def __init__(self, parent_window = None, message = ""):
        MessageDialog.__init__(self,parent_window,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                gtk.MESSAGE_INFO,gtk.BUTTONS_OK,
                unicode(StringType(message)).encode('utf-8'))
        self.set_default_response(gtk.BUTTONS_OK)
        self.connect('response', lambda dialog, response: dialog.destroy())
        self.show()

class dlgError(Dialog):

    def __init__(self, parent_window = None, message = "", quit = None, trace = True):
        Dialog.__init__(self,
                unicode(StringType("Error")).encode('utf-8'),
                parent_window,
                0,
                (gtk.STOCK_OK, gtk.RESPONSE_OK))

        self.set_default_size(400, 150)
        hbox = gtk.HBox(False, 8)
        hbox.set_border_width(8)
        self.vbox.pack_start(hbox, False, False, 0)
        stock = gtk.image_new_from_stock(
                                        gtk.STOCK_DIALOG_ERROR,
                                        gtk.ICON_SIZE_DIALOG)
        hbox.pack_start(stock, False, False, 0)
        try:
            label = gtk.Label(unicode(StringType(message)).encode('utf-8'))
        except:
            label = gtk.Label("Ha ocurrido un error.")
        hbox.pack_start(label, True, True, 0)
        if trace:
            sw = gtk.ScrolledWindow()
            sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            textview = gtk.TextView()
            textbuffer = textview.get_buffer()
            sw.add(textview)
            sw.show()
            textview.set_editable(False)
            textview.set_cursor_visible(False)
            textview.show()
            t = StringType(sys.exc_info()[0]) + "\n"
            t += StringType(sys.exc_info()[1]) + "\n"
            t += "Traza:\n"
            for i in traceback.format_tb(sys.exc_info()[2]):
                t += i + "\n"
            textbuffer.set_text(t)
            expander = gtk.Expander("Detalles")
            expander.add(sw)
            expander.set_expanded(True)
            self.vbox.pack_start(expander, True, True)
        self.show_all()
        self.response = self.run()
        self.destroy()

class dlgSiNo(Dialog):

    def __init__(self, parent_window = None, message = None, window_title = None):
        Dialog.__init__(self,
                window_title,
                parent_window,
                0,
                (gtk.STOCK_NO, gtk.RESPONSE_NO, gtk.STOCK_YES, gtk.RESPONSE_YES))
        hbox = gtk.HBox(False, 8)
        hbox.set_border_width(8)
        self.vbox.pack_start(hbox, False, False, 0)
        stock = gtk.image_new_from_stock(
                                        gtk.STOCK_DIALOG_QUESTION,
                                        gtk.ICON_SIZE_DIALOG)
        hbox.pack_start(stock, False, False, 0)
        label = gtk.Label(message)
        hbox.pack_start(label, True, True, 0)
        self.show_all()
        self.response = self.run()
        self.destroy()

def messagedialog(dialog_type, short, long=None, parent=None,
                  buttons=gtk.BUTTONS_OK, additional_buttons=None):
    d = gtk.MessageDialog(parent=parent, flags=gtk.DIALOG_MODAL,
                          type=dialog_type, buttons=buttons)

    if additional_buttons:
        d.add_buttons(*additional_buttons)

    d.set_markup(short)
    d.set_position(gtk.WIN_POS_CENTER_ALWAYS)

    if long:
        if isinstance(long, gtk.Widget):
            widget = long
        elif isinstance(long, basestring):
            widget = gtk.Label()
            widget.set_markup(long)
        else:
            raise TypeError("long must be a gtk.Widget or a string")

        expander = gtk.Expander(_("Haga click aquí para más detalles."))
        expander.set_border_width(6)
        expander.add(widget)
        d.vbox.pack_end(expander)

    d.show_all()
    response = d.run()
    d.destroy()
    return response

def error(short, long=None, parent=None):
    """Displays an error message."""
    return messagedialog(gtk.MESSAGE_ERROR, short, long, parent)

def info(short, long=None, parent=None):
    """Displays an info message."""
    return messagedialog(gtk.MESSAGE_INFO, short, long, parent)

def yesno(text, parent=None):
    return messagedialog(gtk.MESSAGE_WARNING, text, None, parent,
                         buttons=gtk.BUTTONS_YES_NO)

