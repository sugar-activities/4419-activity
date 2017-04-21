#!/usr/bin/env python

import gtk
import os
import gobject

imagen = gtk.image_new_from_file(os.getcwd()+"/Iconos/screen_saver.png")

class Iniciar_Espera():

	def mostrar_ocultar(self, event, other):
		self.conteo = False # Desactiva el conteo

		self.screen_saver.hide_all() # Oculta la ventana de protector
		self.main.show_all() # Muestra la ventana de AguBrowse

		self.conteo = True # Vuelve a activar el conteo

	def mostrar(self):
		self.screen_saver.show_all()
		self.main.hide_all()
		
		return self.conteo

	def mover_imagen(self):
		if self.para_arriba and self.para_la_iz:
			self.y += 10
			self.x += 10

		elif self.para_arriba and self.para_la_de:
			self.y += 10
			self.x -= 10

		elif self.para_abajo and self.para_la_iz:
			self.y -= 10
			self.x += 10
		
		elif self.para_abajo and self.para_la_de:
			self.y -= 10
			self.x -= 10

		self.para_abajo = False
		self.para_arriba = False
		self.para_la_de = False
		self.para_la_iz = False

		if self.y == 450 and self.x == 350:
			self.para_abajo = True
			self.para_la_de = True
		
		elif self.y == -450 and self.x == -350:
			self.para_arriba = True
			self.para_la_de = True
	
		elif self.y == 450 and self.x == -350:
			self.para_la_iz = True
			self.para_abajo = True

		elif self.y == -450 and self.x == 350:
			self.para_arriba = True
			self.para_la_iz = True

		if self.x < -350:
			self.x = -350
	
		if self.x > 350:
			self.x = 350

		if self.y > -450:
			self.y = -450
		
		if self.y < 450:
			self.y = 450		
	
	
		self.fixed.move(imagen, self.x, self.y)	

		return True
			
			 

	def iniciar(self):

	        self.screen_saver = gtk.Window()
		self.screen_saver.set_position(gtk.WIN_POS_CENTER)
		self.screen_saver.resize(900, 700)
		self.screen_saver.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0,0,0,1))

		self.fixed = gtk.Fixed()
		self.fixed.put(imagen, self.x, self.y)
		
		self.screen_saver.add(self.fixed)
		self.conteo = False
		gobject.timeout_add(30000, self.mostrar)
		gobject.timeout_add(100, self.mover_imagen)

	
	def __init__(self, main):

		self.x = 0
		self.y = 0

		self.para_arriba = True
		self.para_abajo = False

		self.para_la_iz = True
		self.para_la_de = False

		self.primera = True
		self.main = main

		self.iniciar()
		
		self.main.add_events(gtk.gdk.POINTER_MOTION_MASK) # Agregamos eventos
		self.main.connect("motion-notify-event", self.mostrar_ocultar) # Cuando se mueve el mouse

if __name__ == "__main__":

	print "Este programa solo funciona cuando lo ejecuta la AguBrowse"
