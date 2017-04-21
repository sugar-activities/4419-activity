#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#   AguBrowse.py por:
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



import gtk # www.gtk.org
import pygtk # www.pygtk.org
import os, sys 

try:
    import webkit
    from webkit import *	
except ImportError:
    try:
	import webkit_local
        from webkit_local import *
    except ImportError:
        print "Necesitas webkit para usar AguBrowser"
        sys.exit(0) 

import time, datetime
import subprocess 

import pango
import urllib, urllib2
import Modulos.Protector_de_Pantalla as Protector

import sqlite3
import pygame # www.pygame.org

from sugar.activity import activity

datos = os.path.join(activity.get_activity_root(), "data/datos/")
if not os.path.exists(datos):
	os.mkdir(datos)
	sesion = open(datos+"Sesion", "w")
	sesion.write("")
	sesion.close()
	historial = open(datos+"Historial", "w")
	historial.write("")
	historial.close()
	marcadores = open(datos+"Marcadores", "w")
	marcadores.write("")
	marcadores.close()
	bh = open(datos+"Boton_Home", "w")
	bh.write("Si")
	bh.close()
	search = open(datos+"Buscador", "w")
	search.write("Google!http://www.google.com.uy/#hl=es&biw=1280&bih=534&q=palabra_clave&aq=f&aqi=&aql=&oq=&fp=1e07aebe9596e838")
	search.close()
	wh = open(datos+"Web_Home", "w")
	wh.write("file://"+os.getcwd()+"/Home.html")
	wh.close()
	os.mkdir(datos+"/Paginas_Guardadas/")

if not os.path.exists(activity.get_activity_root()+"/data/Favicons/"): 
	os.mkdir(activity.get_activity_root()+"/data/Favicons/")

from Modulos.AguDownloader import *
from Modulos.Configuracion import *
from Modulos.Inspector import *
from Modulos.Pantalla_Completa import *
from Modulos.Bases_de_Datos import *
from Reloj.Reloj import Reloj
	

class AguBrowse(activity.Activity):

	def Salir(self, guardar):
		sesion = open(datos+"Sesion", "w")
		if guardar:
			sesion.write(str(self.navegador.get_main_frame().get_uri()))
		
		else:
			sesion.write("")
		
		sesion.close()
		
		os.remove(datos+"Marcadores")
		marcadores = open(datos+"Marcadores", "a")
		for x in self.marcadores.keys():
			marcadores.write(x+">"+self.marcadores[x]+"\n")
		
		marcadores.close()
		
		for x in self.notificaciones:
			x.close()
		
		gtk.main_quit()
		sys.exit()

	def saliendo(self,ventana, datos):

		dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO)
		dialog.set_title("Sesion...")
		dialog.set_markup("Esta saliendo de AguBrowser 2.0 \n ¿Desea Guardar la sesion?")
		#dialog.set_image(image)
		response = dialog.run()
		dialog.show_all()
		dialog.destroy()
		if response == gtk.RESPONSE_YES:
			self.Salir(True)

		else:
			self.Salir(False)

	def ventana_con_webview(self, web_view, web_frame):
		self.dir_ventana_emergente = None
		scroll = gtk.ScrolledWindow()
		navegador = webkit.WebView()
		scroll.add(navegador)

		ventana = gtk.Window()
		ventana.set_title("AguBrowser 2.0")
		ventana.add(scroll)

		ventana.show_all()
		ventana.resize(640, 400)

		navegador.connect("title-changed", self.webview_titulo, ventana)
		web_view.connect("download-requested", self.descargar_archivo, ventana)
		

		return navegador
		
		#print self.dir_ventana_emergente

	def webview_titulo(self, web_view, frame, titulo, ventana):
		self.dir_ventana_emergente = frame.get_uri()
		ventana.set_title(titulo+" - AguBrowser 2.0")
				

	def abrir_direccion(self, widget, url=None):
		if not url: dir = widget.get_text()

		if url: dir = url

		if "http://" in dir or "https://" in dir or "ftp://" in dir or "about:" in dir or "file:///" in dir or "view-source:" in dir or "http//" in dir:
			self.navegador.open(dir)

		else: 
			self.navegador.open("http://"+dir)
		if widget:
			widget.set_text("http://"+dir)

		pixbuf = gtk.gdk.pixbuf_new_from_file_at_size("Iconos/cargando.gif", 32, 32)
		self.direccion.set_property("primary-icon-pixbuf", pixbuf)
	
		#elsefile

	def set_titulo(self, view, frame, titulo):
		self.set_title(titulo+" - AguBrowser 2.0")
		self.label.set_text(titulo)
		self.direccion.set_text(frame.get_uri())
		self.titulo = titulo

		self.guardar_historial(titulo, frame.get_uri())
		self.dir_actual = frame.get_uri()

 
	def error(self, a, b,c, d):
		if self.parado:
			n = Notificacion("Error", "Ocurrio un error al intentar cargar la pagina", icono="Iconos/gtk-dialog-error.png")
			n.attach_to_widget(gtk.HScale())
			n.set_timeout(300)
			self.notificaciones.append(n)
			self.direccion.set_text("Ocurrio un error al cargar la pagina")


	def listo(self, a, b):
		self.direccion.set_property("primary-icon-stock", gtk.STOCK_APPLY)
		self.favicon_i.set_from_stock(gtk.STOCK_NEW, gtk.ICON_SIZE_BUTTON)
		#os.system("clear")
		print "Listo"
		self.listo_s.play()

	def cargando(self, a, b):
		pixbuf = gtk.gdk.pixbuf_new_from_file_at_size("Iconos/cargando.gif", 32, 32)
		self.direccion.set_property("primary-icon-pixbuf", pixbuf)
		self.favicon_i.set_from_file("Iconos/cargando.gif")

	def set_progreso(self, a, valor):
		cantidad = 0

		for x in str(valor):
			if cantidad == 0:
				cantidad = 1
				numero1 = x

			else:
				cantidad = 0
				numero2 = x

		if valor != 100:
			self.direccion.set_property("progress-fraction",float(str("0"+"."+numero1+numero2)))
			self.parado = False

		else:
			def timeout(direccion):
				direccion.set_property("progress-fraction",0.0)

				return False

			self.direccion.set_property("progress-fraction",1.0)	
			time_out = gobject.timeout_add(5000, timeout, self.direccion)
			self.parado = True

		

	def ATRAS(self, widget):
		self.navegador.go_back()

	def NEXT(self, widget):
		self.navegador.go_forward()
	
	def refrescar_cb(self, widget):
		self.navegador.reload()

	def parar(self, widget):
		self.navegador.stop_loading()
		self.parado = True

	def favicon(self, webview, icono):
		d = urllib.urlopen(icono)
		if os.path.exists(activity.get_activity_root()+"/data/Favicons/"+icono.split("/")[-1]): os.remove("Favicons/"+icono.split("/")[-1])
		fav = open(activity.get_activity_root()+"/data/Favicons/"+icono.split("/")[-1], "a")
		for x in d.readlines():
			fav.write(x)

		fav.close()

		self.favicon_i.set_from_file(activity.get_activity_root()+"/data/Favicons/"+icono.split("/")[-1])
	
	def guardar_historial(self, titulo, dir):
		historial = open(datos+"Historial", "a")
		historial.write(str(datetime.date.today())+">"+time.strftime("%H:%M:%S")+">"+titulo+">"+dir+"\n")
		historial.close()
		self.hist.actualizar()

	def Imprimir(self, boton):
    		mainframe = self.navegador.get_main_frame()
    		mainframe.print_full(gtk.PrintOperation(), gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG);

	def descargar_archivo(self, webview, descarga, ventana):
		a = FileSave(descarga)		

	def set_text_status(self, webview, texto):
		self.estado.display(texto)
		
	def update_marcadores(self):
		for y in self.botones.keys():
			self.marcadores_box.remove(self.botones[y])

		self.botones = {}

		for x in self.marcadores.keys():
			self.botones[x] = gtk.ToolButton()
			self.botones[x].set_label(x)
			self.marcadores_box.add(self.botones[x])
			self.botones[x].connect("clicked", self.abrir_direccion, self.marcadores[x])
			self.botones[x].show_all()

	def agregar_marcador(self, widget):
		self.marcadores[self.titulo] = self.dir_actual
		self.update_marcadores()

	def inspector(self, widget):
		inspector = Inspector(self.navegador.get_web_inspector())
		inspector._show_window_cb(self.navegador.get_web_inspector())
	
	def menu_webview(self, webview, menu):
		ins = gtk.MenuItem("Inspeccionar Elemento")
		ins.add_accelerator("activate", self.ag,
                            ord('E'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
		agregar = gtk.MenuItem("Agregar a marcadores")
		agregar.add_accelerator("activate", self.ag,
                            ord('A'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)

		agregar.connect("activate", self.agregar_marcador)
		ins.connect("activate", self.inspector)

		menu.append(agregar)
		menu.append(ins)
		menu.show_all()

	def Acerca_de(self, widget):
		acerca_de = gtk.AboutDialog() # http://www.pygtk.org/docs/pygtk/class-gtkaboutdialog.html
		acerca_de.set_name("AguBrowser")
		acerca_de.set_version("2.0")
		acerca_de.set_copyright("Agustin Zubiaga 2011")
		acerca_de.set_comments("AguBrowser es un navegador \n avanzado, rapido y muy facil \n de usar. Espero que les guste")
		acerca_de.set_license('''
Este programa es software libre, puede redistribuirlo y / o modificar
bajo los términos de la GNU General Public License publicada por
la Free Software Foundation, bien de la versión 2 de la Licencia, o
(a su elección) cualquier versión posterior.

Este programa se distribuye con la esperanza de que sea útil,
pero SIN NINGUNA GARANTÍA, incluso sin la garantía implícita de
COMERCIALIZACIÓN o IDONEIDAD PARA UN PROPÓSITO PARTICULAR. Consulte la
GNU General Public License para más detalles.''')

		acerca_de.set_website("http://www.wix.com/aguszs97/Agustin-Zubiaga")
		acerca_de.set_authors(["Pramacion y diseño: Agustín Zubiaga", "Beta Tester: Ignacio Rodriguez"])
		pixbuf3 = gtk.gdk.pixbuf_new_from_file_at_size("Iconos/presentacion.png", 225, 213)
		acerca_de.set_logo(pixbuf3)

		acerca_de.run()
		acerca_de.destroy()


	def ir_a_home(self, widget):
		self.abrir_direccion(None, url=self.dp)

	def configuracion_cb(self, widget):
		self.configuracion = Configuracion(self)

	def actualizar_sensibilidad_de_controles(self):
		if self.navegador.can_go_back(): self.siguiente.set_sensitive(False)
		else: self.atras.set_sensitive(True)
		if self.navegador.can_go_forward(): self.siguiente.set_sensitive(False)
		else: self.siguiente.set_sensitive(True)

	def update_configuracion(self):
	# **** Actualiza la configuracion

		# **** Actualizacion de buscador:
		self.buscador = open(datos+"Buscador", "r")

		for x in self.buscador.readlines():
			sp = x.split("!")
			nombre = sp[0]
			direccion = sp[1]
			sp1 = direccion.split("palabra_clave")			
		
		try:
			self.direccion_T = (sp1[0], sp1[1])
		
		except IndexError:

			self.direccion_T = (sp1[0])

		self.bg.set_text("Buscar en "+nombre)

		self.buscador.close()

		if nombre == "Google":
			pixbuf1 = gtk.gdk.pixbuf_new_from_file_at_size("Iconos/Google.ico", 16, 16)

		elif nombre == "Yahoo":
			self.bg.set_text("Buscar en Yahoo!")
			pixbuf1 = gtk.gdk.pixbuf_new_from_file_at_size("Iconos/yahoo.jpg", 16, 16)
			print self.direccion_T 

		elif nombre == "Bing":
			pixbuf1 = gtk.gdk.pixbuf_new_from_file_at_size("Iconos/bing-logo.jpg", 16, 16)

		elif nombre == "Wikipedia":
			pixbuf1 = gtk.gdk.pixbuf_new_from_file_at_size("Iconos/wikipedia-logo.jpg", 16, 16)

		elif nombre == "Creative Commons":
			pixbuf1 = gtk.gdk.pixbuf_new_from_file_at_size("Iconos/creative-commons.jpg", 16, 16)		

		elif nombre == "eBay":
			pixbuf1 = gtk.gdk.pixbuf_new_from_file_at_size("Iconos/ebay.jpg", 16, 16)

		elif not nombre == "Yahoo":
			self.bg.set_text("Buscar en " + nombre)

		self.bg.set_property("primary-icon-pixbuf", pixbuf1)

		# **** Actualizacion de boton home:
		comprobar = open(datos+"Boton_Home", "r")
		for x in comprobar.readlines():
			boton_CPE = x

		comprobar.close()

		if boton_CPE == "Si" and not self.el_boton_es_visible:
			self.hbox1.add(self.b_home)
			self.el_boton_es_visible = True
		else: 
			if self.el_boton_es_visible:
				self.hbox1.remove(self.b_home)	
				self.el_boton_es_visible = False

		# **** Actualizacion pagina de inicio:
		dir_p = open(datos+"Web_Home", "r")
		for x in dir_p.readlines():
			direccion_principal = x

		dir_p.close()

		self.dp = direccion_principal

	def guardar_pagina(self, widget):
		pagina = urllib.urlopen(self.dir_actual)
		archivo = open(datos+"Paginas_Guardadas/"+self.dir_actual.split("/")[-1], "w")
		archivo.write("")
		archivo.close()
		archivo = open(datos+"Paginas_Guardadas/"+self.dir_actual.split("/")[-1], "a")
	
		for x in pagina.readlines():
			archivo.write(x)

		archivo.close()
		pagina.close()		
		salir = gtk.Button(None, stock=gtk.STOCK_QUIT)
		salir.connect("clicked", self.saliendo, None)
		hbox1.add(salir)
		if os.path.exists(datos+"Paginas_Guardadas/"+self.dir_actual.split("/")[-1]):

			def abrir_carpeta(widget):
				args = "%s %s" % ("nautilus", datos+"/Paginas_Guardadas/")
				abrir = subprocess.Popen(args, shell=True, universal_newlines=True)

			dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO)
			dialog.set_title("Listo!!! - AguBrowser 2.0")
			dialog.set_markup("Se ha guardardo la pagina, exitosamente")

			mostrar = gtk.Button("Mostrar Carpeta de Paginas")
			mostrar.connect("clicked", abrir_carpeta)

			dialog.vbox.add(mostrar)
			dialog.vbox.show_all()

			dialog.run()
			dialog.destroy()
		

	def ver_codigo_fuente(self, menuitem):

		def obtener_otro_codigo(widget, buffer, window):
			dir = widget.get_text()	
			buffer.set_text("Obteniendo codigo fuente...")
			window.set_title("Codigo fuente de: "+dir)
			codigo = urllib.urlopen(dir)

			string = ""
			cant = 1
		
		
			for x in codigo.readlines():
				if cant == 1:
					string = x
					cant = 2
				else:
					string = str(string+x+"\n")
			
			if string != "":
				buffer.set_text(string)

			else:
				buffer.set_text("Ocurrio un error al cargar "+dir)		

		window = gtk.Window()
		window.set_title("Codigo fuente de: "+ self.dir_actual)
		window.show_all()
		
		vbox = gtk.VPaned()

		entry = gtk.Entry(max=0)
		entry.set_size_request(600,25)
		vbox.add1(entry)
		
		scroll = gtk.ScrolledWindow()
		
		view = gtk.TextView()
		buffer = view.get_buffer()
		buffer.set_text("Cargando codigo fuente...")
		entry.connect("activate", obtener_otro_codigo, buffer, window)
		view.show_all()
		scroll.add(view)
		scroll.show_all()

		view.set_editable(False)

		vbox.add2(scroll)
		vbox.show_all()
		window.add(vbox)
		window.resize(800, 600)

		codigo = urllib.urlopen(self.dir_actual)

		string = ""
		cant = 1
		
		
		for x in codigo.readlines():
			if cant == 1:
				string = x
				cant = 2
			else:
				string = str(string+x+"\n")
			

		buffer.set_text(string)

	def abrir(self, widget):
		Selector_de_Archivos(self)

	def abrir_archivo(self, archivo):
		self.navegador.open("file://"+archivo)

	def buscar_texto(self, widget):
		Buscar(self.navegador)

	
	def editar_cb(self, widget, tipo):
		if tipo == "Deshacer": self.navegador.undo()
		elif tipo == "Rehacer": self.navegador.redo()
		elif tipo == "Copiar": self.navegador.copy_clipboard() 
		elif tipo == "Cortar": self.navegador.cut_clipboard()
		elif tipo == "Todo": self.navegador.select_all()

	def propiedades_de_la_pagina(self, menu_item):
		web_view = self.navegador
    		mainframe = web_view.get_main_frame()
    		datasource = mainframe.get_data_source()
    		main_resource = datasource.get_main_resource()
    		window = gtk.Window()
    		window.set_default_size(100, 60)
    		vbox3 = gtk.VBox()
    		hbox4 = gtk.HBox()
    		hbox4.pack_start(gtk.Label("Tipo de Pagina :"), False, False)
    		hbox4.pack_end(gtk.Label(main_resource.get_mime_type()), False, False)
    		vbox3.pack_start(hbox4, False, False)
    		hbox2 = gtk.HBox()
    		hbox2.pack_start(gtk.Label("URL: "), False, False)
    		hbox2.pack_end(gtk.Label(main_resource.get_uri()), False, False)
    		vbox3.pack_start(hbox2, False, False)
    		hbox3 = gtk.HBox()
    		hbox3.pack_start(gtk.Label("Codificacion: "), False, False)
    		hbox3.pack_end(gtk.Label(main_resource.get_encoding()), False, False)
    		vbox3.pack_start(hbox3, False, False)
    		window.add(vbox3)
    		window.show_all()
   		window.present()
		window.set_title("Propiedades - AguBrowser 2.0")

	def __init__(self, handle):

		activity.Activity.__init__(self, handle, False)

		pygame.mixer.init()

		self.bases = Bases_de_Datos()
		self.listo_s = pygame.mixer.Sound("Iconos/listo.wav")

		self.set_title("AguBrowser 2.0")
		self.connect("delete-event", self.saliendo)
		self.set_icon_from_file("Iconos/logo.png")
		accel_group = gtk.AccelGroup() # http://www.pygtk.org/docs/pygtk/class-gtkaccelgroup.html
		self.ag = accel_group		
		
		self.add_accel_group(accel_group)
		self.set_opacity(0.98)
		self.parado = False

		# ********** Contenedor Principal

		self.main = gtk.VPaned()
		self.set_canvas(self.main)

		# ********** Navegador
		self.direccion = gtk.Entry()
		self.notebook = gtk.Notebook()
		self.label = gtk.Label()
		self.favicon_i = gtk.Image()
		self.favicon_i.set_from_file("Iconos/cargando.gif")
		box = gtk.HBox(spacing=5)
		box.add(self.favicon_i)
		box.add(self.label)
		box.show_all()

		self.navegador = webkit.WebView()
		self.navegador.set_size_request(700, 500)

		dir_p = open(datos+"Web_Home", "r")
		for x in dir_p.readlines():
			direccion_principal = x

		dir_p.close()
		self.dp = direccion_principal


		if direccion_principal == "" or direccion_principal == None: direccion_principal = "file:///"+os.getcwd()+"/Home.html"
		self.abrir_direccion(None, url=direccion_principal)
		self.navegador.open(self.dp)
		self.notificaciones = []

		self.navegador.connect("title-changed", self.set_titulo)
		self.navegador.connect("load-finished", self.listo)
		self.navegador.connect("load-started", self.cargando)
		self.navegador.connect("load-progress-changed", self.set_progreso)
		self.navegador.connect("load-error", self.error)
		self.navegador.connect("download-requested", self.descargar_archivo, gtk.Window())
		self.navegador.connect("create-web-view", self.ventana_con_webview)
		self.navegador.connect("populate-popup", self.menu_webview)
		self.navegador.connect("status-bar-text-changed", self.set_text_status)
		self.navegador.connect("icon-loaded", self.favicon)
		self.navegador.set_property("transparent", True)
		
		self.scroll = gtk.ScrolledWindow()
		self.scroll.add(self.navegador)
		self.notebook.append_page(self.scroll, box)
		self.titulo = None

		barra_menus = gtk.MenuBar()
		#barra_menus.set_size_request(750, 20)
		hbox3 = gtk.HBox()
		hbox3.add(barra_menus)


		# VBOX:
		vbox = gtk.VBox()
		vbox.add(self.notebook)

		# VBOX:
		vbox1 = gtk.VBox(spacing=4)
		vbox1.add(hbox3)
		
		# Barra Marcadores
		self.marcadores = {}
		self.marcadores_box = gtk.HBox()
		self.botones = {}

		mark = open(datos+"Marcadores", "r")
		for x in mark.readlines():
			sp = x.split(">")
			print sp
			#self.marcadores[sp[0]] = sp[0]
		mark.close()
			
		self.update_marcadores()	

		# ********* Barra de Herramientas

		self.hbox = gtk.HBox()
		vbox1.add(self.hbox)
		self.main.add1(vbox1)
		self.main.add2(vbox)
			

		# *********** Widgets en barra

		self.atras = gtk.ToolButton()
		imagen = gtk.Image()
		imagen.set_from_stock(gtk.STOCK_GO_BACK, 48)
		self.atras.set_icon_widget(imagen)
		self.atras.connect("clicked", self.ATRAS)
		self.atras.add_accelerator("clicked", self.ag,
                            ord('P'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
		
		self.siguiente = gtk.ToolButton()
		sig = gtk.Image()
		sig.set_from_stock(gtk.STOCK_GO_FORWARD, 48)
		self.siguiente.set_icon_widget(sig)
		self.siguiente.connect("clicked", self.NEXT)
		self.siguiente.add_accelerator("clicked", self.ag,
                            ord('S'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)

		self.refrescar = gtk.ToolButton()
		ref = gtk.Image()
		ref.set_from_stock(gtk.STOCK_REFRESH, 48)
		self.refrescar.set_icon_widget(ref)
		self.refrescar.connect("clicked", self.refrescar_cb)
		self.refrescar.add_accelerator("clicked", self.ag,
                            ord('H'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)

		self.direccion = gtk.Entry()
		self.direccion.prepend_text("Escribe aqui la direccion")
		self.direccion.connect("activate", self.abrir_direccion)
		self.direccion.set_size_request(750, 40)
		self.direccion.set_property("primary-icon-stock", gtk.STOCK_APPLY)
		
		def match_cb(self, model, iter, browser):
			browser.abrir_direccion(None, url=model[iter][0].split("\n")[0])
        		return
	
		completion = gtk.EntryCompletion()
		
		#completa.set_text_column(0)
		completion.set_minimum_key_length(3)
	
		self.agregados = {}

		self.liststore = gtk.ListStore(str)
		historial = open(datos+"Historial", "r")
		for s in historial.readlines():
			sp = s.split(">")
			
			try: self.agregados[sp[3]]
			except KeyError:
            			self.liststore.append([sp[3]])
				self.agregados[sp[3]] = "Si"			

		historial.close()
		
		completion.set_model(self.liststore)
		self.direccion.set_completion(completion)
		completion.set_text_column(0)
		completion.connect('match-selected', match_cb, self)

		#self.liststore.show()


		self.stop = gtk.ToolButton()
		stop = gtk.image_new_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_BUTTON)
		self.stop.set_icon_widget(stop)
		self.stop.connect("clicked", self.parar)
		self.stop.add_accelerator("clicked", self.ag,
                            ord('D'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)

		self.image = gtk.Image()
		self.image.set_from_stock(gtk.STOCK_APPLY, gtk.ICON_SIZE_BUTTON)

		self.ajuste = gtk.Adjustment(value=0, lower=0, upper=100, step_incr=1, page_incr=1)
		self.progreso = gtk.ProgressBar(self.ajuste)
		
		self.estado = StatusBar()
		self.estado.add(self.progreso)
		#vbox.add(self.estado)

		self.estado.hide()
		
		self.hbox.add(self.atras)
		self.hbox.add(self.siguiente)
		self.hbox.add(self.refrescar)
		#self.hbox.add(self.image)
		self.hbox.add(self.direccion)
		self.hbox.add(self.stop)

		tooltip = gtk.Tooltips()
		tooltip.set_tip(self.stop, "Detener la carga de esta pagina \nStop the load of this page", tip_private=None)
		

		def limpiar(widget, event):
			widget.set_text("")

		def buscar(widget, navegador):
			
			try: navegador.abrir_direccion(None, url=navegador.direccion_T[0]+widget.get_text()+navegador.direccion_T[1])

			except IndexError: navegador.abrir_direccion(None, url=navegador.direccion_T[0]+widget.get_text())

		hbox1 = gtk.HBox()

		self.buscador = open(datos+"Buscador", "r")

		for x in self.buscador.readlines():
			sp = x.split("!")
			nombre = sp[0]
			direccion = sp[1]
			sp1 = direccion.split("palabra_clave")			
		
		try:
			self.direccion_T = (sp1[0], sp1[1])
		
		except IndexError:

			self.direccion_T = (sp1[0])

		self.buscador.close()

		buscar_google = gtk.Entry(max=0)
		buscar_google.set_text("Buscar en " + nombre)

		if nombre == "Google":
			pixbuf1 = gtk.gdk.pixbuf_new_from_file_at_size("Iconos/Google.ico", 16, 16)

		elif nombre == "Yahoo":
			buscar_google.set_text("Buscar en Yahoo!")
			pixbuf1 = gtk.gdk.pixbuf_new_from_file_at_size("Iconos/yahoo.jpg", 32, 32)
			print self.direccion_T 

		elif nombre == "Bing":
			pixbuf1 = gtk.gdk.pixbuf_new_from_file_at_size("Iconos/bing-logo.jpg", 32, 32)

		elif nombre == "Wikipedia":
			pixbuf1 = gtk.gdk.pixbuf_new_from_file_at_size("Iconos/wikipedia-logo.jpg", 32, 32)

		elif nombre == "Creative Commons":
			pixbuf1 = gtk.gdk.pixbuf_new_from_file_at_size("Iconos/creative-commons.jpg", 32, 32)		

		elif nombre == "eBay":
			pixbuf1 = gtk.gdk.pixbuf_new_from_file_at_size("Iconos/ebay.jpg", 32, 32)

		
		buscar_google.set_property("primary-icon-pixbuf", pixbuf1)
		buscar_google.connect("button-press-event", limpiar)
		buscar_google.connect("activate", buscar, self)
		hbox1.add(buscar_google)	

		self.bg = buscar_google
		
		comprobar = open(datos+"Boton_Home", "r")
		for x in comprobar.readlines():
			boton_CPE = x

		comprobar.close()


		
		home = gtk.ToolButton()
		imagen1 = gtk.image_new_from_stock(gtk.STOCK_HOME, gtk.ICON_SIZE_BUTTON)
		home.set_icon_widget(imagen1)
		home.connect("clicked", self.ir_a_home)
		home.add_accelerator("clicked", self.ag,
                            ord('H'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)

		self.b_home = home
		self.hbox1 = hbox1

		if boton_CPE == "Si": 
			self.hbox1.add(self.b_home)
			self.el_boton_es_visible = True
	
		else: self.el_boton_es_visisblie = False

		configuracion = gtk.ToolButton()
		config = gtk.image_new_from_stock(gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_BUTTON)
		configuracion.set_icon_widget(config)
		
		configuracion.connect("clicked", self.configuracion_cb)
		hbox1.add(configuracion)	

		salir = gtk.ToolButton()
		salir.set_icon_widget(gtk.image_new_from_stock(gtk.STOCK_QUIT, gtk.ICON_SIZE_BUTTON))
		salir.connect("clicked", self.saliendo, None)
		tooltip = gtk.Tooltips()
		tooltip.set_tip(salir, "Salir de AguBrowser 2.0 \nExit of AguBrowser 2.0", tip_private=None)
		
	
		def fullscreen_cb(widget, esto):
			Armar_Pantalla_Completa(esto)		

		b_fullscreen = gtk.ToolButton()
		b_fullscreen.set_icon_widget(gtk.image_new_from_stock(gtk.STOCK_FULLSCREEN, gtk.ICON_SIZE_BUTTON))
		b_fullscreen.connect("clicked", fullscreen_cb, self)
		hbox1.add(b_fullscreen)
		self.hbox.add(salir)
	

		vbox1.add(hbox1)
		vbox1.add(self.marcadores_box)

		# Historial
		vbox3 = gtk.VBox()
		scroll = gtk.ScrolledWindow()
		hist = Historial(self)
		scroll.add(hist)
		scroll.set_size_request(700, 500)
		vbox3.add(scroll)
		self.hist = hist
	
		limpiar = gtk.Button("Limpiar Historial")

		def limpiar_hist(widget, abrowse):

			os.remove(datos+"Historial")
			a  = open(datos+"Historial", "w")
			a.write("")
			a.close()
			
			self.hist.actualizar()		
					
		limpiar.connect("clicked", limpiar_hist, self)
	
		vbox3.add(limpiar)

		HBOX2 = gtk.HBox(spacing=5)
		HBOX2.add(gtk.image_new_from_file("Iconos/historial.png"))
		HBOX2.add(gtk.Label("Historial"))
		HBOX2.show_all()
		self.notebook.append_page(vbox3, HBOX2)

		# ******** Menus:
		archivo = gtk.MenuItem("Archivo")
		barra_menus.append(archivo)

		archivom = gtk.Menu()
		archivo.set_submenu(archivom)

		abrir = gtk.MenuItem("Abrir archivo")
		abrir.add_accelerator("activate", accel_group,
                            ord('A'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
		
		abrir.connect("activate", self.abrir)

		archivom.append(abrir)


		guardar = gtk.MenuItem("Guardar la pagina Actual")
		guardar.add_accelerator("activate", accel_group,
                            ord('G'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)

		guardar.connect("activate", self.guardar_pagina)

		archivom.append(guardar)

		imprimir = gtk.MenuItem("Imprimir")
		imprimir.add_accelerator("activate", accel_group,
                            ord('I'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
      
		imprimir.connect("activate", self.Imprimir)
		archivom.append(imprimir)


		se = gtk.MenuItem("Buscar Texto")
		se.add_accelerator("activate", accel_group,
                            ord('B'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)

		se.connect("activate", self.buscar_texto)

		archivom.append(se)


		# Menu Editar

		editar = gtk.MenuItem("Editar")
		editarm = gtk.Menu()
	
		editar.set_submenu(editarm)
	
		
		deshacer = gtk.MenuItem("Deshacer")
		rehacer = gtk.MenuItem("Rehacer")
		cortar = gtk.MenuItem("Cortar")
		copiar = gtk.MenuItem("Copiar")
		pegar = gtk.MenuItem("Pegar")
		todo = gtk.MenuItem("Seleccionar todo")
		prefs = gtk.MenuItem("Preferencias")

		deshacer.connect("activate", self.editar_cb, "Deshacer")
		rehacer.connect("activate", self.editar_cb, "Rehacer")
		cortar.connect("activate", self.editar_cb, "Cortar")
		copiar.connect("activate", self.editar_cb, "Copiar")
		pegar.connect("activate", self.editar_cb, "Pegar")
		todo.connect("activate", self.editar_cb, "Todo")
		prefs.connect("activate", self.configuracion_cb)

		editarm.append(deshacer)
		editarm.append(rehacer)
		#editarm.add_separator()
		editarm.append(cortar)
		editarm.append(copiar)
		editarm.append(pegar)
		#editarm.add_separator()
		editarm.append(todo)
		#editarm.add_separator()
		barra_menus.append(editar)

		# Menu Ver:
		def mostrar_ocultar_barras(widget, clase, barra):
			if clase.mostradas2 and barra == 2:
				clase.hbox1.hide_all()
				clase.mostradas2 = False
	
			elif clase.mostradas2 == False and barra == 2:
				clase.hbox1.show_all()
				clase.mostradas2 = True 

			elif clase.mostradas1 and barra == 1:
				clase.hbox.hide_all()
				clase.mostradas1 = False

			elif clase.mostradas1 == False and barra == 1:
				clase.hbox.show_all()
				clase.mostradas1 = True 

		ver = gtk.MenuItem("Ver")
		verm = gtk.Menu()

		ver.set_submenu(verm)

		barra_menus.append(ver)

		self.mostradas1 = True
		self.mostradas2 = True

		barra1 = gtk.CheckMenuItem("Barra de Navegacion")
		barra2 = gtk.CheckMenuItem("Barra de Busqueda y Herramientas")
		

		cg = gtk.MenuItem("Codigo Fuente")
		cg.add_accelerator("activate", accel_group,
                            ord('U'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)

		cg.connect("activate", self.ver_codigo_fuente)

		pr = gtk.MenuItem("Propiedades de la Pagina")
		pr.connect("activate", self.propiedades_de_la_pagina)

		barra1.set_active(True)
		barra2.set_active(True)

		barra1.connect("activate", mostrar_ocultar_barras, self, 1)
		barra2.connect("activate", mostrar_ocultar_barras, self, 2)
		
		verm.append(barra1)
		verm.append(barra2)
		verm.append(cg)
		verm.append(pr)

		# Menu Ir
		ir = gtk.MenuItem("Ir a:")
		irb = gtk.Menu()

		ir.set_submenu(irb)

		menui = gtk.ImageMenuItem()
		menui.set_property("label", "Atras")
		menui.set_image(gtk.image_new_from_stock(gtk.STOCK_GO_BACK, gtk.ICON_SIZE_MENU))
		menui.set_property("use-stock", True)		
		menui.set_property("always-show-image", True)	
		menui.connect("activate",self.ATRAS)

		irb.append(menui)

		menui = gtk.ImageMenuItem()
		menui.set_property("label", "Siguiente")
		menui.set_image(gtk.image_new_from_stock(gtk.STOCK_GO_FORWARD, gtk.ICON_SIZE_MENU))
		menui.set_property("use-stock", True)		
		menui.set_property("always-show-image", True)	
		menui.connect("activate",self.NEXT)

		irb.append(menui)
		
		menui = gtk.ImageMenuItem()
		menui.set_property("label", "Pagina Principal")
		menui.set_image(gtk.image_new_from_stock(gtk.STOCK_HOME, gtk.ICON_SIZE_MENU))
		menui.set_property("use-stock", True)		
		menui.set_property("always-show-image", True)	
		menui.connect("activate",self.ir_a_home)

		irb.append(menui)

		barra_menus.append(ir)
		
		ayuda = gtk.MenuItem("Ayuda")
		menudeayuda = gtk.Menu()
		ayuda.set_submenu(menudeayuda)
		
		acerca = gtk.MenuItem("Acerca de...")
		acerca.connect("activate", self.Acerca_de)
		menudeayuda.append(acerca)
		barra_menus.append(ayuda)		
	
		argumentos = 0

		# ******** Sesion
		sesion = open(datos+"Sesion", "r")
		if sesion.read() and argumentos == 0:
			dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO)
			dialog.set_title("Sesion...")
			dialog.set_markup("Hay una sesion guardada \n ¿Desea abrirla?")
			#dialog.set_image(image)
			response = dialog.run()
			dialog.show_all()
			dialog.destroy()
			if response == gtk.RESPONSE_NO: print "NO"

			else:
				self.navegador.open(sesion.read())
				print sesion.read()
			

		sesion.close()

		hbbox1 = gtk.HButtonBox()
		hbbox1.set_layout(gtk.BUTTONBOX_END)
		hbbox1.add(Reloj())

		hbox1.add(hbbox1)

		# Protector.Iniciar_Espera(self) Por ahora no funciona 
		self.set_flags(gtk.CAN_FOCUS)
		self.show_all()
		
		self.update_marcadores()
		

class Historial(gtk.TreeView):

	def callback_activated (self, treeview, path, view_column):
		iter = treeview.modelo.get_iter(path)
		url = treeview.modelo.get_value(iter, 1)
		self.navegador.abrir_direccion(None, url=url)

	def actualizar(self):
		historial = open(datos+"Historial", "r")
		self.modelo.clear()
		for x in historial.readlines():
			separados = x.split(">")
			self.modelo.append([separados[2], separados[3], separados[0], separados[1]])	

	def __init__(self, navegador):

		self.modelo = gtk.ListStore(str, str, str, str)

		gtk.TreeView.__init__(self, self.modelo)

		self.navegador = navegador

		titulo = gtk.TreeViewColumn("Titulo")
		direccion = gtk.TreeViewColumn("Direccion")
		fecha = gtk.TreeViewColumn("Fecha")
		hora = gtk.TreeViewColumn("Hora")
		
		titulocel = gtk.CellRendererText()
		dircel = gtk.CellRendererText()
		datecel = gtk.CellRendererText()
		horacel = gtk.CellRendererText()

		titulo.pack_start(titulocel)
		direccion.pack_start(dircel)
		fecha.pack_start(datecel)
		hora.pack_start(horacel)

		self.append_column(titulo)
		self.append_column(direccion)
		self.append_column(fecha)
		self.append_column(hora)


		titulo.set_attributes(titulocel, text=0)
		direccion.set_attributes(dircel, text=1)
		fecha.set_attributes(datecel, text=2)
		hora.set_attributes(horacel, text=3)

		historial = open(datos+"Historial", "r")
		self.modelo.clear()
		for x in historial.readlines():
			separados = x.split(">")
			self.modelo.append([separados[2], separados[3], separados[0], separados[1]])	

		self.connect("row-activated", self.callback_activated)
		self.show_all()	

class StatusBar(gtk.Statusbar):

	def __init__(self):
		gtk.Statusbar.__init__(self)
		self.iconbox = gtk.EventBox()
		self.iconbox.add(gtk.image_new_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_BUTTON))
		self.pack_start(self.iconbox, False, False, 6)
		self.iconbox.hide_all()

	def display(self, text, context=None):
		cid = self.get_context_id("pywebkitgtk")
		self.push(cid, str(text))

	def show_javascript_info(self): self.iconbox.show()

	def hide_javascript_info(self): self.iconbox.hide()


class Selector_de_Archivos(gtk.FileChooserDialog):

	def ok(self, widget):
		self.abrowse.abrir_archivo(self.get_filename())
		self.salir(None, None)

	def salir(self, widget, event):
		self.destroy()
	
	def __init__(self, abrowse_class):
		
		gtk.FileChooserDialog.__init__(self, title="Abrir archivo - AguBrowse 2.0", action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=None, backend="Coso")

		self.connect("delete-event", self.salir)
		self.set_current_folder(datos+"/Paginas_Guardadas")
		self.add_shortcut_folder(datos+"/Paginas_Guardadas")

		# filtros:
		html = gtk.FileFilter()
		html.set_name("Archivos HTML")
		html.add_pattern("*.html")
		html.add_pattern("*.HTML")
		self.add_filter(html)

		xml = gtk.FileFilter()
		xml.set_name("Archivos XML")
		xml.add_pattern("*.xml")
		xml.add_pattern("*.XML")
		self.add_filter(xml)		
		
		imagenes = gtk.FileFilter()
		imagenes.set_name("Archivos de Imagenes")
		imagenes.add_mime_type("image/*")
		self.add_filter(imagenes)

		musica = gtk.FileFilter()
		musica.set_name("Archivos de Música")
		musica.add_mime_type("audio/*")
		self.add_filter(musica)

		video = gtk.FileFilter()
		video.set_name("Archivos de Video")
		video.add_mime_type("video/*")
		self.add_filter(video)

		todos = gtk.FileFilter()
		todos.set_name("Todos los Archivos")
		todos.add_pattern("*")
		self.add_filter(todos)

		# Se puede seleccionar mas de un archivo??:
		self.set_select_multiple(False) # False o True indican si se puede o no

		# ****** #
		
		boton = gtk.Button("Abrir el archivo seleccionado")
		boton.set_flags(gtk.CAN_FOCUS)

		boton.connect("clicked", self.ok)

		hbbox = gtk.HButtonBox()
		hbbox.set_layout(gtk.BUTTONBOX_END)

		hbbox.add(boton)
		hbbox.show_all()

		self.abrowse = abrowse_class

		self.set_extra_widget(hbbox)

		self.show_all()

class Buscar(gtk.Window):

	def buscar(self, widget): self.navegador.search_text(widget.get_text(), True)
	def salir(self, widget): self.destroy()

	def __init__(self, navegador):

		gtk.Window.__init__(self)

		self.set_title("Buscar - AB")
		self.set_position(gtk.WIN_POS_CENTER)

		self.navegador = navegador
		entry = gtk.Entry(max=120)
		entry.connect("activate", self.buscar)
		entry.set_editable(True)


		cerrar = gtk.ToolButton()
		cerrar_i = gtk.image_new_from_stock(gtk.STOCK_QUIT, gtk.ICON_SIZE_BUTTON)
		cerrar.set_icon_widget(cerrar_i)
		cerrar.connect("clicked", self.salir)

		main = gtk.HBox()
		main.add(entry)
		main.add(cerrar)

		self.resize(300, 25) 
		entry.set_flags(gtk.CAN_FOCUS)

		self.add(main)
		self.show_all()
