import webapp2
from google.appengine.ext import ndb


class NameValuePair(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    name = ndb.StringProperty(indexed=True)
    value = ndb.StringProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)


class GetHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        name_to_search = self.request.get("name")
        name_value_query = NameValuePair.query(NameValuePair.name == name_to_search).order(-NameValuePair.date)
        name_value_pair_query_result = name_value_query.fetch(1)
        name_value_pair = name_value_pair_query_result[0]
        self.response.write(name_value_pair.name + "=" + name_value_pair.value)


class SetHandler(webapp2.RequestHandler):
    def get(self):
        name = self.request.get("name")
        value = self.request.get("value")
        name_value_pair = NameValuePair()
        name_value_pair.name = name
        name_value_pair.value = value
        name_value_pair.put()
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(name + '=' + value)


app = webapp2.WSGIApplication([
    ('/get', GetHandler),
    ('/set', SetHandler)
], debug=True)
