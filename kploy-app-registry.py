#!/usr/bin/env python

"""
The kploy application registry service powering kploy.net, 
using Google Cloud Storage https://cloud.google.com/storage/docs
for the persistency layer.

@author: Michael Hausenblas, http://mhausenblas.info/#i
@since: 2016-01-02
@status: beta
"""

import logging
import os
import hashlib
import argparse
import json
import tornado.ioloop
import tornado.web

from urlparse import urlparse
from tornado.escape import json_encode
from apiclient import discovery
from oauth2client.client import GoogleCredentials


DEBUG = False

KAR_PORT =  9876
DOWNLOAD_BUFFER_SIZE = 4096
KPLOY_GCS_BUCKET = "kploy.net"
TEMP_APPARCHIVE_DIR = "app_cache/"
GLOBAL_WORKSPACE = "global"

if DEBUG:
  FORMAT = "%(asctime)-0s %(levelname)s %(message)s [at line %(lineno)d]"
  logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt="%Y-%m-%dT%I:%M:%S")
else:
  FORMAT = "%(asctime)-0s %(message)s"
  logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt="%Y-%m-%dT%I:%M:%S")


class GCSProxy(object):
    def bucket_status(self):
        """
        Retrieves status of kploy.net bucket on GCS.
        """
        credentials = GoogleCredentials.get_application_default()
        service = discovery.build("storage", "v1", credentials=credentials)
        req = service.buckets().get(bucket=KPLOY_GCS_BUCKET)
        resp = req.execute()
        return resp

    def list_apps(self, workspace):
        """
        List app archives stored in the kploy.net bucket on GCS.
        """
        credentials = GoogleCredentials.get_application_default()
        service = discovery.build("storage", "v1", credentials=credentials)
        req = service.objects().list(bucket=KPLOY_GCS_BUCKET, prefix=workspace, fields="items(name,size)")
        apps = req.execute()
        return apps

    def get_app(self, workspace, app_archive_filename):
        """
        Retrieves an app archive stored in the kploy.net bucket on GCS.
        """
        credentials = GoogleCredentials.get_application_default()
        service = discovery.build("storage", "v1", credentials=credentials)
        req = service.objects().get_media(bucket=KPLOY_GCS_BUCKET, object="".join([workspace, app_archive_filename]))
        return req.execute()

    def store_app(self, workspace, app_archive_filename):
        """
        Stores an app archive in a workspace of the kploy.net bucket on GCS.
        """
        credentials = GoogleCredentials.get_application_default()
        service = discovery.build("storage", "v1", credentials=credentials)
        req = service.objects().insert(
            media_body=os.path.join(TEMP_APPARCHIVE_DIR, app_archive_filename),
            name="".join([workspace, app_archive_filename]),
            bucket=KPLOY_GCS_BUCKET)
        resp = req.execute()
        return resp

class TopLevelHandler(tornado.web.RequestHandler):
    def get(self):
        """
        Handle top-level resource.
        """
        self.write("Nothing to see here. The API is at <a href='/api/v1'>/api/v1</a>")

class V1APIHandlerUploadApp(tornado.web.RequestHandler):
    def get(self):
        """
        Handle app archive listing via `/api/v1/app` endpoint.
        """
        # get workspace from URL query part:
        query_arg = self.get_query_argument(name="workspace", default=GLOBAL_WORKSPACE, strip=True)
        workspace = _extract_workspace(query_arg)
        
        gcsp = GCSProxy()
        apps = gcsp.list_apps(workspace)
        self.set_header("Content-Type", "application/json")
        if "items" in apps:
            self.write(json_encode(apps["items"]))
        else: 
            self.write(json_encode(apps))
            
    def post(self):
        """
        Handle app archive uploads via `/api/v1/app` endpoint.
        """
        # get workspace from URL query part:
        query_arg = self.get_query_argument(name="workspace", default=GLOBAL_WORKSPACE, strip=True)
        workspace = _extract_workspace(query_arg)
        
        # we generate the ID of the object that contains the app archive from a
        # SHA256 hash of its content; this is an associative content addressing
        # resulting in same app archives being stored under the same ID, 
        # in the context of the workspace):
        h = hashlib.sha256()
        h.update(self.request.body)
        app_uuid = h.hexdigest()
        
        # storing the app archive temporary in the local app cache before upload to Cloud Storage:
        tmp_app_archive_filename = os.path.join(TEMP_APPARCHIVE_DIR, app_uuid)
        tmp_app_archive_filename = "".join([tmp_app_archive_filename, ".zip"])
        with open(tmp_app_archive_filename, "w") as app_archive_file:
            app_archive_file.write(self.request.body)
        gcsp = GCSProxy()
        resp = gcsp.store_app(workspace, "".join([app_uuid, ".zip"]))
        logging.debug("App archive GCS result: %s" %(json.dumps(resp, indent=2)))
        
        # remove the temp app archive if upload is successful
        if resp["id"]:
            os.remove(tmp_app_archive_filename)
        self.set_header("Content-Type", "application/json")
        
        app = { 
            "app_archive_id" : app_uuid, 
            "selfLink"       : "".join([self.request.protocol, "://", self.request.host, "/api/v1/app/", app_uuid]) 
        }
        logging.debug("App archive upload: %s" %(json.dumps(app, indent=2)))
        self.write(json_encode(app))

class V1APIHandlerApps(tornado.web.RequestHandler):
    def get(self, app_uuid):
        """
        Handle app archive downloads via `/api/v1/app/$APP_UUID` resources.
        """
        # get workspace from URL query part:
        query_arg = self.get_query_argument(name="workspace", default=GLOBAL_WORKSPACE, strip=True)
        workspace = _extract_workspace(query_arg)
        
        gcsp = GCSProxy()
        app_name = "".join([app_uuid, ".zip"])
        try:
            content = gcsp.get_app(workspace, app_name)
            if content:
                self.set_header("Content-Type", "application/octet-stream")
                self.write(content)
                self.finish()
            else:
                self.set_status(404)
        except:
            self.set_status(404)

class V1APIHandler(tornado.web.RequestHandler):
    def get(self):
        """
        Handle API status via `/api/v1` resource.
        """
        gcsp = GCSProxy()
        self.set_header("Content-Type", "application/json")
        self.write(json_encode(gcsp.bucket_status()))

def _extract_workspace(query_arg):
    """
    Extracts the workspace from the URL's query part, e.g.: `/api/v1/app?workspace=xxx`
    The workspace is the prefix, or also the virtual top-level directory, in the kploy.net 
    bucket that will be used for this app archive.
    """
    workspace = ""
    components = urlparse(query_arg)
    if components.hostname and components.path:
        workspace = "".join([components.hostname, components.path])
    else:
        workspace = GLOBAL_WORKSPACE
    if not workspace.endswith("/"):
        workspace = "".join([workspace, "/"])
    logging.info("Workspace: %s" %(workspace))
    return workspace

def _make_app():
    """
    Set up the API handler.
    """
    return tornado.web.Application([
        (r"/", TopLevelHandler),
        (r"/api/v1", V1APIHandler),
        (r"/api/v1/app", V1APIHandlerUploadApp),
        (r"/api/v1/app/(.*)", V1APIHandlerApps)
    ])

if __name__ == "__main__":
    if not os.path.exists(TEMP_APPARCHIVE_DIR):
        os.makedirs(TEMP_APPARCHIVE_DIR)
    app = _make_app()
    app.listen(KAR_PORT)
    tornado.ioloop.IOLoop.current().start()