import os
import sys
import configparser

class configFile():
	def __init__(self, master=None):
		self.cp = configparser.ConfigParser()
		self.cp.read(os.path.join(os.path.split(os.path.realpath(__file__))[0],"cfg.ini"))
	
	def write(self, filename="cfg.ini"):
		realFileName = os.path.join(os.path.split(os.path.realpath(__file__))[0],filename)
		writeFile = open(realFileName, "w")
		self.cp.write(writeFile)
		writeFile.close()

