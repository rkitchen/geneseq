import app
from app.web import cherrypy
import os

path = os.path.dirname(os.path.realpath(__file__))

print(path)


def application(environ, start_response):
    return app.web.application(environ, start_response)

if __name__ == '__main__':

    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080,
    })

    # Run the application using CherryPy's HTTP Web Server
    # cherrypy.quickstart(Root())
    if hasattr(cherrypy.engine, 'block'):
        # 3.1 syntax
        cherrypy.engine.start()
        cherrypy.engine.block()
    else:
        # 3.0 syntax
        cherrypy.server.quickstart()
        cherrypy.engine.start()
