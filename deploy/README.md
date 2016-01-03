# Deployment

Environment is Google Cloud Platform, using [Google Container Engine](https://cloud.google.com/container-engine/) (GKE) to provide for a Kubernetes cluster. To interact with the Kubernetes cluster, [Google Cloud Shell](https://cloud.google.com/cloud-shell/docs/) is used.

## Ramp up the K8S cluster

    $ gcloud config set compute/zone europe-west1-d
    $ gcloud container clusters create kploy-net --scopes storage-rw --num-nodes 1 --machine-type g1-small
    $ gcloud compute instances list

Note: per [default](https://cloud.google.com/sdk/gcloud/reference/container/clusters/create) the GKE cluster is created with a scope `compute-rw, storage-ro`, which is not sufficient if one wants to write to Cloud Storage from a container. Hence, above the `--scopes storage-rw` addition.


## Set up kploy.net

Note that because we're deploying kploy.net on GCP, the [app credentials](https://developers.google.com/identity/protocols/application-default-credentials) are available directly via the kploy.net service account.

### Manual setup

    $ cd && git clone https://github.com/kubernauts/kploy.net.git && cd kploy.net/deploy
    $ kubectl create -f kploy-net-svc.yaml
    $ kubectl create -f kploy-net-rc.yaml 

### WIP: Setup using kploy

    # install kploy: 
    $ git clone https://github.com/kubernauts/kploy.git && cd kploy
    $ sudo python setup.py install && export KPLOY_HOME=${PWD}

The following part TBD after `https` fix for kploy is done:

    # install kploy.net:
    $ cd && git clone https://github.com/kubernauts/kploy.net.git && cd kploy.net
    $ export KPLOY_APISERVER=`kubectl config view -o template --template='{{range .clusters}}{{.cluster.server}}{{end}}'`
    $ sed -i "s@apiserver: http://localhost:8080@apiserver: $KPLOY_APISERVER@" deploy/Kployfile

## Tear down the K8S cluster

    $ gcloud container clusters delete kploy-net