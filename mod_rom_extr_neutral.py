import requests
import os
import re
import json
import sys
from bs4 import BeautifulSoup

class Extractor:
	def __init__(self):
		self.URL="https://www.rom.gov.sg/reg_info/rom_licensed_sol_result.asp"
	
	'''
	save HTML as temp file for working on.
	Technically is not required for saving as tmp file,
	but this will allow debugger to debug without 
	pulling too many times from the website

	I scared kenna blacklisted/blocked from website.
	'''
	def getHTMLAsFile(self, u, orgType, tmpFileName):
	
		payload = {
			"orgType": orgType
		}
		
		print("Sending HTTP POST request to ", u)
		print("Payload: ", payload)

		r = requests.post(url = u, data=payload);
		
		with open(tmpFileName,'wb') as output:
			output.write(r.content)
		
		print("Saved HTML results to ", tmpFileName)

	#simple read file as text
	def readFile(self, f):
		print("Reading file: ", f)
		htmlFile=open(f, "r")
		return htmlFile.read()
		
	
	#performs the magic
	def extractAll(self, codes):
		sol = []
		for code in codes:
			print("=============================")
			print("Processing Code: ", code)
			tmp = self.extract(code)
			if len(tmp) > 0:
				for x in tmp:
					sol.append(x)
			
			print("Completed.")
			
		return sol
	

	#performs the magic
	def extract(self, orgType):
		print("Processing...", orgType)
		
		tmpFileName = "temp.tmp"
		
		self.getHTMLAsFile(self.URL, orgType, tmpFileName)
		html = self.readFile(tmpFileName)
		
		soup = BeautifulSoup(html, 'html.parser')
		
		solomizerList = []
		solemizerNames = []
		'''
		General Notes:
		The parsing requires abit of studying of the HTML structure of the data.
		Takes into consideration of invalid HTML constructs (e.g. Open tags without 
		closing or missing closing tags etc)
		
		Developer Notes:
		The neutral lists are still easier to parse as compared to the GRC and Christian list where typos exists
		'''
		for i in soup.find_all("table", {'class': re.compile(r'^table_content')}):
			
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
					
					#prevent duplicates. Technically, this will prevent the closing tag errors
					if val_name not in solemizerNames:
						solomizerList.append(tmp)
						solemizerNames.append(val_name)
			
		os.remove(tmpFileName)
		return solomizerList
		