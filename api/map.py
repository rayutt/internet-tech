import httplib2
import json

#google map api key
google_geocode_id = "AIzaSyAvnFnZSiMNLeXX3eGh5kf9NEySf-zjkHY"

class Maps:
	
	@staticmethod
	def getGeocodeLocation(inputString):
		locationString = inputString.replace(" ","+")
		url = ("https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s"%(locationString, google_geocode_id))
		h = httplib2.Http()
		response, content = h.request(url, 'GET')
		result = json.loads(content)
		return result['results'][0]['geometry']['location']

	#test code
	#print getGeocodeLocation('Chaguanas')