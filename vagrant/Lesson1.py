from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Restaurant, Base, MenuItem
 
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

engine = create_engine('sqlite:///restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# #Menu for UrbanBurger
# restaurant1 = Restaurant(name = "Urban Burger")
# restaurant2 = Restaurant(name = "Rural Burger")

# session.add(restaurant1)
# session.add(restaurant2)

# session.commit()

# restaurantList = session.query(Restaurant).all()

class WebServerHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		try:
			if self.path.endswith("/restaurants"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				message = ""
				message += "<html><body>"
				message += "<a href = 'restaurants/new'><h2>Make a New Restaurant</h2></a>" + "<br>"
				
				restaurantList = session.query(Restaurant).all()
				for restaurant in restaurantList:
					message += restaurant.name + "<br>"
					message += "<a href = 'restaurants/%d/edit'>Edit</a>" %restaurant.id
					message += "<br>"
					message += "<a href = 'restaurants/%d/remove'>Remove</a>" %restaurant.id
					message += "<br>"
				message += "</body></html>"
				self.wfile.write(message)
				print message
				return  

			if self.path.endswith("/restaurants/new"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				message = ""
				message += "<html><body>"
				message += "<form method = 'POST' enctype = 'multipart/form-data' action = '/restaurants/new'><h2>Make a New Restaurant</h2><input name = 'message' type = 'text'><input type = 'submit' value = 'Submit'> </form>"
				message += "<html><body>"
				self.wfile.write(message)
				print message
				return

			if self.path.endswith("edit"):
				restaurantId = int(self.path.split('restaurants/', 1)[1].split('/edit', 1)[0])
				print restaurantId
				restaurantName = session.query(Restaurant).get(restaurantId).name
				print restaurantName
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				message = ""
				message += "<html><body>"
				message += "<form method = 'POST' enctype = 'multipart/form-data' action = '/restaurants/{}/edit'><h2>{}</h2><input name = 'rename' type = 'text' placeholder = {}><input type = 'submit' value = 'Rename'> </form>".format(restaurantId, restaurantName, restaurantName)
				message += "<html><body>"
				self.wfile.write(message)
				print message
				return

			if self.path.endswith("remove"):
				restaurantId = int(self.path.split('/')[2])
				print restaurantId
				restaurantName = session.query(Restaurant).get(restaurantId).name
				print restaurantName
				if restaurantName != []:
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()
					message = ""
					message += "<html><body>"
					message += "<form method = 'POST' enctype = 'multipart/form-data' action = '/restaurants/{}/remove'><h2>Are you sure you want to delete {}?</h2><input type = 'submit' value = 'Remove'> </form>".format(restaurantId, restaurantName)
					message += "<html><body>"
					self.wfile.write(message)
					print message
				return

			else:
				self.send_error(404, 'File Not Found: %s' % self.path)


		except:
			pass

	def do_POST(self):
		try:
			if self.path.endswith("/restaurants/new"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('message')

				restaurant1 = Restaurant(name = messagecontent[0])
				session.add(restaurant1)
				session.commit()

				self.send_response(301)
				self.send_header('Content-type', 'text/html')
				self.send_header('Location', '/restaurants')
				self.end_headers()
				return

			if self.path.endswith("edit"):
				restaurantId = int(self.path.split('restaurants/', 1)[1].split('/edit', 1)[0])
				restaurantQuery = session.query(Restaurant).get(restaurantId)
				if restaurantQuery != []:
					ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
					if ctype == 'multipart/form-data':
						fields = cgi.parse_multipart(self.rfile, pdict)
						messagecontent = fields.get('rename')

					restaurantQuery.name = messagecontent[0]
					session.add(restaurantQuery)
					session.commit()

					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()
				return

			if self.path.endswith("remove"):
				restaurantId = int(self.path.split('/')[2])
				restaurantQuery = session.query(Restaurant).filter_by(id = restaurantId).one()
				if restaurantQuery != []:
					ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
					if ctype == 'multipart/form-data':
						fields = cgi.parse_multipart(self.rfile, pdict)
						messagecontent = fields.get('rename')

					session.delete(restaurantQuery)
					session.commit()

					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()
				return
		except:
			pass

def main():
  #   for restaurant in restaurantList:
		# print restaurant.name

	try:
		port = 8080
		server = HTTPServer(('', port), WebServerHandler)
		print "Web Server running on port %s" % port
		server.serve_forever()
	except KeyboardInterrupt:
		print " ^C entered, stopping web server...."
		server.socket.close()

if __name__ == '__main__':
	main()