import webapp2
import logging
from google.appengine.ext import ndb


class NameValuePair(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    value = ndb.StringProperty(indexed=True)


class UndoOperation(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    value_to_undo = ndb.StringProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)


class RedoOperation(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    value_to_redo = ndb.StringProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)


def get_by_name(name_to_search):
    name_value_query = NameValuePair.query(NameValuePair.name == name_to_search)
    name_value_pair_query_result = name_value_query.fetch(1)
    result = None
    if len(name_value_pair_query_result):
        result = name_value_pair_query_result[0]
    return result


class RedoHandler(webapp2.RequestHandler):
    def get(self):
        redo_ops = RedoOperation.query().order(-RedoOperation.date).fetch(1)
        if len(redo_ops):
            redo = redo_ops[0]
            pair = get_by_name(redo.name)
            current_value = pair.value
            pair.value = redo.value_to_redo
            pair.put()
            # Deleting redo
            redo.key.delete()
            # Creating undo
            undo_operation = UndoOperation()
            undo_operation.name = pair.name
            undo_operation.value_to_undo = current_value
            undo_operation.put()
            self.response.write(pair.name + ' = ' + (pair.value or 'None'))
        else:
            self.response.write('NO COMMANDS')


class UndoHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        undo_ops = UndoOperation.query().order(-UndoOperation.date).fetch(1)
        if len(undo_ops):
            undo = undo_ops[0]
            pair = get_by_name(undo.name)
            current_value = pair.value
            pair.value = undo.value_to_undo
            pair.put()
            # Deleting undo
            undo.key.delete()
            # Creating redo
            redo_operation = RedoOperation()
            redo_operation.name = pair.name
            redo_operation.value_to_redo = current_value
            redo_operation.put()
            self.response.write(pair.name + ' = ' + (pair.value or 'None'))
        else:
            self.response.write('NO COMMANDS')


class EndHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        ndb.delete_multi(NameValuePair.query().fetch(keys_only=True))
        ndb.delete_multi(UndoOperation.query().fetch(keys_only=True))
        ndb.delete_multi(RedoOperation.query().fetch(keys_only=True))
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
        amount = NameValuePair.query(NameValuePair.value == value_to_search).count()
        self.response.write(amount)


class UnsetHandler(webapp2.RequestHandler):
    def get(self):
        name = self.request.get("name")
        name_value_pair = get_by_name(name)
        value_to_undo = name_value_pair.value
        name_value_pair.value = None
        name_value_pair.put()
        # Saving (more like pushing into stuck) undo operation
        undo_operation = UndoOperation()
        undo_operation.name = name
        undo_operation.value_to_undo = value_to_undo
        undo_operation.put()
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(name + ' = None')


class GetHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        name_to_search = self.request.get("name")
        name_value_pair = get_by_name(name_to_search)
        if name_value_pair:
            self.response.write(name_value_pair.value or 'None')
        else:
            self.response.write("Not found")


class SetHandler(webapp2.RequestHandler):
    def get(self):
        name = self.request.get("name")
        value = self.request.get("value")
        name_value_pair = get_by_name(name)
        if name_value_pair is None:
            name_value_pair = NameValuePair()
            name_value_pair.name = name
        value_to_undo = name_value_pair.value
        name_value_pair.value = value
        name_value_pair.put()
        # Saving (more like pushing into stuck) undo operation
        undo_operation = UndoOperation()
        undo_operation.name = name
        undo_operation.value_to_undo = value_to_undo
        undo_operation.put()
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(name + ' = ' + value)


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
