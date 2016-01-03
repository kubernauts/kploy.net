# Deployment

Environment is Google Cloud Platform, using [Google Container Engine](https://cloud.google.com/container-engine/) (GKE) to provide for a Kubernetes cluster. To interact with the Kubernetes cluster, [Google Cloud Shell](https://cloud.google.com/cloud-shell/docs/) is used.

## Ramp up the K8S cluster

    $ gcloud config set compute/zone europe-west1-d
    $ gcloud container clusters create kploy-net --num-nodes 1 --machine-type g1-small
    $ gcloud compute instances list

## Set up kploy.net

Note that because we're deploying kploy.net on GCP, the [app credentials](https://developers.google.com/identity/protocols/application-default-credentials) are available directly via the kploy.net service account.

Note: need to explicitly handle `https://www.googleapis.com/auth/devstorage.read_write` scope as of https://cloud.google.com/compute/docs/api/how-tos/authorization in order to upload object into bucket (TBD: ref to source code).

### Manual setup

    $ cd && git clone https://github.com/kubernauts/kploy.net.git && cd kploy.net/deploy
    $ kubectl create -f kploy-net-svc.yaml
    $ kubectl create -f kploy-net-rc.yaml 

### Setup using kploy

    # install kploy: 
    $ git clone https://github.com/kubernauts/kploy.git && cd kploy
    $ sudo python setup.py install && export KPLOY_HOME=${PWD}

The following part TBD after `https` fix for kploy is done:

    # install kploy.net:
    $ cd && git clone https://github.com/kubernauts/kploy.net.git && cd kploy.net
    $ export KPLOY_APISERVER=`kubectl config view -o template --template='{{range .clusters}}{{.cluster.server}}{{end}}'`
    $ sed -i "s@apiserver: http://localhost:8080@apiserver: $KPLOY_APISERVER@" deploy/Kployfile

## Operation

## Tear down the K8S cluster

    $ gcloud container clusters delete kploy-net