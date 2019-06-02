import requests
import os
from os import system
from colorama import Fore, Back, Style, init
init(autoreset=True)

from bs4 import BeautifulSoup
import re
import sys
import json
import csv

'''
This program does not work for Grassroot page.
	rom_grassroots_all.asp
	
'''


URL="https://www.rom.gov.sg/reg_info/rom_licensed_sol_result2.asp"


def getHTMLAsFile(u, churchCode, tmpFileName):
	r = requests.post(url = u, data={
		"cboDenomination": churchCode
	});
	
	with open(tmpFileName,'wb') as output:
		output.write(r.content)


def readFile(f):
	htmlFile=open(f, "r")
	return htmlFile.read()
	

def extract(churchCode):
	print("Processing...", churchCode)
	
	tmpFileName = "temp.tmp"
	#outputFileName = outputFile + ".json"
	
	getHTMLAsFile(URL, churchCode, tmpFileName)
	html = readFile(tmpFileName)
	
	soup = BeautifulSoup(html, 'html.parser')
	
	solomizerList = []
	tdData = []
	tables = soup.find_all("table", {'class': "content_table"})
	
	contentTable = None
	for table in tables:
		txt = table.getText()
		if len(txt) > 100:
			contentTable = table
	
	allTds = contentTable.find_all("td")
	
	tdData = []
	for td in allTds:
		txt = td.getText()
		#need to clean up HTML misconstruct
		if (len(txt) > 1 and len(txt) < 200 and txt != "Licensed Solemnizers"):
			tdData.append(txt)

	#solomizerList
	for i in range(len(tdData)):
		txt = tdData[i]
		#print(txt.find("CHURCH"), txt.find("CONFERENCE"))	
		if txt.find("CHURCH") > -1 or txt.find("CONFERENCE") > -1:
			
			tmp = {}
			
			#first 4 are fixed.
			val_postalCode = "N/A"
			val_affliation = tdData[i]
			val_name = tdData[i+1]
			val_lang = tdData[i+2]
			val_phone = ""
			val_email = ""
			val_license = ""

			lastCount = i+2
			if (val_lang is not None):
				if val_lang.find("A.K.A") > -1:
					val_name = val_name + "," + val_lang
					val_lang = tdData[i+3]
					lastCount = i+3
				
				val_lang = val_lang.replace("LANGUAGE PREFERRED: ", "")

					
			if (val_postalCode is not None):
				val_postalCode = val_postalCode.replace("POSTAL CODE: ", "")
				
			
			if ((lastCount+1) < len(tdData)):
				dat = tdData[lastCount+1]
				x = re.search("\d{5}", dat)
				if x is not None:
					val_phone = dat
					lastCount = lastCount+1
			
			if ((lastCount+1) < len(tdData)):
				dat = tdData[lastCount+1]
				if dat.find('LICENCE') > -1:
					val_license = dat.replace("LICENCE EXPIRING ON: ", "")
					lastCount = lastCount+1
					
			if ((lastCount+1) < len(tdData)):
				dat = tdData[lastCount+1]
				if dat.find('EMAIL') > -1:
					val_email = dat.replace("EMAIL: ", "")
					lastCount = lastCount+1
			
			
			tmp["POSTAL"] = val_postalCode
			tmp["AFFLIATION"] = val_affliation
			tmp["NAME"] = val_name
			tmp["LANGUAGE"] = val_lang
			tmp["PHONE"] = val_phone
			tmp["LICENCE_EXPIRE"] = val_license
			tmp["EMAIL"] = val_email
			
			solomizerList.append(tmp)

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


	#B,T is for buddhist and taoist
	#codes = ["B", "T"]		
	#codes = ["A", "F", "J"]
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


