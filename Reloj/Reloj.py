#!/usr/bin/env python

import gtk
import time
import gobject

class Reloj(gtk.HBox):

	def actualizar(self, imagenes, cantidad):
		for x in time.strftime("%H:%M:%S"):
			imagenes[cantidad].set_from_file("Reloj/"+x+".gif")
			cantidad += 1

		return True
	
	def __init__(self):

		gtk.HBox.__init__(self, False, 1)

		imagenes = [gtk.Image(), gtk.Image(), gtk.Image(), gtk.Image(), gtk.Image(), gtk.Image(), gtk.Image(), gtk.Image()]
		cantidad = 0

		for x in imagenes: self.add(x)
	
		self.show_all()

		gobject.timeout_add(1000, self.actualizar, imagenes, cantidad)
