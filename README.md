# kploy.net

This is the [kploy](http://kubernetes.sh/kploy/) application registry service. It is using [Google Cloud Storage](https://cloud.google.com/storage/docs) for the persistency layer.

## API

- `/api/v1`
- `/api/v1/app`
- `/api/v1/app/$APP_UUID`

## Dependencies

- [google-api-python-client](https://github.com/google/google-api-python-client)
- [Tornado](http://www.tornadoweb.org/en/stable/)
- [Requests](http://docs.python-requests.org/en/latest/)

