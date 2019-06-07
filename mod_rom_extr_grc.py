import requests
import os
import re
import json
import sys
from bs4 import BeautifulSoup

class Extractor:
	def __init__(self):
		self.URL="https://www.rom.gov.sg/reg_info/rom_grassroots_all.asp"
	
	'''
	save HTML as temp file for working on.
	Technically is not required for saving as tmp file,
	but this will allow debugger to debug without 
	pulling too many times from the website

	I scared kenna blacklisted/blocked from website.
	'''
	def getHTMLAsFile(self, u, selGRC, tmpFileName):
	
		payload = {
			"selGRC": selGRC
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
		
		solemizerNames = []
		solomizerList = []
		tdData = []
		
		'''
		General Notes:
		The parsing requires abit of studying of the HTML structure of the data.
		Takes into consideration of invalid HTML constructs (e.g. Open tags without 
		closing or missing closing tags etc)
		
		Developer Notes:
		
		'''
		for i in soup.find_all("table", {'class': re.compile(r'^table_content')}):
			
			allTds = i.find_all("td")
			for i in range(len(allTds)):
				txt = allTds[i].getText().strip()
				if (len(txt) > 1):
					tdData.append(txt)

		lastIdx = 0

		#texts to detect affliation. Note the spacing AND typos.
		affliationTxts = [" CLUB", " CONSTITUENCY", " CENTRE", " CONSITUENCY", " COMMUNITY"]
		
		#need a sticky affliation due to data structure
		affliation = ""
		for i in range(len(tdData)):
		
			txt = tdData[i]

			if txt.find("LICENCE") > -1:
			
				tmp = {}
				setData = tdData[(lastIdx+1):(i+1)]

				startFrom = 0
				for x in range(len(setData)):
				
					#identify affliation in set of data
					txt = setData[x]
					for aff in affliationTxts:
						if txt.find(aff) > -1:
							affliation = txt
							startFrom = x+1
							break
							
					#if 	txt.find(" CLUB") > -1 or txt.find(" CONSTITUENCY") > -1 or txt.find(" CENTRE") > -1 or txt.find(" CONSITUENCY") > -1 or txt.find(" COMMUNITY") > -1:

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
				
				#prevent duplicates. Technically, this will prevent the closing tag errors
				if val_name not in solemizerNames:
					solomizerList.append(tmp)
					solemizerNames.append(val_name)
				
				lastIdx = i
				
		#print("=============== End Processing for [" + orgType + "] ========================")
				
		os.remove(tmpFileName)
		return solomizerList
		