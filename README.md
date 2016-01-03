# kploy.net

This is the [kploy](http://kubernetes.sh/kploy/) application registry (KAR), serving at [registry.kploy.net](http://registry.kploy.net/), 
enabling you to store and retrieve kploy application archives. KAR itself is a Kubernetes application—see the also the [deploy](deploy/) folder—using [Google Cloud Storage](https://cloud.google.com/storage/docs) for the persistency layer.

## API

The base URL for below API calls is http://registry.kploy.net/ for the KAR. If you deploy it yourself, you need to change this.

Note that the API uses the concept of workspaces for app archives. If the query parameter `workspace` is present in an API call,
for example `?workspace=http://example.org/some/path` then the derived workspace would be `example.org/some/path/`.
If the workspace is missing or is not valid (that is, a URL with at least hostname and path component) then the global workspace 
`global/` is used, instead.

### KAR Status

A `GET` on `/api/v1` returns a JSON object, reporting on the global KAR status.

### Upload app archive

A `POST` to `/api/v1/app` uploads the HTTP body as an app archive into the workspace and
returns a JSON object informing about the outcome of the operation:

    $ http POST http://registry.kploy.net/api/v1/app < test/app.kploy
    HTTP/1.1 200 OK
    Content-Length: 203
    Content-Type: application/json
    Date: Sun, 03 Jan 2016 18:16:53 GMT
    Server: TornadoServer/4.3

    {
        "app_archive_id": "328ebadef2f23d30bf9f806d4eb67c56e2869f471ca34f18780c7ce31576021d",
        "selfLink": "http://registry.kploy.net/api/v1/app/328ebadef2f23d30bf9f806d4eb67c56e2869f471ca34f18780c7ce31576021d"
    }

With workspace explicitly set:

    http POST http://registry.kploy.net/api/v1/app?workspace=http://github.com/kubernauts/kploy.net < test/app.kploy

### List app archives

A `GET` on `/api/v1/app` returns a JSON object, listing the app archives in the workspace.

    $ http http://registry.kploy.net/api/v1/app
    HTTP/1.1 200 OK
    Content-Length: 105
    Content-Type: application/json
    Date: Sun, 03 Jan 2016 18:17:26 GMT
    Etag: "a460a3c55f5efed73046255540c07a3729e1feeb"
    Server: TornadoServer/4.3

    [
        {
            "name": "global/328ebadef2f23d30bf9f806d4eb67c56e2869f471ca34f18780c7ce31576021d.zip",
            "size": "4952"
        }
    ]

With workspace explicitly set:

    http http://registry.kploy.net/api/v1/app?workspace=http://github.com/kubernauts/kploy.net
    HTTP/1.1 200 OK
    Content-Length: 130
    Content-Type: application/json
    Date: Sun, 03 Jan 2016 18:21:26 GMT
    Etag: "baed5d0034d34e55a3088154a36ee698392bc7bf"
    Server: TornadoServer/4.3

    [
        {
            "name": "github.com/kubernauts/kploy.net/328ebadef2f23d30bf9f806d4eb67c56e2869f471ca34f18780c7ce31576021d.zip",
            "size": "4952"
        }
    ]

### Download app archive

A `GET` on `/api/v1/app/$APP_UUID` will download the app archive from the workspace:

    $ http http://registry.kploy.net/api/v1/app/328ebadef2f23d30bf9f806d4eb67c56e2869f471ca34f18780c7ce31576021d
    HTTP/1.1 200 OK
    Content-Length: 4952
    Content-Type: application/octet-stream
    Date: Sun, 03 Jan 2016 18:18:29 GMT
    Etag: "e222fb53177e19ad3d8ffcf5d3e9264f37e94ad9"
    Server: TornadoServer/4.3



    +-----------------------------------------+
    | NOTE: binary data not shown in terminal |
    +-----------------------------------------+

With workspace explicitly set:

    $ http http://registry.kploy.net/api/v1/app/328ebadef2f23d30bf9f806d4eb67c56e2869f471ca34f18780c7ce31576021d?workspace=http://github.com/kubernauts/kploy.net

## Dependencies

- [google-api-python-client](https://github.com/google/google-api-python-client)
- [Tornado](http://www.tornadoweb.org/en/stable/)

