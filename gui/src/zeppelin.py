#!/usr/bin/env python

import pygame

import serial
import sys

import wx
import wxversion
import wx.html

def bool_array_to_byte_array(bools):
	array=[]

	temp=0

	for ii in range(0,len(bools)):
		if bools[ii]:
			temp+=1<<int(ii%8)

		if ii%8>=7 or ii==len(bools)-1:
			array.append(chr(temp))
			temp=0

	return array

def serial_list():
	valid_ports=[]

	try:
		import serial
		import serial.tools.list_ports

		for port in serial.tools.list_ports.comports():
			if port[2]!='n/a':
				valid_ports.append(port[0])
	except:
		None

	return valid_ports

def joystick_list():
	valid_joysticks=[]

	try:
		pygame.quit()
		pygame.init()
		pygame.joystick.init()

		for ii in range(0,pygame.joystick.get_count()):
			valid_joysticks.append(pygame.joystick.Joystick(ii).get_name())
	except:
		None

	pygame.quit()
	return valid_joysticks

class window_t(wx.html.HtmlWindow):
	def __init__(self,parent,id,size=(600,400)):
		wx.html.HtmlWindow.__init__(self,parent,id,size=size)
		if "gtk2" in wx.PlatformInfo:
			self.SetStandardFonts()

	def OnLinkClicked(self,link):
		wx.LaunchDefaultBrowser(link.GetHref())

class aboutbox_t(wx.Dialog):
	def __init__(self,title,text):
		wx.Dialog.__init__(self,None,-1,"About "+title,style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
		hwin=window_t(self,-1,size=(400,200))

		version_text=""
		version_text+="<p>"
		version_text+="<p>Python Version "+sys.version.split()[0]
		version_text+="<br>"
		version_text+="wxWidgets Version "+wx.VERSION_STRING
		version_text+="<br>"
		version_text+="pySerial Version "+sys.version.split()[0]
		version_text+="<br>"
		version_text+="pyGame SDL Version "
		version_text+=str(pygame.get_sdl_version()[0])
		version_text+="."
		version_text+=str(pygame.get_sdl_version()[1])
		version_text+="."
		version_text+=str(pygame.get_sdl_version()[2])
		version_text+="</p>"

		hwin.SetPage(text+version_text)
		btn=hwin.FindWindowById(wx.ID_OK)
		internal_representation=hwin.GetInternalRepresentation()

		width=hwin.GetInternalRepresentation().GetWidth()+25
		height=hwin.GetInternalRepresentation().GetHeight()+10
		hwin.SetSize((width,height))

		self.SetClientSize(hwin.GetSize())
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

class frame_t(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self,None,title="Zepplin",pos=(150,150),size=(480,300))
		self.Bind(wx.EVT_CLOSE,self.OnClose)

		menubar_m=wx.MenuBar()
		self.SetMenuBar(menubar_m)

		filemenu_m=wx.Menu()

		quit_m=filemenu_m.Append(wx.ID_EXIT,"Q&uit","Close window and exit program.")
		self.Bind(wx.EVT_MENU,self.OnClose,quit_m)
		menubar_m.Append(filemenu_m,"&File")

		helpmenu_m=wx.Menu()

		about_m=helpmenu_m.Append(wx.ID_ABOUT,"&About","Information about this program")
		self.Bind(wx.EVT_MENU,self.OnAbout,about_m)
		menubar_m.Append(helpmenu_m,"&Help")

		self.statusbar=self.CreateStatusBar()
		self.statusbar.SetStatusText("Started.")

		self.panel=wx.Panel(self)

		self.box_sizer=wx.BoxSizer(wx.VERTICAL)
		self.panel.SetSizer(self.box_sizer)

		self.serial_obj=None

		self.serial_text=wx.StaticText(self.panel,-1,"Serial Port")
		self.box_sizer.Add(self.serial_text,0,wx.ALL,4)

		self.serial_dropdown=wx.ComboBox(self.panel,-1,style=wx.CB_READONLY)
		self.Bind(wx.EVT_COMBOBOX,self.update_combos,self.serial_dropdown)
		self.box_sizer.Add(self.serial_dropdown,0,wx.ALL,4)

		self.joystick_obj=None

		self.joystick_text=wx.StaticText(self.panel,-1,"Joystick")
		self.box_sizer.Add(self.joystick_text,0,wx.ALL,4)

		self.joystick_dropdown=wx.ComboBox(self.panel,-1,style=wx.CB_READONLY)
		self.Bind(wx.EVT_COMBOBOX,self.update_combos,self.joystick_dropdown)
		self.box_sizer.Add(self.joystick_dropdown,0,wx.ALL,4)

		self.button_sizer=wx.BoxSizer(wx.HORIZONTAL)
		self.box_sizer.Add(self.button_sizer,0,wx.ALL,4)

		self.refresh_button=wx.Button(self.panel,wx.ID_REFRESH)
		self.Bind(wx.EVT_BUTTON,self.OnRefresh,self.refresh_button)
		self.button_sizer.Add(self.refresh_button,0,wx.ALL,4)

		self.connected=False
		self.connect_button=wx.Button(self.panel,label="Connect")
		self.Bind(wx.EVT_BUTTON,self.on_connect,self.connect_button)
		self.button_sizer.Add(self.connect_button,0,wx.ALL,4)

		self.OnRefresh(None)
		self.update_combos(None)

		self.timer_interval_ms=50
		self.timer=wx.Timer(self)
		self.Bind(wx.EVT_TIMER,self.update,self.timer)

		self.panel.Layout()

	def OnClose(self,event):
		self.disconnect()
		self.Destroy()

	def OnAbout(self,event):
		summary="<p>Zepplin is blimp control software designed for ASRA 2015.</p>"
		license="<p>Public Domain</p>"
		author="<p>Created by Mike Moss (mrmoss@alaska.edu).</p>"
		dialog=aboutbox_t("Zepplin",summary+license+author)
		dialog.ShowModal()
		dialog.Destroy()

	def OnRefresh(self,event):
		self.refresh_button.Enable(False)
		self.serial_refresh()
		self.joystick_refresh()
		self.refresh_button.Enable(True)
		self.update_combos(None)

	def update_combos(self,event):
		if self.serial_dropdown.GetCurrentSelection()>0 and self.joystick_dropdown.GetCurrentSelection()>0:
			self.connect_button.Enable(True)
		else:
			self.connect_button.Enable(False)

	def on_connect(self,event):
		self.connected=not self.connected

		if self.connected:
			self.connect()
			self.statusbar.SetStatusText("Connected to blimp.")
		else:
			self.disconnect()
			self.statusbar.SetStatusText("Disconnected from blimp.")

	def disconnect(self):
		self.connected=False
		self.serial_dropdown.Enable(True)
		self.joystick_dropdown.Enable(True)
		self.refresh_button.Enable(True)
		self.connect_button.SetLabel("Connect")
		self.serial_disconnect()
		self.joystick_disconnect()
		self.timer.Stop()
		self.OnRefresh(None)

	def connect(self):
		self.connected=True
		self.serial_dropdown.Enable(False)
		self.joystick_dropdown.Enable(False)
		self.refresh_button.Enable(False)
		self.connect_button.SetLabel("Disconnect")
		self.serial_connect()
		self.joystick_connect()
		self.timer.Start(self.timer_interval_ms)

	def serial_disconnect(self):
		if not self.serial_obj==None:
			self.serial_obj.close()
			self.serial_obj=None

	def serial_connect(self):
		if self.serial_dropdown.GetCurrentSelection()>0:
			serial_name=self.serial_dropdown.GetValue()
			self.serial_obj=serial.Serial(serial_name,57600)

	def serial_refresh(self):
		old_value=self.serial_dropdown.GetValue()
		selected_index=0

		self.serial_dropdown.Enable(False)
		self.serial_dropdown.SetValue("");
		self.serial_dropdown.Clear()
		self.serial_dropdown.Append("Select Serial Port")
		self.serial_dropdown.SetSelection(0)
		serials=serial_list()

		for ii in range(0,len(serials)):
			self.serial_dropdown.Append(serials[ii])

			if serials[ii]==old_value:
				selected_index=ii+1

		if selected_index>0:
			self.serial_dropdown.SetSelection(selected_index)
		elif len(serials)>0:
			self.serial_dropdown.SetSelection(1)

		if len(serials)>0:
			self.serial_dropdown.Enable(True)

	def joystick_disconnect(self):
		pygame.quit()
		self.joystick_obj=None

	def joystick_connect(self):
		if self.joystick_dropdown.GetCurrentSelection()>0:
			pygame.quit()
			pygame.init()
			pygame.joystick.init()
			self.joystick_obj=pygame.joystick.Joystick(self.joystick_dropdown.GetCurrentSelection()-1)
			self.joystick_obj.init()

	def joystick_refresh(self):
		old_value=self.joystick_dropdown.GetValue()
		selected_index=0

		self.joystick_dropdown.Enable(False)
		self.joystick_dropdown.SetValue("");
		self.joystick_dropdown.Clear()
		self.joystick_dropdown.Append("Select Joystick")
		self.joystick_dropdown.SetSelection(0)
		joysticks=joystick_list()

		for ii in range(0,len(joysticks)):
			self.joystick_dropdown.Append(joysticks[ii])

			if joysticks[ii]==old_value:
				selected_index=ii+1

		if selected_index>0:
			self.joystick_dropdown.SetSelection(selected_index)
		elif len(joysticks)>0:
			self.joystick_dropdown.SetSelection(1)

		if len(joysticks)>0:
			self.joystick_dropdown.Enable(True)

	def update(self,event):
		if self.serial_obj.isOpen():
			try:
				pygame.event.get()

				self.serial_obj.write(chr(0xfa))
				self.serial_obj.write(chr(0xaf))

				num_axes=min(256,self.joystick_obj.get_numaxes())
				self.serial_obj.write(chr(num_axes))

				for axis in range(0,num_axes):
					value=int(self.joystick_obj.get_axis(axis)*127)

					if value<0:
						value+=256

					self.serial_obj.write(chr(value))

				num_buttons=min(256,self.joystick_obj.get_numbuttons())
				self.serial_obj.write(chr(num_buttons))

				button_array=[]

				for button in range(0,num_buttons):
					button_array.append(self.joystick_obj.get_button(button))

				for byte in bool_array_to_byte_array(button_array):
						self.serial_obj.write(byte)

				self.statusbar.SetStatusText("Connected to blimp.");

			except:
				self.disconnect()
				self.statusbar.SetStatusText("Serial unexpectedly disconnected.")

if __name__=="__main__":
	app=wx.App()
	frame=frame_t()
	frame.Show()
	app.MainLoop()