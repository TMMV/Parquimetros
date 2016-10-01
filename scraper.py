#!/usr/bin/env python
# -*- coding: utf-8 -*

from bs4 import BeautifulSoup
import requests
import re
import json
from ftfy import fix_text
import os
import datetime
import scraperwiki

URL = 'http://www.cm-porto.pt/ruas-tarifadas'
response = requests.get(URL, verify=False,timeout=10)
soup = BeautifulSoup(response.text, 'html.parser')
scripts = soup.find_all('script')

pTextFilename = 'parquimetros.json'
parquimetros = {}
if (os.path.isfile(pTextFilename)):
	parquimetrosFile = open(pTextFilename,"r")
	parquimetros = json.load(parquimetrosFile)
	parquimetrosFile.close()

currentDate = datetime.date.today().strftime("%d-%m-%Y")

for script in scripts:
	scriptText = script.text
	#print(scriptText)
	roadTemp = re.findall(r"title:( *)'(.*?)',", script.text)
	roads = []
	for road in roadTemp:
		#roads.append(fix_text(road[1].lstrip()).encode('utf-8'))
		roads.append(fix_text(road[1].lstrip(), normalization='NFKC').encode('utf-8').replace('Ã¡','á')) # oh god it burns

	coords = re.findall('LatLng\((.*?)\)',script.text)
	coords = coords[:-2]

	zipped = zip(roads, coords)

	finalDict = []
	for location in zipped:
		finalDict.append({
			"street": location[0],
			"latitude": location[1].split(",")[0],
            "longitude": location[1].split(",")[1].lstrip()
		})

	if len(finalDict) > 0:
		break

parquimetros[currentDate] = finalDict

parquimetrosFile = open(pTextFilename,"w")
json.dump(parquimetros, parquimetrosFile,  ensure_ascii=False,encoding="utf-8", indent=4)
parquimetrosFile.close()

# save in sqlite too
for entry in parquimetros[currentDate]:
    tableEntry = {
        "date": currentDate,
        "street": entry["street"].decode('utf-8'),
        "longitude": entry["longitude"],
        "latitude": entry["latitude"]
    }
    scraperwiki.sql.save(unique_keys=['date','street','longitude','latitude'], data=tableEntry)
