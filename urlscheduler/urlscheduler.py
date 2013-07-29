import webapp2, urllib2
from google.appengine.api import urlfetch
from google.appengine.ext import db
from datetime import datetime, timedelta

class UrlCall(db.Model):
    link = db.StringProperty()
    date = db.DateTimeProperty()
    expired = db.BooleanProperty()


class AddCall(webapp2.RequestHandler):
    def get(self):
        hours = self.request.get("hours")
        if not hours:
            hours = 0
        link = self.request.get("link")
        if link:
            future = timedelta(hours=int(hours))
            call = UrlCall(link = link, date = datetime.now() + future, expired=False)
            call.put()
            self.response.write('succcess')
        else:
            self.response.write('fail')
            
class LoadUrls(webapp2.RequestHandler):
    def get(self):
        now = datetime.now()
        query = UrlCall.all()
        query.filter('expired =', False)
        for urlcall in query.run():
            if now > urlcall.date:
                try:
                    result = urlfetch.fetch(url=urlcall.link,deadline=600)
                    self.response.write(result.content)
                    urlcall.expired = True
                    urlcall.put()
                except:
                    self.response.write('fail for %s' % urlcall.link)
                    

add_call = webapp2.WSGIApplication([('/add_call', AddCall)],debug=True)
load_urls = webapp2.WSGIApplication([('/load_urls', LoadUrls)],debug=True)
