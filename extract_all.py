import csv
import json

import mod_rom_extr_christian
import mod_rom_extr_neutral
import mod_rom_extr_grc

def jsonToCsv(jsonObj, outFile):
	inJson = json.dumps(jsonObj)
	
	allRecords = json.loads(inJson)

	f = csv.writer(open(outFile, "w", newline=''))
	
	# Write CSV Header, If you dont need that, remove this line
	f.writerow(["CATEGORY", "POSTAL", "AFFLIATION", "NAME", "LANGUAGE", "PHONE", "EMAIL", "LICENSE EXPIRING"])
	for details in allRecords:
		f.writerow([details["CATEGORY"],
			details["POSTAL"],
			details["AFFLIATION"],
			details["NAME"],
			details["LANGUAGE"],
			details["PHONE"],
			details["EMAIL"],
			details["LICENCE_EXPIRE"]])


if __name__ == "__main__":
	sol = []
	
	codes = "AD,AN,AG,BA,BP,BR,EC,CS,ID,LU,ME,PE,PR,RC".split(",")
	extr = mod_rom_extr_christian.Extractor()
	x = extr.extractAll(codes)
	for e in x:
		e["CATEGORY"] = "CHURCH"
	sol.extend(x)
	
	codes = "A,F,J".split(",")
	extr = mod_rom_extr_neutral.Extractor()
	x = extr.extractAll(codes)
	for e in x:
		e["CATEGORY"] = "NEUTRAL"
	sol.extend(x)
	
	codes = "AJ,AM,BS,CC,EC,HB,JB,JR,MA,MY,NS,PN,SB,SC,TM,TP,WC".split(",")
	extr = mod_rom_extr_grc.Extractor()
	x = extr.extractAll(codes)
	for e in x:
		e["CATEGORY"] = "GRC"
	sol.extend(x)
	
	
	jsonToCsv(sol, "ROM_LIST_ALL.csv")
		
