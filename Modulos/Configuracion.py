#!/usr/bin/env python

#   Configuracion.py por:
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

import gtk
import pygtk
import os, sys
import pango

pygtk.require("2.0")

datos = os.path.join(os.getenv("HOME"), ".AguBrowse/")

class Configuracion(gtk.Window):

	def delete_event(self, window, data):
		self.destroy()
		home_web = open(datos+"Web_Home", "w")
		home_web.write(self.entry.get_text())
		home_web.close()
		self.browser.update_configuracion()
	
	def boton_home_cb(self, boton):
		bool = boton.get_active()
		home = open(datos+"Boton_Home", "w")
		if bool:
			home.write("Si")

		else:
			home.write("No")

		home.close()

	def set_buscador(self, menuitem, direccion, boton):
		buscador = open(datos+"Buscador", "w")
		buscador.write(menuitem.get_label()+"!"+direccion)
		buscador.close()

		boton.set_label(menuitem.get_label()+", Haz click aqui para cambiar")

	def menu_busquedas(self, boton1, event):
		boton = event.button
		tiempo = event.time
		pos = (event.x, event.y)
		self.menu(boton1, boton, pos, tiempo)
		return

	def menu(self, widget, boton, pos, tiempo):
		menu = gtk.Menu()
		buscadores = {"Google" : "http://www.google.com.uy/#hl=es&biw=1280&bih=534&q=palabra_clave&aq=f&aqi=&aql=&oq=&fp=1e07aebe9596e838",
			      "Bing" : "http://www.bing.com/search?setmkt=es-XL&q=palabra_clave",
			      "Yahoo!" : "http://search.yahoo.com/search?ei=UTF-8&fr=crmas&p=palabra_clave",
			      "Wikipedia" : "http://es.wikipedia.org/wiki/Special:Search?search=palabra_clave",
                              "eBay" : "http://rover.ebay.com/rover/1/711-47294-18009-3/4?satitle=palabra_clave",
			      "Creative Commons" : "http://search.creativecommons.org/?q=palabra_clave"}
		for x in buscadores.keys():
			item = gtk.MenuItem(str(x))
			menu.append(item)
			item.connect_object("activate", self.set_buscador, item, buscadores[x], widget)
		menu.show_all()
		menu.popup(None, None, self.posicionar_menu, boton, tiempo, None)

	def posicionar_menu(self, a, b): pass

	def set_home_web(self, entry):
		home_web = open(datos+"Web_Home", "w")
		home_web.write(entry.get_text())
		home_web.close()
		self.browser.update_configuracion()
	
	def __init__(self, browser):
		
		gtk.Window.__init__(self)
		
		self.set_title("Configuracion - AguBrowse 2.0")
		self.resize(600, 300)

		# ***** Obtenemos la clase AguBrowse:
		self.browser = browser

		# ***** Contenedor
		main = gtk.VBox()
		self.add(main)

		# ***** NOTEBOOK
		pestanias = gtk.Notebook()
		main.add(pestanias)

		# ***** Basicas *****
		basicas = gtk.VBox()
		pestanias.append_page(basicas, gtk.Label("Basicas"))

		principal = gtk.Label("Pagina principal")
		principal.modify_font(pango.FontDescription("bold"))
		basicas.add(principal)
		basicas.add(gtk.Label("Abrir esta pagina web: "))
		
		entry = gtk.Entry()
		entry.set_text("http://www.google.com")
		entry.connect("activate", self.set_home_web)
		basicas.add(entry)
		self.entry = entry

		boton_home = gtk.CheckButton(label='Motrar el boton "Pagina de Inicio" en la barra de herramientas')
		boton_home.connect("toggled", self.boton_home_cb)
		boton_home.set_active(True)
		boton_home.modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.color_parse("skyblue"))
		boton_home.modify_bg(gtk.STATE_SELECTED, gtk.gdk.color_parse("yellow"))
		#basicas.add(boton_home)
		
		buscar = gtk.Label("Buscar")
		buscar.modify_font(pango.FontDescription("bold"))
		basicas.add(buscar)

		donde = gtk.Button("Google, Haz click aqui para cambiar")
		donde.connect("button-press-event", self.menu_busquedas)
		basicas.add(donde)


		def boton_notify(widget):
			bool = boton.get_active()
			home = open(datos+"Notificaciones", "w")
			if bool:
				home.write("Si")

			else:
				home.write("No")

			home.close()

		notify = gtk.CheckButton(label="Deseas que aparezca una notificacion cada vez \n que se termine de cargar una pagina")
		notify.modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.color_parse("skyblue"))
		notify.modify_bg(gtk.STATE_SELECTED, gtk.gdk.color_parse("yellow"))
		notify.set_active(True)
		notify.connect("toggled", boton_notify)

		quitbox = gtk.HButtonBox()
		quitbox.set_layout(gtk.BUTTONBOX_END)
		
		cerrar = gtk.Button("Cerrar")
		cerrar.connect("clicked", self.delete_event, None)
		quitbox.add(cerrar)		
		main.add(quitbox)
		self.show_all()

if __name__ == "__main__":
	Configuracion()
	gtk.main()
		
	
		
