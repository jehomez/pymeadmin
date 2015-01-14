import gtk
import treetohtml
from mensajes import info, yesno
from datetime import date, datetime
from articulos import DlgArticulo
from articulos_produccion import ArticulosEnProduccion
from modelo import Model
from comunes import punto_coma, coma_punto, caracter_a_logico, logico_a_caracter, calcular_iva_venta, calcular_precio_neto, calcular_precio_venta, calcular_utilidad


class ActualizarPrecios:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre=None):
        builder = gtk.Builder()
        builder.add_from_file('dlgActualizacionPrecios.glade')
        builder.connect_signals(self)

        self.dialogo = builder.get_object('dialogo')
        self.scroll = builder.get_object('scroll_window')
        self.tree = builder.get_object('vista')
        self.lista = builder.get_object('lista')
        self.opcion_algunos = builder.get_object('algunos')
        self.opcion_todos = builder.get_object('todos')
        self.dialogo.show()
        

    def on_todos_group_changed(self, *args):
        pass

    def on_algunos_group_changed(self, *args):
        if self.opcion_algunos.get_active() == 1:
            self.scroll.set_visible(True)
            self.tree.set_visible(True) 

    def on_aceptar_clicked(self, *args):
        pass

    def on_salir_clicked(self, *args):
        self.on_dialogo_destroy()

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()

if __name__ == '__main__':
    ActualizarPrecios().main()
