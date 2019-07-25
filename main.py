import webapp2
from google.appengine.ext import ndb

LAST = 'last'
PREV = 'prev'


class NameValuePair(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    value = ndb.StringProperty(indexed=True)
    status = ndb.StringProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)


def get_by_name(name_to_search, status_to_search):
    name_value_query = NameValuePair.query(
        ndb.AND(NameValuePair.name == name_to_search, NameValuePair.status == status_to_search)).order(
        -NameValuePair.date)
    name_value_pair_query_result = name_value_query.fetch(1)
    return name_value_pair_query_result


class RedoHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        name_value_query = NameValuePair.query(NameValuePair.status == LAST).order(-NameValuePair.date)
        name_value_pair_query_result = name_value_query.fetch(1)
        if len(name_value_pair_query_result):

            current_value = name_value_pair_query_result[0]
            prev_value_result = NameValuePair.query(NameValuePair.date > current_value.date).order(
                -NameValuePair.date).fetch(1)
            if len(prev_value_result):
                prev_value = prev_value_result[0]
                current_value.status = PREV
                current_value.put()
                prev_value.status = LAST
                prev_value.put()
                self.response.write(prev_value.name + "=" + (prev_value.value or 'None'))
            else:
                self.response.write("NO COMMANDS")
        else:
            self.response.write("NO COMMANDS")


class UndoHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        name_value_query = NameValuePair.query(NameValuePair.status == LAST).order(-NameValuePair.date)
        name_value_pair_query_result = name_value_query.fetch(1)
        if len(name_value_pair_query_result):

            current_value = name_value_pair_query_result[0]
            prev_value_result = NameValuePair.query(NameValuePair.date < current_value.date).order(
                -NameValuePair.date).fetch(1)
            if len(prev_value_result):
                prev_value = prev_value_result[0]
                current_value.status = PREV
                current_value.put()
                prev_value.status = LAST
                prev_value.put()
                self.response.write(prev_value.name + "=" + (prev_value.value or 'None'))
            else:
                self.response.write("NO COMMANDS")
        else:
            self.response.write("NO COMMANDS")


class EndHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        ndb.delete_multi(NameValuePair.query().fetch(keys_only=True))
        self.response.write('CLEANED')


class ShowAllHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        all_rows = NameValuePair.query().fetch()
        self.response.write(all_rows)


class NumEqualToHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        value_to_search = self.request.get("value")
        amount = NameValuePair.query(
            ndb.AND(NameValuePair.value == value_to_search, NameValuePair.status == LAST)).count()
        self.response.write(amount)


class UnsetHandler(webapp2.RequestHandler):
    def get(self):
        name = self.request.get("name")
        value = self.request.get("value")
        pair_by_name = get_by_name(name, LAST)
        if len(pair_by_name):
            # Updating last entry
            pair_by_name[0].status = PREV
            pair_by_name[0].put()
        name_value_pair = NameValuePair()
        name_value_pair.name = name
        name_value_pair.value = None
        name_value_pair.status = LAST
        name_value_pair.put()
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(name_value_pair.name + "=None")


class GetHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        name_to_search = self.request.get("name")
        name_value_pair_query_result = get_by_name(name_to_search, LAST)
        if len(name_value_pair_query_result):
            name_value_pair = name_value_pair_query_result[0]
            self.response.write(name_value_pair.name + "=" + (name_value_pair.value or 'None'))
        else:
            self.response.write("Not found")


class SetHandler(webapp2.RequestHandler):
    def get(self):
        name = self.request.get("name")
        value = self.request.get("value")
        pair_by_name = get_by_name(name, LAST)
        if len(pair_by_name):
            # Updating last entry
            pair_by_name[0].status = PREV
            pair_by_name[0].put()
        name_value_pair = NameValuePair()
        name_value_pair.name = name
        name_value_pair.value = value
        name_value_pair.status = LAST
        name_value_pair.put()
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(name + '=' + value)


app = webapp2.WSGIApplication([
    ('/get', GetHandler),
    ('/set', SetHandler),
    ('/unset', UnsetHandler),
    ('/numequalto', NumEqualToHandler),
    ('/undo', UndoHandler),
    ('/redo', RedoHandler),
    ('/showall', ShowAllHandler),
    ('/end', EndHandler)
], debug=True)
