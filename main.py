import webapp2


class GetHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World! ' + self.request.get("name"))


app = webapp2.WSGIApplication([
    ('/get', GetHandler),
], debug=True)
