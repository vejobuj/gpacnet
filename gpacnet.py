#!/usr/bin/env python2

import gtk
import json
import urllib
import commands
import posix
import shlex, subprocess

try:
	from kiwi.ui.views import BaseView, SlaveView
	from kiwi.ui.gadgets import quit_if_last
	from kiwi.ui.objectlist import ObjectList, Column
except:
	print("Please get kiwi package:")
	print("pacman -S kiwi")


TERMINAL = 'terminal'

def is_root():
	uid = posix.getuid()
	return uid == 0
	
root = is_root()
	
class Local():
	def __init__(self):
		command = ["pacman","-Q"]
		out, errors = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
		if errors:
			raise errors
		self.list = out.split('\n')[:-1]
		self.names = []
		self.versions = []
		for row in self.list:
			item = row.split(' ')
			self.names.append(item[0])
			self.versions.append(item[1])
		
	def check(self, package):
		try:
			index_number = self.names.index("%s" % package)
			return self.versions[index_number]
		except:
			return ""
			

class CategoryItem():
	def __init__(self, name):
		self.name = name


class Category(SlaveView):
	
	columns = [
		Column("name", sorted=True)
	]
	
	def __init__(self):
		listt = ObjectList(self.columns)
		listt.connect('selection-changed', self.selected)
		
		# selecting categories
		f = urllib.urlopen("http://pacnet.archlinux.pl/api/categories/").read()
		categories=json.loads(f)
		for category in categories:
			row = CategoryItem(category['fields']['name'])
			listt.append(row)

		SlaveView.__init__(self, listt)
		
	def selected(self, the_list, item):
		package.new_list(item.name)


class PackageItem():
	def __init__(self, name, version, installed, description):
		self.name, self.version, self.installed, self.description = name, version, installed, description


class Package(SlaveView):
	
	columns = [
		Column("name", sorted=True),
		Column("version"),
		Column("installed"),
		Column("description")
	]
	
	def __init__(self):
		self.list = ObjectList(self.columns)
		self.list.connect('selection-changed', self.info)
		
		self.to_install = ""
			
		# selecting categories
		f = urllib.urlopen("http://pacnet.karbownicki.com/api/category/app-accessibility/").read()
		packages=json.loads(f)
		for category in packages:
			got = local.check(category['name'])
			row = PackageItem(category['name'], category['version'], got, category['description'])
			self.list.append(row)

		SlaveView.__init__(self, self.list)


	def info(self, the_list, item):
		command = ["pacman", "-Si", item.name]
		pkg_info, errors = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
		shell.get_widget("info").get_buffer().set_text(pkg_info)
		self.to_install = item.name
		
	def new_list(self, category):
		self.list.clear()
		f = urllib.urlopen("http://pacnet.karbownicki.com/api/category/%s/" % category).read()
		packages=json.loads(f)
		for category in packages:
			got = local.check(category['name'])
			row = PackageItem(category['name'], category['version'], got, category['description'])
			self.list.append(row)
			
class Install():
	
	def __init__(self):
		self.button = shell.get_widget("install")
		self.button.add_events(gtk.gdk.BUTTON_PRESS_MASK)
		self.button.connect('button_press_event', self.clicked)
		
	def clicked(self, widget, event):
		if package.to_install:
			if root:
				pacman = "pacman -S %s && read" % package.to_install
				command = [TERMINAL, "-e", pacman]
			else:
				pacman = "su --command='pacman -S %s && read'" % package.to_install
				command = [TERMINAL, "-e", pacman]
			out, errors = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
			if errors:
				raise errors
		else:
			print("No package to install")
		

shell = BaseView(gladefile="gpacnet", delete_handler=quit_if_last)

local = Local()
category = Category()
package = Package()
install = Install()


shell.attach_slave("category", category)
shell.attach_slave("package", package)



category.show_all()
category.focus_topmost()
package.show_all()
package.focus_topmost()
shell.show()
gtk.main()
