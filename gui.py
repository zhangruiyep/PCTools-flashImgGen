import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import os
import tkinter.ttk
import types
import datetime
import cfg
import csvop
import flashImage

class AddFrame(tkinter.ttk.Frame):
	def __init__(self, master=None, parentIdx=""):
		tkinter.ttk.Frame.__init__(self, master)
		self.grid()
		self.tv = master
		self.parentIdx = parentIdx
		self.createWidgets()
		
	def createWidgets(self):
		dataframe = tkinter.ttk.Frame(self)
		dataframe.grid(row = 0, pady=3)
		
		label = tkinter.ttk.Label(dataframe, text="File:", justify=tk.LEFT)
		label.grid(row=0, sticky=tk.E, padx=6, pady=3)

		self.fileEntry = tkinter.ttk.Entry(dataframe)
		self.fileEntry.delete(0, tk.END)
		self.fileEntry.grid(row=0, column=1, padx=6, pady=3)		

		self.getFileBtn = tkinter.ttk.Button(dataframe, text="Choose", command=self.chooseFile, width=10)
		self.getFileBtn.grid(row=0, column=2, padx=6, pady=3)

		label = tkinter.ttk.Label(dataframe, text="Offset(HEX):", justify=tk.LEFT)
		label.grid(row=1, sticky=tk.E, padx=6, pady=3)

		self.offEntry = tkinter.ttk.Entry(dataframe)
		self.offEntry.delete(0, tk.END)
		self.offEntry.grid(row=1, column=1, padx=6, pady=3)		

		btnframe = tkinter.ttk.Frame(self)
		btnframe.grid(row = 1, pady=3)
		
		OKBtn = tkinter.ttk.Button(btnframe, text="OK", command=self.addRecord)
		OKBtn.grid(row=0, padx=6)
		CancelBtn = tkinter.ttk.Button(btnframe, text="Cancel", command=self.cancelAdd)
		CancelBtn.grid(row=0, column=1, padx=6)

	def addRecord(self):
		filename = self.fileEntry.get()
		if not os.path.exists(filename):
			tkinter.messagebox.showwarning("Warning", "File not found")
			return
		
		offsetStr = self.offEntry.get()
		try:
			offset = int(offsetStr, 16)
		except:
			tkinter.messagebox.showwarning("Warning", "Offset Invalid")
			return
		
		self.tv.insert(self.parentIdx, "end", values=(filename, self.offEntry.get()))

		self.destroy()

	def cancelAdd(self):
		self.destroy()
		
	def chooseFile(self):
		filename = tkinter.filedialog.askopenfilename()
		if (filename != None) and (filename != ""):
			self.fileEntry.delete(0, tk.END)
			self.fileEntry.insert(0, os.path.realpath(filename))

def takeOffset(elem):
	return elem[1]

class filesTreeview(tkinter.ttk.Treeview):
	def __init__(self, master=None):
		tkinter.ttk.Treeview.__init__(self, master)
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
		for item in self.get_children():
			self.delete(item)
			
		for f in self.filesdata:
			self.insert('',"end",values=(f[0], f[1]))

	
	def update_filesdata(self):
		self.filesdata = []
		for i in self.get_children():
			if type(self.item(i)["values"][1]) == int:
				off = int(str(self.item(i)["values"][1]), 16)
			else:
				off = int(self.item(i)["values"][1], 16)
			self.filesdata.append([self.item(i)["values"][0], off])
		self.filesdata.sort(key=takeOffset)
					
class Application(tkinter.ttk.Frame):
	def __init__(self, master=None):
		tkinter.ttk.Frame.__init__(self, master) 
		self.cfg = cfg.configFile()
		self.columnconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)
		self.grid(sticky=tk.NSEW) 
		self.createWidgets()
		
	def createWidgets(self):
		tv_frame = tkinter.ttk.Frame(self)
		tv_frame.grid(row = 2, sticky=tk.NSEW, pady = 3)
		
		self.tv = filesTreeview(tv_frame)
		self.tv.grid(row = 0, sticky=tk.NSEW)
		try:
			filesdata = csvop.readDataFile("data.csv")
		except:
			filesdata = []
		self.tv.fill_treeview(filesdata)
				
		self.sb = tkinter.ttk.Scrollbar(tv_frame, orient=tk.VERTICAL, command=self.tv.yview)
		self.sb.grid(row = 0, column=1, sticky=tk.NS)
		
		self.tv.configure(yscrollcommand=self.sb.set)

		self.context_menu = tk.Menu(self.tv, tearoff=0)
		self.context_menu.add_command(label="Add", command=self.add_handler)
		self.context_menu.add_command(label="Delete", command=self.delete_handler)
		self.tv.bind('<3>', self.show_context_menu)
		self.entryPopup = ""
		self.record_frame = ""

		output_frame = tkinter.ttk.Frame(self)
		output_frame.grid(row = 0, sticky=tk.NSEW, pady = 3)
		
		self.Info = tkinter.ttk.Label(output_frame, text="Output file:", justify=tk.LEFT)
		self.Info.grid(row=0, sticky=tk.W, padx=10)
		
		self.outputFilePathEntry = tkinter.ttk.Entry(output_frame, width = 40)
		self.outputFilePathEntry.grid(row=0, column=1, padx=10)
		if self.cfg:
			try:
				self.outputFilePathEntry.delete(0, tk.END)
				self.outputFilePathEntry.insert(0, self.cfg.cp['OutFile']['Name'])
			except:
				print("can not get file name from cfg")

		self.getFileBtn = tkinter.ttk.Button(output_frame, text="Choose", command=self.chooseOutputFile, width=10)
		self.getFileBtn.grid(row=0, column=2, padx=10)
		
		flashOptionFrame = tkinter.ttk.Frame(self)
		flashOptionFrame.grid(row = 1, sticky=tk.NSEW, pady=3)
		
		self.flashSizeInfo = tkinter.ttk.Label(flashOptionFrame, text="Flash size(MB):", justify=tk.LEFT)
		self.flashSizeInfo.grid(row = 0, sticky=tk.W, padx=10)

		optionList = ["", "8", "4", "2", "1"]
		self.v = tk.StringVar()
		self.v.set(optionList[1])
		if self.cfg:
			try:
				self.v.set(self.cfg.cp['OutFile']['Size'])
			except:
				print("can not get file size from cfg")
			
		self.platformOpt = tkinter.ttk.OptionMenu(flashOptionFrame, self.v, *optionList)
		self.platformOpt.grid(row = 0, column=1, sticky=tk.W, padx=10)

		progressFrame = tkinter.ttk.Frame(self)
		progressFrame.grid(row = 3, sticky=tk.NSEW, pady=3)
		
		self.pbar = tkinter.ttk.Progressbar(progressFrame,orient ="horizontal",length = 500, mode ="determinate")
		self.pbar.grid(padx=10, sticky=tk.NSEW)
		self.pbar["maximum"] = 100

		actionFrame = tkinter.ttk.Frame(self)
		actionFrame.grid(row = 4, sticky=tk.NSEW, pady=3)
		
		self.genOutFileBtn = tkinter.ttk.Button(actionFrame, text="Generate Flash Image", command=self.genOutFile)
		self.genOutFileBtn.grid(padx=10, row = 0, column = 0)

		self.saveCfgFileBtn = tkinter.ttk.Button(actionFrame, text="Save Configuration", command=self.saveCfgFile)
		self.saveCfgFileBtn.grid(padx=10, row = 0, column = 1)		

	def show_context_menu(self, event):
		self.context_menu.post(event.x_root,event.y_root)
		self.event = event
 

	def delete_handler(self):
		# close previous popups
		if self.entryPopup:
			self.entryPopup.destroy()
			
		self.edit_row = self.tv.identify_row(self.event.y)
		
		self.tv.focus(self.edit_row)
		
		item = self.tv.focus()
		if item != '':
			self.tv.delete(item)

		
	def add_handler(self):
		if self.entryPopup:
			self.entryPopup.destroy()

		self.edit_row = self.tv.identify_row(self.event.y)
		self.edit_column = self.tv.identify_column(self.event.x)
		
		parent = self.tv.parent(self.edit_row)
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
		filename = tkinter.filedialog.asksaveasfilename()
		if (filename != None) and (filename != ""):
			self.outputFilePathEntry.delete(0, tk.END)
			self.outputFilePathEntry.insert(0, os.path.realpath(filename))
	
	def genOutFile(self):
		outputFile = self.outputFilePathEntry.get().strip()
		if not outputFile:
			tkinter.messagebox.showwarning("Warning", "Output file not set")
			return
		
		outputSizeMB = self.v.get()
		outputSize = int(outputSizeMB)*1024*1024
		
		self.tv.update_filesdata()
		
		img = flashImage.flashImage(outputFile, outputSize, self.tv.filesdata, self.updateProgress)
		retval = img.writeFile()
		if (retval.result == "Error"):
			tkinter.messagebox.showerror(retval.result, retval.msg)
		else:
			tkinter.messagebox.showinfo("Info", retval.msg)
		
	def saveCfgFile(self):
		try:
			self.cfg.cp.add_section("OutFile")
		except:
			print("section exist")
		outFileName = self.outputFilePathEntry.get().strip()
		self.cfg.cp['OutFile']['Name'] = outFileName
		self.cfg.cp['OutFile']['Size'] = self.v.get()
		self.cfg.write()

		self.tv.update_filesdata()
		csvop.writeDataFile(self.tv.filesdata, "data.csv")	

		return
	
	def updateProgress(self, value):
		self.pbar["value"] = int(value * self.pbar["maximum"])
		self.update_idletasks()

app = Application() 
app.master.title('FlashImgGen') 
app.master.rowconfigure(0, weight=1)
app.master.columnconfigure(0, weight=1)
app.mainloop() 