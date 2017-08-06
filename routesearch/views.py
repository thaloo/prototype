from django.shortcuts import render
from django.shortcuts import render_to_response
from django.shortcuts import HttpResponse
import csv
import os.path
import codecs
from urllib.request import urlopen
from urllib.request import Request
from urllib.request import urlretrieve
from urllib.parse import quote
from bs4 import BeautifulSoup
from xml.dom import minidom
from collections import defaultdict

class Airport:
    def __init__(self, name, code, region):
        self.name = name
        self.code = code
        self.region = region
    @property
    def getName(self):
        return self.name

    @property
    def getCode(self):
        return self.code

    @property
    def getRegion(self):
        return self.code


def getUrl(s, d, date, people_number):
    return "https://www.google.com/flights/?f=0&gl#search;f="+quote(str(s))+";t="+quote(str(d))+";d="+date+";tt=o"+";px="+people_number

def getCityData(query):
    try:
        url = 'https://maps.googleapis.com/maps/api/geocode/xml?address='+quote(query)
        request = Request(url)
        request.add_header('Accept-Encoding', 'utf-8')

        response = urlopen(request)
        contents = response.read()

        xml_raw = minidom.parseString(contents)

        address_raw = quote(xml_raw.getElementsByTagName("formatted_address")[0].firstChild.data)
        address = address_raw.split('%2C%20')

        return [address[0].replace('%20',' '), address[len(address)-1].replace('%20', ' ')]
    except:
        return None

def getAirport(query):
    if query is None:
        return None
    f = codecs.open(os.path.dirname(os.path.realpath(__file__))+"/airports.dat","r","utf-8")
    lines = f.readlines()
    airport_info = defaultdict(list)
    for line in lines:
        temp = quote(line).split('%2C')

        name = temp[1].replace("%22","").replace("%20"," ")
        code = temp[4].replace("%22","")
        region = temp[2].replace("%22","").replace("%20"," ")

        if code != "%5CN":
            airport_info[region].append(Airport(name,code,region))
    f.close()
    if len(airport_info[query]) != 0:
        return airport_info[query]
    else:
        if 'city' in query:
            return getAirportCode(query.split(" ")[0])

def index(request):
    return render(request, 'routesearch/index.html', {})

def result(request):
    cities = []
    route = []
    countries = []
    omitted = []

    if 'user_name' in request.GET:
        user_name = request.GET['user_name']
    if 'city' in request.GET:
        cities = request.GET.getlist('city')
    if 'start_date' in request.GET:
        start_date = request.GET['start_date']
    if 'end_date' in request.GET:
        end_date = request.GET['end_date']
    if 'people' in request.GET:
        people_number = request.GET['people']



    for city in cities:
        if city is None:
            continue
        try:
            temp = getCityData(city)
            route.append(temp[0])
            if getCityData(city)[1] not in countries:
                    countries.append(temp[1])
        except:
            omitted.append(city)

    c1 = cities[0]
    c2 = cities[1]
    c3 = cities[len(cities)-2]
    c4 = cities[len(cities)-1]

    if (c1 and c2 and c3 and c4) not in omitted:
        airport1 = getAirport(getCityData(c1)[0])
        airport2 = getAirport(getCityData(c2)[0])
        airport3 = getAirport(getCityData(c3)[0])
        airport4 = getAirport(getCityData(c4)[0])

    return render_to_response('routesearch/result.html',{'user_name':user_name,
                                                        'route':route,
                                                        'start_date':start_date,
                                                        'end_date':end_date,
                                                        'people_number':people_number,
                                                        'airport1':airport1,
                                                        'airport2':airport2,
                                                        'airport3':airport3,
                                                        'airport4':airport4,})
