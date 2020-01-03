import csv

def readDataFile(filename):
	filesdata = []
	f = open(filename, "rb")
	rdr = csv.reader(f)
	for row in rdr:
		filesdata.append([row[0], row[1]])
	f.close()
	return filesdata

def writeDataFile(filesdata, filename):
	print("saving %s" % filename)
	with open(filename, "wb") as f:
		wtr = csv.writer(f)
		for r in filesdata:
			row = []
			row.append(''.join([x.encode('utf-8') for x in r[0]]))
			row.append(hex(int(r[1]))[2:])
			print(row)
			wtr.writerow(row)
		f.close()
	