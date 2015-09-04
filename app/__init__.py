import cherrypy
import os
import json
from mako import exceptions
from mako.lookup import TemplateLookup
from app.pipe import Pipe as Pipe

path = os.path.dirname(os.path.realpath(__file__))
print(path)
lookup = TemplateLookup(directories=['%s/html' % path])
print(lookup)


class Root(object):
    exposed = True

    def GET(self, **kwargs):
        kwargs['Title'] = 'Home'
        tmpl = lookup.get_template("index.html")
        try:
            return tmpl.render(**kwargs)
        except:
            return exceptions.html_error_template().render()


class Data(object):
    exposed = True

    def __init__(self):
        self.pipe = Pipe()

    def getSliders(self):
        sliders = self.pipe.select['table_sliders']
        for slider in sliders:
            slider['init'] = str(slider['init'])
        print(sliders)
        return sliders

    def getTable(self, **kwargs):
        return self.pipe.getDataTable(**kwargs)

    def serializeJSON(self, data):
        # TODO search for all unserializable
        # objects rather than specific
        for item in data:
            item['expr'] = str(item['expr'])
            item['expr_next'] = str(item['expr_next'])
            item['expr_diff'] = str(item['expr_diff'])

        return data

    def GET(self, **kwargs):
        kwargs['Title'] = "Data"
        tmpl = lookup.get_template("table.html")
        table = self.getTable()
        kwargs['data'] = table
        kwargs['sliders'] = self.getSliders()
        print(table)
        try:
            return tmpl.render(**kwargs)
        except:
            return exceptions.html_error_template().render()

    def POST(self, method='data_table', **kwargs):
        for item in kwargs:
                print('%s\t%s' % (item, kwargs[item]))

        if method == 'data_table':
            table = self.getTable(limit=5)

            table = self.serializeJSON(table)

            ret = dict()
            ret['data'] = table
            ret['recordsTotal'] = len(ret['data'])
            ret['recordsFiltered'] = ret['recordsTotal']

            return json.dumps(ret)
        elif method == 'sliders':
            ranges = dict()
            for slider in self.getSliders():
                if '%s[]' % slider['column'] in kwargs:
                    key = slider['column']
                    translated = self.pipe.select['translate'][key]
                    slider_data = kwargs.pop('%s[]' % key)
                    ranges[translated] = {'min': slider_data[0],
                                          'max': slider_data[1]}
            # limit = None
            # if 'limit' in kwargs:
            #     limit = kwargs['limit']
            kwargs['ranges'] = ranges
            print('kwargs from request')
            print()
            print('kwargs from request: ' + str(kwargs))
            new_data = self.pipe.getDataTable(**kwargs)
            # print('new_data: %s' % new_data)
            return json.dumps(self.serializeJSON(new_data))


class Gene(object):
    exposed = True

    def GET(self, id=None, **kwargs):
        if id is None:
            return 'No id given'
        else:
            if not isinstance(id, int):
                try:
                    id = int(id)
                except ValueError as e:
                    print(e)
                    # TODO return proper error message
                    return 'invalid id given'
            pipe = Pipe()
            tmpl = lookup.get_template("data.html")
            data = pipe.getGene(id)
            data['Title'] = data['geneName']
            print(data)
            """data = dict()
         data['geneName'] = 'GRHL1'
         data['geneID'] = 'ENSMUSG00000020656.11'
         data['geneID_human'] = 'ENSG00000134317'
         data['geneID_mouse'] = 'ENSMUSG00000020656'
         data['cellType'] = 'Astrocyte'
         data['expr'] = 36.2531
         data['expr_next'] = 6.5397
         data['Title'] = data['geneName']"""
            try:
                return tmpl.render(**data)
            except:
                return exceptions.html_error_template().render()


class Search(object):
    exposed = True

    def GET(self, query=None, **kwargs):
        tmpl = lookup.get_template("search.html")
        kwargs['Title'] = 'Search'
        if query is not None:
            kwargs['geneID'] = Pipe().search_like(query)[0]
        return tmpl.render(**kwargs)

cherrypy.config.update({'tools.staticdir.root': path})
# cherrypy.config.update('%s/global.conf' % path)
cherrypy.tree.mount(Gene(), '/gene', config='%s/gene.conf' % path)
cherrypy.tree.mount(Data(), '/data', config='%s/data.conf' % path)
cherrypy.tree.mount(Data(), '/table', config='%s/data.conf' % path)
cherrypy.tree.mount(Search(), '/search', config='%s/search.conf' % path)
cherrypy.tree.mount(Root(), '/', config='%s/root.conf' % path)
for app in [v[1] for v in cherrypy.tree.apps.items()]:
    app.merge('%s/apps.conf' % path)
