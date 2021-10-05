## 
##  Copyright (C) 2021 Francesco Del Castillo - Comune di Rivoli
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU Affero General Public License as
##  published by the Free Software Foundation, either version 3 of the
##  License, or (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU Affero General Public License for more details.
##
##  You should have received a copy of the GNU Affero General Public License
##  along with this program.  If not, see <https://www.gnu.org/licenses/>. 

## Definizione delle regole di interazione con le API di app IO (https://developer.io.italia.it/openapi.html)


import requests
import socket
import datetime
import json
import os
import serviziIO

# import logging

cftest="AAAAAA00A00A000A" ## codice fiscale di test in ambiente IO
baseURL = "https://api.io.italia.it/api/v1" # url di base dei web service IO

logFileName="appIO.log"


# logging.basicConfig(level=logging.DEBUG)

def getIPAddress():
    return socket.gethostbyname(socket.gethostname())

callingIP = getIPAddress()
callingUser = os.getlogin()

def timestamp():
    return datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')

def logRequest(logFile, requestTime, verbo, metodo, info):
    rigaDiLog=[requestTime, callingIP, callingUser, verbo, metodo, info]
    logFile.write(";".join(rigaDiLog))
    logFile.write("\n")
    logFile.flush()

def logResponse(logFile, responseTime, requestTime, status_code, info):
    rigaDiLog=[responseTime, callingIP, requestTime, str(status_code), info]
    logFile.write(";".join(rigaDiLog))
    logFile.write("\n")
    logFile.flush()

def getProfile(codiceFiscale, servizioIO):
    headers={"Ocp-Apim-Subscription-Key":serviziIO.serviziIO[servizioIO]["APIKEY"]}
    with open(logFileName, "a+") as logFile:
        requestTime=timestamp()
        logRequest(logFile, requestTime, "GET", "profiles", codiceFiscale)
        r = requests.get(baseURL+"/profiles/"+codiceFiscale, headers = headers, timeout=100)
        responseTime=timestamp()
        info = str(r.json()["sender_allowed"]) if r.status_code==200 else str(r.json()["title"])
        logResponse(logFile, responseTime, requestTime, r.status_code, info)
        return r

def getProfilePost(codiceFiscale, servizioIO):
    headers={"Ocp-Apim-Subscription-Key":serviziIO.serviziIO[servizioIO]["APIKEY"]}
    with open(logFileName, "a+") as logFile:
        requestTime=timestamp()
        logRequest(logFile, requestTime, "GET", "profiles", codiceFiscale)
        r = requests.post(baseURL+"/profiles", headers = headers, timeout=100, json={"fiscal_code" : codiceFiscale})
        responseTime=timestamp()
        info = str(r.json()["sender_allowed"]) if r.status_code==200 else str(r.json()["title"])
        logResponse(logFile, responseTime, requestTime, r.status_code, info)
        return r

def submitMessage(codiceFiscale, servizioIO, body): #CF nel payload
    headers={"Ocp-Apim-Subscription-Key":serviziIO.serviziIO[servizioIO]["APIKEY"], "Content-Type":"application/json", "Connection":"keep-alive"}
    with open(logFileName, "a+") as logFile:
        requestTime=timestamp()
        logRequest(logFile, requestTime, "POST", "submitMessage", codiceFiscale)
        r = requests.post(baseURL+"/messages", headers = headers, timeout=100, json=body)
        responseTime=timestamp()
        info = str(r.json()["id"]) if r.status_code==201 else str(r.json()["title"])
        logResponse(logFile, responseTime, requestTime, r.status_code, info)
        return r

def submitMessageCF(codiceFiscale, servizioIO, body):   #CF nell'URL
    headers={"Ocp-Apim-Subscription-Key":serviziIO.serviziIO[servizioIO]["APIKEY"], "Content-Type":"application/json", "Connection":"keep-alive"}
    with open(logFileName, "a+") as logFile:
        requestTime=timestamp()
        logRequest(logFile, requestTime, "POST", "submitMessage", codiceFiscale)
        r = requests.post(baseURL+"/messages/"+codiceFiscale, headers=headers, timeout=100, json=body)
        responseTime=timestamp()
        info = str(r.json()["id"]) if r.status_code==201 else str(r.json()["title"])
        logResponse(logFile, responseTime, requestTime, r.status_code, info)
        return r

def getMessage(codiceFiscale, message_id, servizioIO):
    headers={"Ocp-Apim-Subscription-Key": serviziIO.serviziIO[servizioIO]["APIKEY"]}
    with open(logFileName, "a+") as logFile:
        requestTime=timestamp()
        logRequest(logFile, requestTime, "GET", "getMessage", message_id)
        r = requests.get(baseURL+"/messages/"+codiceFiscale+"/"+message_id, headers=headers, timeout=100)
        responseTime=timestamp()
        info = str(r.json()["status"]) if r.status_code==200 else str(r.json()["title"])
        logResponse(logFile, responseTime, requestTime, r.status_code, info)
        return r

def controllaCF(listaCF, servizioIO): ## definizione della funzione per controllare iscrizione di una lista di CF a un servizio
    utentiIscritti=[]
    utentiNonIscritti=[]
    utentiSenzaAppIO=[]
    interrogazioniInErrore=[]
    contatore=1
    totale=len(listaCF)
    for cf in listaCF:
        print(contatore,"di",totale)
        risposta = getProfilePost(cf, servizioIO)
        if risposta.status_code==200:
            if risposta.json()["sender_allowed"]:
                utentiIscritti.append(cf)
            else:
                utentiNonIscritti.append(cf)
        else:
            if risposta.status_code==404:
                utentiSenzaAppIO.append(cf)
            else:
                interrogazioniInErrore.append(cf)
        contatore=contatore+1
    return {"iscritti":utentiIscritti, "nonIscritti":utentiNonIscritti, "senzaAppIO":utentiSenzaAppIO, "inErrore":interrogazioniInErrore}   
    

