import requests
import json
import urllib.parse
from datetime import date
import pprint

#accuweatherAPIKEY1 ='ZPs9y75OXxMQleJqAp57b0ikeLFMGhgE'
#accuweatherAPIKEY2 ='AXMjnUzZa6XfqxZfsd8Q3POQaLFRA8AJ'
accuweatherAPIKEY = 'AQRBI8EIB5ka2nj8tuxwgW9F7ffe3U3d'
mapboxToken =  'pk.eyJ1Ijoic2FmZWVtYWlsMjkiLCJhIjoiY2s4ZDRzcmU3MG50ajNlcWVsMTVkZG9rcSJ9.-ZYQmHZv6ln1N3puH6s8Rw'

dias_semana = ['Domingo', 'Segunda-Feira', 'Terça-Feira', 'Quarta-Feira', 'Quinta-Feira', 'Sexta-Feira', 'Sábado']

def pegarCoordenadas(): #pega as coordenadas de acordo com o JSON
    r = requests.get('http://www.geoplugin.net/json.gp')

    if (r.status_code != 200):
        print('\nNão foi possível obter a localização.')
        return None
    else:
        try:
            localization = json.loads(r.text)
            coordenadas = {}
            coordenadas['lat'] = localization['geoplugin_latitude']
            coordenadas['long'] = localization['geoplugin_longitude']
            return coordenadas
        except:
            return None

def pegarCodLocal(lat,long): #pega a key do local baseada na lat e long


    LocationAPIUrl = "http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=" + accuweatherAPIKEY + "&q="+ lat +"%2C"+ long +"&language=pt-br"

    r = requests.get(LocationAPIUrl)
    
    if (r.status_code != 200):
        print('\nNão foi possível o código do local.')
        return None
    else:
        try:
            locationResponse = json.loads(r.text)
            infoLocal = {}
            infoLocal['nomeLocal'] = locationResponse['LocalizedName'] + ", " + locationResponse['AdministrativeArea']['LocalizedName']  + ", " + locationResponse['Country']['LocalizedName']
            infoLocal['codigoLocal'] = locationResponse['Key']
            return infoLocal
        except:
            return None
def getWeather(codigoLocal, nomeLocal):
        
    CurrentConditionsAPIUrl = "http://dataservice.accuweather.com/currentconditions/v1/" + codigoLocal + "?apikey=" + accuweatherAPIKEY + "&language=pt-br"

    r = requests.get(CurrentConditionsAPIUrl)
    if (r.status_code != 200):
        print('\nNão foi obter o clima atual.')
        return None
    else:
        try:
            CurrentConditionsResponse = json.loads(r.text)
            infoWeather ={}
            infoWeather['weather'] = CurrentConditionsResponse[0]['WeatherText']
            infoWeather['temp'] = CurrentConditionsResponse[0]['Temperature']['Metric']['Value']
            infoWeather['nomeLocal'] = nomeLocal
            return infoWeather
        except:
            return None

def get5D(codigoLocal): #pega previsão de 5 dias
            
    DailyAPIUrl = "http://dataservice.accuweather.com/forecasts/v1/daily/5day/" + codigoLocal + "?apikey=" + accuweatherAPIKEY + "&language=pt-br&metric=true"

    r = requests.get(DailyAPIUrl)
    if (r.status_code != 200):
        print('\nNão foi obter o clima atual.')
        return None
    else:
        try:
            DailyResponse = json.loads(r.text)
            infoClima5D = []
            for dia in DailyResponse['DailyForecasts']:
                climaDia = {}
                climaDia['max'] = dia['Temperature']['Maximum']['Value']
                climaDia['min'] = dia['Temperature']['Minimum']['Value']
                climaDia['clima'] = dia['Day']['IconPhrase']
                diaSemana = int(date.fromtimestamp(dia['EpochDate']).strftime("%w"))
                climaDia['dia'] = dias_semana[diaSemana]
                infoClima5D.append(climaDia)
            return infoClima5D
        except:
            return None


def mostrarPrevisao(lat, long):
    try:
        local = pegarCodLocal(lat, long)
        weather = getWeather(local['codigoLocal'], local['nomeLocal'])
        print('Clima atual em: ' + weather['nomeLocal'])
        print(weather['weather'])
        print('Temperatura: '+ str(weather['temp']) + "\xb0" + "C")
    except:
        print("\nErro ao obter o clima atual")

   
    opcao = input('\nDeseja ver a previsão dos próximos dias? (s ou n): ').lower()
    
    if opcao == "s":
        
        print("\nClima para hoje e para os próximos dias")
        print("\n")
        try:
            
            previsao5D = get5D(local['codigoLocal'])
            for dia in previsao5D:
                print(dia['dia'])
                print("Mínima: " +str(dia['min'])+ "\xb0" + "C")
                print("Máxima: " +str(dia['max'])+ "\xb0" + "C")
                print("Clima: " + dia['clima'])
                print("\n")
        except:
            print("Erro ao obter a previsão dos próximos dias")


def pesquisarLocal (local):
    _local = urllib.parse.quote(local)
    mapboxGeocodeUrl = "https://api.mapbox.com/geocoding/v5/mapbox.places/"+ _local +".json?access_token=" + mapboxToken
    
    r = requests.get(mapboxGeocodeUrl)
    if (r.status_code != 200):
        print('Não foi obter o clima atual.')
        return None
    else:
        try:
            mapboxResponse = json.loads(r.text)
            coordenadas = {}
            coordenadas['long'] = str(mapboxResponse['features'][0]['geometry']['coordinates'][0])
            coordenadas['lat'] = str(mapboxResponse['features'][0]['geometry']['coordinates'][1])
            return coordenadas
        except:
            print("Error")


#Start

try:
    
    coordenadas =  pegarCoordenadas()
    mostrarPrevisao(coordenadas['lat'], coordenadas['long'])

    continuar = "s"

    while continuar == "s":
        continuar = input ("\nDeseja consultar a previsão de outro local? (s ou n): ").lower()
        
        if continuar != "s":
            break
        
        local = input("\nDigite a Cidade e o Estado: ")
         
        try:
            print("\n")
            coordenadas = pesquisarLocal(local)
            mostrarPrevisao(coordenadas['lat'],coordenadas['long'])
        
        except:
            print("Não foi possível obter a previsão para esse local.")
  
except: 
    print("Error")    
