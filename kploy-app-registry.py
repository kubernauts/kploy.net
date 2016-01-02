#!/usr/bin/env python

"""
The kploy application registry service powering kploy.net, 
using Google Cloud Storage https://cloud.google.com/storage/docs
for the persistency layer.

@author: Michael Hausenblas, http://mhausenblas.info/#i
@since: 2016-01-02
@status: init
"""

import logging
import os
import hashlib
import argparse
import json
import tornado.ioloop
import tornado.web

from apiclient import discovery
from oauth2client.client import GoogleCredentials


DEBUG = False    # you can change that to enable debug messages ...

DOWNLOAD_BUFFER_SIZE = 4096
KPLOY_GCS_BUCKET = "kploy.net"
TEMP_APPARCHIVE_DIR = "app_cache/"

if DEBUG:
  FORMAT = "%(asctime)-0s %(levelname)s %(message)s [at line %(lineno)d]"
  logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt="%Y-%m-%dT%I:%M:%S")
else:
  FORMAT = "%(asctime)-0s %(message)s"
  logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt="%Y-%m-%dT%I:%M:%S")


class GCSProxy(object):
    def list_apps(self):
        """
        List app archives stored in the kploy.net bucket on GCS.
        """
        credentials = GoogleCredentials.get_application_default()
        service = discovery.build("storage", "v1", credentials=credentials)
        req = service.buckets().get(bucket=KPLOY_GCS_BUCKET)
        resp = req.execute()
        return resp

    def store_app(self, app_archive_filename):
        """
        Stored an app archive in the kploy.net bucket on GCS.
        """
        credentials = GoogleCredentials.get_application_default()
        service = discovery.build('storage', 'v1', credentials=credentials)
        req = service.objects().insert(media_body=os.path.join(TEMP_APPARCHIVE_DIR, app_archive_filename), name=app_archive_filename, bucket=KPLOY_GCS_BUCKET)
        resp = req.execute()
        return resp

class TopLevelHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Nothing to see here. The API is at <a href='/api/v1/'>/api/v1/</a>")

class V1APIHandlerPush(tornado.web.RequestHandler):
    def post(self):
        """
        Handle app archive uploads via `/api/v1/push` endpoint.
        """
        h = hashlib.sha256()
        h.update(self.request.body)
        app_uuid = h.hexdigest()
        tmp_app_archive_filename = os.path.join(TEMP_APPARCHIVE_DIR, app_uuid)
        tmp_app_archive_filename = "".join([tmp_app_archive_filename, ".zip"])
        with open(tmp_app_archive_filename, "w") as app_archive_file:
            app_archive_file.write(self.request.body)
        gcsp = GCSProxy()
        gcsp.store_app("".join([app_uuid, ".zip"]))
        # todo: check if successful before removing the temp app archive
        os.remove(tmp_app_archive_filename)
        self.write("/api/v1/app/%s" %(app_uuid))

class V1APIHandlerApps(tornado.web.RequestHandler):
    def get(self, app_uuid):
        """
        Handle app archive downloads via `/api/v1/app/$APP_UUID` resources.
        """
        if os.path.exists(app_uuid):
            self.set_header("Content-Type", "application/octet-stream")
            with open(app_uuid, "r") as f:
                while True:
                    data = f.read(DOWNLOAD_BUFFER_SIZE)
                    if not data:
                        break
                    self.write(data)
            self.finish()
        else:
            self.set_status(404)

class V1APIHandler(tornado.web.RequestHandler):
    def get(self):
        gcsp = GCSProxy()
        self.write("<p>overall system status: \o/</p>")
        self.write("<p>apps:</p>")
        self.write("<pre>%s</pre>" %(json.dumps(gcsp.list_apps(), indent=2)))

def make_app():
    return tornado.web.Application([
        (r"/", TopLevelHandler),
        (r"/api/v1", V1APIHandler),
        (r"/api/v1/push", V1APIHandlerPush),
        (r"/api/v1/app/(.*)", V1APIHandlerApps)
    ])

if __name__ == "__main__":
    if not os.path.exists(TEMP_APPARCHIVE_DIR):
        os.makedirs(TEMP_APPARCHIVE_DIR)
    app = make_app()
    app.listen(9876)
    tornado.ioloop.IOLoop.current().start()