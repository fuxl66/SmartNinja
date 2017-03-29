from google.appengine.ext import ndb

class Allitems(ndb.Model):
    item_name = ndb.StringProperty()
    item_created = ndb.DateTimeProperty(auto_now_add=True)
    item_price = ndb.FloatProperty()
    item_qty = ndb.FloatProperty(default=1)
    item_shop = ndb.StringProperty()
    item_ean = ndb.IntegerProperty(default=0000000000)
    item_select = ndb.BooleanProperty(default=False)
    item_totalprice = ndb.FloatProperty(default=0)