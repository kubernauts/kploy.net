# kploy.net

This is the [kploy](http://kubernetes.sh/kploy/) application registry service. It is using [Google Cloud Storage](https://cloud.google.com/storage/docs) for the persistency layer.

## API

- `/api/v1` `[GET]`
- `/api/v1/app` `[GET]` | `[POST]`
- `/api/v1/app/$APP_UUID` `[GET]`

## Dependencies

- [google-api-python-client](https://github.com/google/google-api-python-client)
- [Tornado](http://www.tornadoweb.org/en/stable/)

## To do

- package as Dockerfile
- create GCP service account
- create Autobuild on DockerHub
- deploy as app via kploy
- set up Cloud DNS for kploy.net domain
- add API doc, here
