

import pygtk
import gtk

class  Ventana:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('ventana.glade')
        builder.connect_signals(self)

        self.windows = builder.get_object('window1')
        self.windows.show()

if __name__ == '__main__':
    a = Ventana()
    a.main()



