#!/usr/bin/env python
import os
import jinja2
import webapp2
from models import Allitems

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        self.response.out.write(template.render(params))


class ListHandler(BaseHandler):
    def get(self):
        items = Allitems.query().fetch()
        selected = Allitems.query(Allitems.item_select == True).fetch()
        params = {"items": sorted(items, key=lambda x: x.item_name), "selected": len(selected)}
        return self.render_template("items_all.html", params=params)


class AddHandler(BaseHandler):
    def get(self):
        items = Allitems.query().fetch()
        params = {"items": items}
        return self.render_template("items_all.html", params=params)

    def post(self):
        itemname = self.request.get("item_name")
        itemprice = float(self.request.get("item_price").replace(",", "."))
        itemshop = self.request.get("item_shop")
        itemean = int(self.request.get("item_ean"))

        import re
        findings = re.findall("<(\w+)>", itemname)
        findings2 = re.findall("<(\w+)>", itemshop)
        if findings or findings2:
           pass
        else:
            item = Allitems(item_name=itemname, item_price=itemprice, item_shop=itemshop, item_ean=itemean)
            item.put()
        items = Allitems.query().fetch()
        params = {"items": items}
        return self.render_template("items_all.html", params=params)


class DetailsHandler(BaseHandler):
    def get(self, item_id):
        items = Allitems.get_by_id(int(item_id))
        params = {"items": items}
        return self.render_template("item_detail.html", params=params)


class EditHandler(BaseHandler):
    def get(self, item_id):
        items = Allitems.get_by_id(int(item_id))
        params = {"items": items}
        return self.render_template("item_edit.html", params=params)

    def post(self, item_id):
        newname = self.request.get("item_name")
        newprice = float(self.request.get("item_price").replace(",", "."))
        import re
        findings = re.findall("<(\w+)>", newname)
        if findings:
           pass
        else:
            items = Allitems.get_by_id(int(item_id))
            items.item_name = newname
            items.item_price = newprice
            items.put()
        return self.redirect_to("list")


class MinusHandler(BaseHandler):
    def get(self, item_id):
        items = Allitems.get_by_id(int(item_id))
        params = {"items": items}
        return self.render_template("items_all.html", params=params)

    def post(self, item_id):
        items = Allitems.get_by_id(int(item_id))
        items.item_select = False
        items.item_qty = 1
        items.item_totalprice = 0
        items.put()
        select = Allitems.query(Allitems.item_select == True).fetch()
        params = {"selected": len(select)}
        return self.render_template("items_all.html", params=params)


class PlusHandler(BaseHandler):
    def get(self, item_id):
        items = Allitems.get_by_id(int(item_id))
        params = {"items": items}
        return self.render_template("items_all.html", params=params)

    def post(self, item_id):
        items = Allitems.get_by_id(int(item_id))
        items.item_select = True
        items.item_qty = float(self.request.get(item_id))
        items.item_totalprice = items.item_qty * items.item_price
        items.put()
        select = Allitems.query(Allitems.item_select == True).fetch()
        params = {"selected": len(select)}
        return self.render_template("items_all.html", params=params)


class SelectedHandler(BaseHandler):
    total = 0

    def get(self):
        items = Allitems.query(Allitems.item_select == True).fetch()
        # params = {"items": items, "selected": len(items)}
        params = {"items": sorted(items, key=lambda x: x.item_name), "selected": len(items)}
        return self.render_template("items_selected.html", params=params)

    def post(self, item_id):
        items = Allitems.get_by_id(int(item_id))
        items.item_totalprice = items.item_price * items.item_qty
        items.put()
        for prices in items:
            total = total + prices.item_totalprice
        params = {"items": items, "total": round(total, 2)}
        return self.render_template("items_selected.html", params=params)


class DeleteHandler(BaseHandler):
    def get(self, item_id):
        items = Allitems.get_by_id(int(item_id))
        selected = Allitems.query(Allitems.item_select == True).fetch()
        params = {"items": items, "selected": len(selected)}
        return self.render_template("items_delete.html", params=params)

    def post(self, item_id):
        items = Allitems.get_by_id(int(item_id))
        items.key.delete()
        return self.redirect_to("list")


app = webapp2.WSGIApplication([
    webapp2.Route('/', ListHandler, name="list"),
    webapp2.Route('/<item_id:\d+>', DetailsHandler),
    webapp2.Route('/<item_id:\d+>/edit', EditHandler),
    webapp2.Route('/<item_id:\d+>/minus', MinusHandler),
    webapp2.Route('/<item_id:\d+>/plus', PlusHandler),
    webapp2.Route('/<item_id:\d+>/delete', DeleteHandler),
    webapp2.Route('/add', AddHandler),
    webapp2.Route('/selected', SelectedHandler),
], debug=True)
