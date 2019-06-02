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

'''
This program does not work for Grassroot page.
	rom_grassroots_all.asp
	
'''


URL="https://www.rom.gov.sg/reg_info/rom_licensed_sol_result.asp"


def getHTMLAsFile(u, orgType, tmpFileName):
	r = requests.post(url = u, data={
		"orgType": orgType
	});
	
	with open(tmpFileName,'wb') as output:
		output.write(r.content)


def readFile(f):
	htmlFile=open(f, "r")
	return htmlFile.read()
	
#html = readFile("list.html")

#soup = BeautifulSoup(html, 'html.parser')

#for novel_group in soup.find_all(class_='novel_list')

#print(soup.prettify())


def extract(orgType):
	print("Processing...", orgType)
	
	tmpFileName = "temp.tmp"
	
	getHTMLAsFile(URL, orgType, tmpFileName)
	html = readFile(tmpFileName)
	
	soup = BeautifulSoup(html, 'html.parser')
	
	solomizerList = []
	for i in soup.find_all("table", {'class': re.compile(r'^table_content')}):
		#print(i.prettify())
		
		allTds = i.find_all("td")
		tdData = []
		for i in range(len(allTds)):
			txt = allTds[i].getText()
			if (len(txt) > 1):
				tdData.append(txt)

		cleanDataStart = 0
		for i in range(len(tdData)):
			txt = tdData[i]
			if (txt.find("POSTAL") > -1):
				cleanDataStart = i
				break
			
		tdData = tdData[cleanDataStart:]
		
		#solomizerList
		for i in range(len(tdData)):
			txt = tdData[i]
			if (txt.find("POSTAL") > -1):
				tmp = {}
				
				#first 4 are fixed.
				val_postalCode = tdData[i+0]
				val_affliation = tdData[i+1]
				val_name = tdData[i+2]
				val_lang = tdData[i+3]
				val_phone = ""
				val_email = ""
				val_license = ""

				lastCount = i+3
				if (val_lang is not None):
					if val_lang.find("A.K.A") > -1:
						val_name = val_name + "," + val_lang
						val_lang = tdData[i+4]
						lastCount = i+4
					
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

		#print(json.dumps(solomizerList, indent=4))
		
		#with open(outputFileName, 'w') as output:
		#	output.write(json.dumps(solomizerList, indent=4))
		
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

