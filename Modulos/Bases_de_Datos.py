#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import gtk
import sqlite3
import os
import shutil

from sugar.activity import activity
datos = activity.get_activity_root()+"/data/datos/"
if not os.path.exists(datos+"Claves.py"):
	nuevo = open(datos+"Claves.py", "w")
	nuevo.write("primera=True")
	nuevo.close()

class Bases_de_Datos():

	def limpiar(self, entry, event):
		entry.set_text("")


	def aceptar(self, widget, entry, dialog, entry0):
		self.clave = entry.get_text()
		self.usuario = entry0.get_text()

		if self.usuario and self.clave:
			nuevo = open(datos+"Claves.py")
			nuevo.write("primera=%s \nusuario=%s \nclave=%s" % ("False", self.usuario, self.clave))
			nuevo.close()			
			
			pos_anterior = os.getcwd() # Guardo la direccion actual 
			os.chdir(datos) # Me muevo al directorio de datos para importar
			import Claves
			os.chdir(pos_anterior) # me muevo de vuelta a la posicion anterior (que deberia ser: /home/olpc/Activities/AguBrowser.activity/)

			dialog.destroy()

	def comprobar_datos(self, usuario, clave):
		
		if usuario == Claves.usuario and clave == Claves.clave: datos = "Coinciden"
		else: datos = "No coinciden"

		return datos


	def __init__(self):
		pass
		"""
		pos_anterior = os.getcwd() # Guardo la direccion actual 
		os.chdir(os.environ["HOME"]+"/.sugar/default/org.ceibaljam.AguBrowser/data/datos/") # Me muevo al directorio de datos para importar
		import Claves
		os.chdir(pos_anterior) # me muevo de vuelta a la posicion anterior (que deberia ser: /home/olpc/Activities/AguBrowser.activity/)

	
		if Claves.primera: # Si el valor es True (Verdadero)

			dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO) # Un dialogo de mensaje
			dialog.set_title("Crear usuario - AguBrowser 1.5") # Titulo
			dialog.set_markup("Parece que es la primera vez que ejecutas AguBrowser 1.5. \n En esta version debes crear un usuario \n para poder controlar la configuracion \n e el historial. Llena el formulario: ") # INFO

			self.clave = False
			self.usuario = False

			usuario = gtk.Entry(max=12) # Entrada de usuario
			usuario.set_text("Usuario")

			
			clave = gtk.Entry(max=12) # Entrada de clave
			clave.set_text("Contraseña")
			clave.set_visibility(False) # Aparecen los puntitos en vez de los caracteres
			clave.set_property("caps-lock-warning", True) # Advierte si esta activada la tecla Bloq Mayus

			clave.connect("button-press-event", self.limpiar)
			usuario.connect("button-press-event", self.limpiar)
			guardar = gtk.Button("Aceptar/Accept")

			guardar.connect("clicked", self.aceptar, clave, dialog, usuario)
		
			dialog.vbox.add(usuario)
			dialog.vbox.add(clave)
			dialog.vbox.add(guardar)
			dialog.vbox.show_all()

			dialog.run()
			dialog.destroy()"""
