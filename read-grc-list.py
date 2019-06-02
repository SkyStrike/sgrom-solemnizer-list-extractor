import requests
import os
from os import system
from colorama import Fore, Back, Style, init
init(autoreset=True)

from bs4 import BeautifulSoup
import re
import json
import csv
import sys


URL="https://www.rom.gov.sg/reg_info/rom_grassroots_all.asp"


def getHTMLAsFile(u, selGRC, tmpFileName):
	r = requests.post(url = u, data={
		"selGRC": selGRC
	});
	
	with open(tmpFileName,'wb') as output:
		output.write(r.content)


def readFile(f):
	htmlFile=open(f, "r")
	return htmlFile.read()


def extract(orgType):
	print("Processing...", orgType)
	
	tmpFileName = "temp.tmp"
	
	getHTMLAsFile(URL, orgType, tmpFileName)
	html = readFile(tmpFileName)
	
	soup = BeautifulSoup(html, 'html.parser')
	
	solemizerNames = []
	solomizerList = []
	tdData = []
	for i in soup.find_all("table", {'class': re.compile(r'^table_content')}):
		
		allTds = i.find_all("td")
		for i in range(len(allTds)):
			txt = allTds[i].getText().strip()
			if (len(txt) > 1):
				tdData.append(txt)

	lastIdx = 0
	
	
	affliation = ""
	for i in range(len(tdData)):
	
		txt = tdData[i]
		#print(lastIdx, i, tdData[i])
		
		if txt.find("LICENCE") > -1:
		
			tmp = {}
			setData = tdData[(lastIdx+1):(i+1)]
			#for x in setData:
			#	print(x)
			
			#print("------------")
			
			startFrom = 0
			for x in range(len(setData)):
			
				#identify affliation in set of data
				txt = setData[x]
				if 	txt.find(" CLUB") > -1 or txt.find(" CONSTITUENCY") > -1 or txt.find(" CENTRE") > -1 or txt.find(" CONSITUENCY") > -1 or txt.find(" COMMUNITY") > -1:
					
					affliation = txt
					startFrom = x+1

			#print("len(setData)", len(setData))
			#for x in range(len(setData)):
			#	print(x, setData[x])
			#
			#print("1---------")
			#for x in range(startFrom, len(setData)):
			#	print(x, setData[x])
			#print("2---------")
			#
			#print(startFrom, len(setData))
			
			val_postalCode = "N/A"
			val_affliation = affliation
			val_name = ""
			val_lang = ""
			val_phone = ""
			val_email = ""
			val_license = ""
			
			for x in range(startFrom, len(setData)):
				txt = setData[x].strip()
				
				if val_name == "":
					val_name = txt
									
				elif val_phone == "":

					if ("\n" in txt):
						contact = txt.split('\n')
						for t in contact:
							t = t.strip()
							if t != "":
								if val_phone == "":
									val_phone = t
								elif val_email == "":
									val_email = t

					else:
						x = re.search("\d{5}", txt)
						if x is not None:
							val_phone = txt
						else:
							val_phone = "N/A"
							val_email = txt
						
				elif txt.find("A.K.A") > -1:
					val_name = val_name + "," + txt	
					
				elif val_lang == "":
					val_lang = txt.replace("LANGUAGE PREFERRED:", "").strip()
					if (val_lang == ""):
						val_lang = "Not Specified"
						
				elif val_license == "":
					val_license = txt.replace("LICENCE EXPIRING ON: ", "").strip()

			tmp["POSTAL"] = val_postalCode
			tmp["AFFLIATION"] = val_affliation
			tmp["NAME"] = val_name
			tmp["LANGUAGE"] = val_lang
			tmp["PHONE"] = val_phone
			tmp["LICENCE_EXPIRE"] = val_license
			tmp["EMAIL"] = val_email
			
			#print(json.dumps(tmp, indent='    '))
			
			if val_name not in solemizerNames:
				solomizerList.append(tmp)
				solemizerNames.append(val_name)
			
			lastIdx = i
			
	print(json.dumps(solomizerList, indent = '   '))
	print("=============== End Processing for [" + orgType + "] ========================")
			
	os.remove(tmpFileName)
	return solomizerList


def jsonToCsv(jsonObj, outFile):
	inJson = json.dumps(jsonObj)
	
	allRecords = json.loads(inJson)

	f = csv.writer(open(outFile, "w", newline=''))
	
	# Write CSV Header, If you dont need that, remove this line
	f.writerow(["POSTAL", "AFFLIATION", "NAME", "LANGUAGE", "PHONE", "EMAIL", "LICENSE EXPIRING"])
	for details in allRecords:
		f.writerow([details["POSTAL"],
			details["AFFLIATION"],
			details["NAME"],
			details["LANGUAGE"],
			details["PHONE"],
			details["EMAIL"],
			details["LICENCE_EXPIRE"]])



def main():
		
	sol = []	
	cmd_codes = sys.argv[1]
	output_file_name = sys.argv[2]
	codes = cmd_codes.split(",")

	for code in codes:
		tmp = extract(code)
		if len(tmp) > 0:
			for x in tmp:
				sol.append(x)
				
	jsonToCsv(sol, output_file_name)
	
if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("No codes found to extract.")
		print("Usage: xxxx.py \"CODE_A, CODE_B .....\" myFile.csv")
	else:
		main()

