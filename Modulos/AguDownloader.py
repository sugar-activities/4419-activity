#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#   AguDownloader.py por:
#   Agustin Zuiaga <aguszs97@gmail.com>
#   Python Joven - Utu Rafael Peraza 
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import subprocess
import time
import gobject
import gtk, os

import sys

from sugar.activity import activity

descargas = os.path.join(activity.get_activity_root(), "data/Descargas/")
if not os.path.exists(descargas): os.mkdir(descargas)

class Descargar(gtk.Window):	

	def comenzar_descarga(self):
		print "La descarga comenzara"
		os.system("reset")
		salida = "/tmp/out_abrowse%d" % time.time()
		args = "%s %s %s %s %s" % ("wget", "-P", descargas, self.url, "--no-check-certificate")

		entrada = "/tmp/in_abrowse%d" % time.time()

		self.descargar = subprocess.Popen(args, shell=True, stdout=open(salida, "w+b"), stderr=open(salida, "r+b"), universal_newlines=True)
		salida1 = open(salida, "r")		

		self.time_out = gobject.timeout_add(100, self.set_info, salida1)

	def set_info(self, salida):
		salida.flush()
		for x in salida.readlines():
			sp = x.split()
			print sp

			try: 
				self.barra.set_text(self.texto)
				self.ajuste.set_value(self.porcentaje)
				self.ajuste.value_changed()
			except: pass
			
			try:
				try:
					for z in x.split()[-1]:
						if z == "s":
				        		self.tiempo_restante = x.split()[-1]
				  			self.informacion.set_text(self.tiempo_restante+" "+self.velocidad)
	    
      			        except: pass	
	
				if "K" in sp[-2]: 
					self.velocidad = sp[-2]
					self.info_label.set_text(self.tiempo_restante+"  "+self.velocidad)

				
				try:
					for y in sp[-3]:
						if y == "%":
							self.texto = "Descargando " + x.split(" ")[-3]
		      					self.barra.set_text(self.texto)
		      					hallar_porcentaje = self.texto.split("Descargando ")[1]
		      					porcentaje = int(hallar_porcentaje.split("%")[0])
							self.porcentaje = porcentaje

							self.ajuste.set_value(porcentaje)
							self.ajuste.value_changed()
				except: pass
				if sp[-2] == "guardado":
					self.texto = "Descarga Completa..."
					self.barra.set_text(self.texto)
					#self.descargar.kill()

					os.system("clear")

					def _clipboard_get_func_cb(clipboard, selection_data, info, data):
	
						selection_data.set('text/uri-list', 8, self.direccion+self.url.split("/")[-1])	

					def _clipboard_clear_func_cb(clipboard, data):

						pass
		
					def copiar(widget):
						clipboard = gtk.Clipboard()
						clipboard.set_with_data([('text/uri-list', 0, 0)],
												_clipboard_get_func_cb,
												_clipboard_clear_func_cb)
	
					boton = gtk.Button("Copiar al Portapapeles")
					self.main.add(boton)
					boton.show_all()
			
					boton.connect("clicked", copiar)
	
					gobject.source_remove(self.time_out)
					n.show()					

			except: pass

			if "error" in sp or "Error" in sp or "ERROR" in sp:
				self.texto = "Ocurrio un error...."
	      			self.barra.set_text(self.texto)
				


		return True

	def __init__(self, archivo):

		gtk.Window.__init__(self)
		self.ajuste = gtk.Adjustment(value=0, lower=0, upper=100, step_incr=1, page_incr=1)
		self.barra = gtk.ProgressBar(self.ajuste)
		self.barra.show_all()


		self.texto = "Comenzando descarga...."
		self.barra.set_text(self.texto)
		
		self.url = archivo
			
		self.porcentaje = 0

		self.info_label = gtk.Label()
		self.info_label.show_all()
		
		descarga = self

		descarga.set_title("Descargando - AguBrowse")
		descarga.set_icon_from_file("Iconos/logo.png")
		
		main = gtk.VBox()
		
		hbox = gtk.HBox()
		hbox.add(self.barra)


		cancelar = gtk.ToolButton()
		image = gtk.image_new_from_stock(gtk.STOCK_CANCEL, gtk.ICON_SIZE_BUTTON)
		cancelar.set_icon_widget(image)
		#cancelar.connect("clicked", cancelar, self, descarga)

		main.add(hbox)	
		main.add(self.info_label)

		self.main = main

		descarga.add(main)
		descarga.show_all()
		
		self.comenzar_descarga()	
		
