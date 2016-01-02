# Deployment

Environment is Google Cloud Platform, using [Google Container Engine](https://cloud.google.com/container-engine/) (GKE) to provide for a Kubernetes cluster. To interact with the Kubernetes cluster, [Google Cloud Shell](https://cloud.google.com/cloud-shell/docs/) is used.

## Ramp up

    $ gcloud config set compute/zone europe-west1-d
    $ gcloud container clusters create kploy-net --num-nodes 1 --machine-type g1-small
    $ gcloud compute instances list

## Testing

TBD: create RC and SVC manually

    $ kubectl run kar --image=mhausenblas/kploy.net
    $ kubectl expose rc kar --port=80 --target-port=9876 --load-balancer-ip=""

## Production

TBD, via kploy

## Tear down

    $ gcloud container clusters delete kploy-net