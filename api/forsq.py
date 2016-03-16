import httplib2
import json
#from map import Maps

#forsqure keys
fsid = "P0ZAGLGKKXLD50RFY4AKJHWPPIL5NJWNVE1UHOJCGKZHLFUB"
fsSecret = "FLLJ2TP3SKNSJQYGBSVURTTXCXJQCLVBGH3NUOMRY20ZXBIE"



class forsqure:

	def findAResturant(mealType, geoloc):
		#geoloc = Maps.getGeocodeLocation(location)
		url = ("https://api.foursquare.com/v2/venues/search?client_id=%s&client_secret=%s&v=20120609&ll=%s,%s&query=%s"%(fsid, fsSecret,geoloc['lat'],geoloc['lng'],mealType))
		h = httplib2.Http()
		response, content = h.request(url, 'GET')
		result = json.loads(content)
		return result

	#test code
	#print findAResturant('pizza', 'Chaguanas')