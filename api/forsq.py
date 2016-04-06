import httplib2
import json
from map import Maps

#forsqure keys
fsid = "P0ZAGLGKKXLD50RFY4AKJHWPPIL5NJWNVE1UHOJCGKZHLFUB"
fsSecret = "FLLJ2TP3SKNSJQYGBSVURTTXCXJQCLVBGH3NUOMRY20ZXBIE"



class forsqure:
	@staticmethod
	def findAResturant(mealType, geoloc):
		geoloc = Maps.getGeocodeLocation(geoloc)
		url = ("https://api.foursquare.com/v2/venues/search?client_id=%s&client_secret=%s&v=20120609&ll=%s,%s&query=%s"%(fsid, fsSecret,geoloc['lat'],geoloc['lng'],mealType))
		h = httplib2.Http()
		response, content = h.request(url, 'GET')
		result = json.loads(content)
		#return result
		if result['response']['venues']:
		#Grab the first restaurant
			restaurant = result['response']['venues'][0]
			venue_id = restaurant['id'] 
			restaurant_name = restaurant['name']
			restaurant_address = restaurant['location']['formattedAddress']
			#Format the Restaurant Address into one string
			address = ""
			for i in restaurant_address:
				address += i + " "
			restaurant_address = address

			#Get a  300x300 picture of the restaurant using the venue_id (you can change this by altering the 300x300 value in the URL or replacing it with 'orginal' to get the original picture
			url = ('https://api.foursquare.com/v2/venues/%s/photos?client_id=%s&v=20150603&client_secret=%s' % ((venue_id,fsid,fsSecret)))
			result = json.loads(h.request(url,'GET')[1])
			#Grab the first image
			#if no image available, insert default image url
			if result['response']['photos']['items']:
				firstpic = result['response']['photos']['items'][0]
				prefix = firstpic['prefix']
				suffix = firstpic['suffix']
				imageURL = prefix + "300x300" + suffix
			else:
				imageURL = "http://runawayapricot.com/wp-content/uploads/2014/09/placeholder.jpg"

			restaurantInfo = {'name':restaurant_name, 'address':restaurant_address, 'image':imageURL}
			#print "Restaurant Name: %s " % restaurantInfo['name']
			#print "Restaurant Address: %s " % restaurantInfo['address']
			#print "Image: %s \n " % restaurantInfo['image']
			return restaurantInfo
		else:
			#print "No Restaurants Found for %s" % location
			return "No Restaurants Found"
	#test code
	#print findAResturant('pizza', 'Chaguanas')
	# eg of output
	#{'image': u'https://irs1.4sqi.net/img/general/300x300/17003726_hz37fr6XDK5qNjpcVxryLSt5tDpxTllqno2aORGxgyA.jpg', 'name': u"Mario's Pizza, Mid Centre Mall", 'address': u'Mid Centre Mall Chaguanas Trinidad and Tobago '}