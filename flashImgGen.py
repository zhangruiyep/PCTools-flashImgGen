import os
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk as ttk
import types
import types
import datetime
import cfg
import csvop
	
class AddFrame(ttk.Frame):
	def __init__(self, master=None, parentIdx=""):
		ttk.Frame.__init__(self, master)
		self.grid()
		self.tv = master
		self.parentIdx = parentIdx
		self.createWidgets()
		
	def createWidgets(self):
		curRow = 0
		label = ttk.Label(self, text="File:", justify=tk.LEFT)
		label.grid(row = curRow)

		self.fileEntry = ttk.Entry(self)
		self.fileEntry.delete(0, tk.END)
		self.fileEntry.grid(row=curRow, column=1)		

		curRow += 1
		label = ttk.Label(self, text="Offset(HEX):", justify=tk.LEFT)
		label.grid(row=curRow)

		self.offEntry = ttk.Entry(self)
		self.offEntry.delete(0, tk.END)
		self.offEntry.grid(row=curRow, column=1)		

		self.getFileBtn = ttk.Button(self, text="Choose", command=self.chooseFile, width=10)
		self.getFileBtn.grid(row=0, column=2)
		
		curRow += 1
		OKBtn = ttk.Button(self, text="OK", command=self.addRecord)
		OKBtn.grid(row=curRow)
		CancelBtn = ttk.Button(self, text="Cancel", command=self.cancelAdd)
		CancelBtn.grid(row=curRow, column=1)

	def addRecord(self):
		filename = self.fileEntry.get()
		if not os.path.exists(filename):
			tkMessageBox.showwarning("Warning", "File not found")
			return
		
		offsetStr = self.offEntry.get()
		try:
			offset = int(offsetStr, 16)
		except:
			tkMessageBox.showwarning("Warning", "Offset Invalid")
			return
		
		self.tv.insert(self.parentIdx, "end", values=(filename, self.offEntry.get()))

		self.destroy()

	def cancelAdd(self):
		self.destroy()
		
	def chooseFile(self):
		filename = tkFileDialog.askopenfilename()
		if (filename != None) and (filename != ""):
			self.fileEntry.delete(0, tk.END)
			self.fileEntry.insert(0, os.path.realpath(filename))

def takeOffset(elem):
	return elem[1]

class filesTreeview(ttk.Treeview):
	def __init__(self, master=None):
		ttk.Treeview.__init__(self, master)
		self['columns']=("filename", "offset")
		self.filesdata = []
		self.grid(sticky=tk.NSEW)
		self.createWidgets()
	
	def createWidgets(self):
		self.column("#0", width=20, stretch=0)
		self.column("filename", width=400)
		self.column("offset", width=100)

		self.heading('filename', text='File Name')
		self.heading('offset', text='Offset')
		
	def fill_treeview(self, filesdata):
		self.filesdata = filesdata
		#print self.filesdata
		for item in self.get_children():
			self.delete(item)
			
		for f in self.filesdata:
			#print f
			self.insert('',"end",values=(f[0], f[1]))

	
	def update_filesdata(self):
		self.filesdata = []
		for i in self.get_children():
			#print self.item(i)["values"]
			if type(self.item(i)["values"][1]) == types.IntType:
				off = int(str(self.item(i)["values"][1]), 16)
			else:
				off = int(self.item(i)["values"][1], 16)
			self.filesdata.append([self.item(i)["values"][0], off])
		#print self.filesdata
		self.filesdata.sort(key=takeOffset)
					
class Application(ttk.Frame):
	def __init__(self, master=None):
		ttk.Frame.__init__(self, master) 
		self.cfg = cfg.configFile()
		self.columnconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)
		self.grid(sticky=tk.NSEW) 
		self.createWidgets()
		
	def createWidgets(self):
		tv_frame = ttk.Frame(self)
		tv_frame.grid(row = 2, sticky=tk.NSEW, pady = 3)
		
		self.tv = filesTreeview(tv_frame)
		self.tv.grid(row = 0, sticky=tk.NSEW)
		try:
			filesdata = csvop.readDataFile("data.csv")
		except:
			filesdata = []
		self.tv.fill_treeview(filesdata)
				
		self.sb = ttk.Scrollbar(tv_frame, orient=tk.VERTICAL, command=self.tv.yview)
		self.sb.grid(row = 0, column=1, sticky=tk.NS)
		
		self.tv.configure(yscrollcommand=self.sb.set)

		self.context_menu = tk.Menu(self.tv, tearoff=0)
		self.context_menu.add_command(label="Add", command=self.add_handler)
		self.context_menu.add_command(label="Delete", command=self.delete_handler)
		self.tv.bind('<3>', self.show_context_menu)
		self.entryPopup = ""
		self.record_frame = ""

		output_frame = ttk.Frame(self)
		output_frame.grid(row = 0, sticky=tk.NSEW, pady = 3)
		
		self.Info = ttk.Label(output_frame, text="Output file:", justify=tk.LEFT)
		self.Info.grid(row=0, sticky=tk.W, padx=10)
		
		self.outputFilePathEntry = ttk.Entry(output_frame, width = 40)
		self.outputFilePathEntry.grid(row=0, column=1, padx=10)
		if self.cfg:
			try:
				self.outputFilePathEntry.delete(0, tk.END)
				self.outputFilePathEntry.insert(0, self.cfg.cp.get("OutFile", "Name"))
			except:
				print("can not get file name from cfg")

		self.getFileBtn = ttk.Button(output_frame, text="Choose", command=self.chooseOutputFile, width=10)
		self.getFileBtn.grid(row=0, column=2, padx=10)
		
		flashOptionFrame = ttk.Frame(self)
		flashOptionFrame.grid(row = 1, sticky=tk.NSEW, pady=3)
		
		self.flashSizeInfo = ttk.Label(flashOptionFrame, text="Flash size(MB):", justify=tk.LEFT)
		self.flashSizeInfo.grid(row = 0, sticky=tk.W, padx=10)

		optionList = ["", "8", "4", "2", "1"]
		self.v = tk.StringVar()
		self.v.set(optionList[1])
		if self.cfg:
			try:
				self.v.set(self.cfg.cp.get("OutFile", "Size"))
			except:
				print("can not get file size from cfg")
			
		self.platformOpt = ttk.OptionMenu(flashOptionFrame, self.v, *optionList)
		self.platformOpt.grid(row = 0, column=1, sticky=tk.W, padx=10)

		progressFrame = ttk.Frame(self)
		progressFrame.grid(row = 3, sticky=tk.NSEW, pady=3)
		
		self.pbar = ttk.Progressbar(progressFrame,orient ="horizontal",length = 500, mode ="determinate")
		self.pbar.grid(padx=10, sticky=tk.NSEW)
		self.pbar["maximum"] = 100

		actionFrame = ttk.Frame(self)
		actionFrame.grid(row = 4, sticky=tk.NSEW, pady=3)
		
		self.genOutFileBtn = ttk.Button(actionFrame, text="Generate Flash Image", command=self.genOutFile)
		self.genOutFileBtn.grid(padx=10, row = 0, column = 0)

		self.saveCfgFileBtn = ttk.Button(actionFrame, text="Save Configuration", command=self.saveCfgFile)
		self.saveCfgFileBtn.grid(padx=10, row = 0, column = 1)		

	def show_context_menu(self, event):
		self.context_menu.post(event.x_root,event.y_root)
		self.event = event
 

	def delete_handler(self):
		#print "in copy_handler"
		#print self.event.x, self.event.y
		# close previous popups
		if self.entryPopup:
			self.entryPopup.destroy()
			
		self.edit_row = self.tv.identify_row(self.event.y)
		#print self.edit_row
		
		self.tv.focus(self.edit_row)
		
		item = self.tv.focus()
		if item != '':
			self.tv.delete(item)

		
	def add_handler(self):
		if self.entryPopup:
			self.entryPopup.destroy()

		self.edit_row = self.tv.identify_row(self.event.y)
		self.edit_column = self.tv.identify_column(self.event.x)
		#print self.tv.identify_region(self.event.x, self.event.y)
		#print self.edit_row
		#x,y,width,height = self.tv.bbox(self.edit_row)
		
		parent = self.tv.parent(self.edit_row)
		#print parent
		self.addDataFrame(parent)
			
			
	def addDataFrame(self, parentItem):
		#x,y,width,height = self.tv.bbox(parentItem)
		
		if self.record_frame:
			self.record_frame.destroy()

		self.record_frame = AddFrame(self.tv, parentItem)
		self.record_frame.place(x=0, y=20, anchor=tk.NW)			
		

	def entryEnter(self, event):
		entry_text = self.entryPopup.get()
		#print entry_text
		self.tv.set(self.edit_row, column=self.edit_column, value=entry_text)
		self.tv.update_accs()
		self.tv.update_yrr()
		self.entryPopup.destroy()
	
	def entryEntryDestroy(self, event):
		self.entryPopup.destroy()
			
	def chooseOutputFile(self):
		filename = tkFileDialog.asksaveasfilename()
		if (filename != None) and (filename != ""):
			self.outputFilePathEntry.delete(0, tk.END)
			self.outputFilePathEntry.insert(0, os.path.realpath(filename))
	
	def genOutFile(self):
		outputFile = self.outputFilePathEntry.get().strip()
		if not outputFile:
			tkMessageBox.showwarning("Warning", "Output file not set")
			return
		#print outputFile
		
		outputSizeMB = self.v.get()
		outputSize = int(outputSizeMB)*1024*1024
		#print outputSize
		
		self.tv.update_filesdata()
		
		if self.writeOutputFile(outputFile, outputSize) == True:
			tkMessageBox.showinfo("Info", "Done.")
	
	def writeOutputFile(self, filename, size):
		fo = open(filename, "wb")
		paddingChar = [255]
		for fdata in self.tv.filesdata:
			#print fdata
			if fo.tell() > fdata[1]:
				tkMessageBox.showerror("Error", "OVERLAP %s" % fdata[0])
				return False
				
			self.updateProgress(float(fo.tell())/size)
			
			for i in range(fo.tell(), fdata[1]):
				fo.write(bytearray(paddingChar))
			self.updateProgress(float(fo.tell())/size)
			
			fi = open(fdata[0], "rb")			
			fo.write(fi.read())
			if (fo.tell() > size):
				tkMessageBox.showerror("Error", "%s out of flash" % fdata[0])
				return False
			self.updateProgress(float(fo.tell())/size)
			
			fi.close()
		# padding to end fo file
		for i in range(fo.tell(), size):
			fo.write(bytearray(paddingChar))
		self.updateProgress(float(fo.tell())/size)
		fo.close()
		return True
	
	def saveCfgFile(self):
		try:
			self.cfg.cp.add_section("OutFile")
		except:
			print("section exist")
		outFileName = self.outputFilePathEntry.get().strip()
		self.cfg.cp.set("OutFile", "Name", ''.join([x.encode('utf-8') for x in outFileName]))
		self.cfg.cp.set("OutFile", "Size", self.v.get())
		
		self.tv.update_filesdata()
		
		csvop.writeDataFile(self.tv.filesdata, "data.csv")	
		
		self.cfg.write()
		return
	
	def updateProgress(self, value):
		#print value
		self.pbar["value"] = int(value * self.pbar["maximum"])
		self.update_idletasks()
		#print self.pbar["value"]

app = Application() 
app.master.title('FlashImgGen V2.0') 
app.master.rowconfigure(0, weight=1)
app.master.columnconfigure(0, weight=1)
app.mainloop() 