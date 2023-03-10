#!/bin/bash

read -p "Introduce your cluster name (default 'trainingPath'): " clusterName
clusterName=${clusterName:-"trainingPath"}

# Part 0: Download the materials
mkdir $clusterName
cd $clusterName
git clone https://github.com/huzmgod/k8sTraining.git
mv k8sTraining/* .
rm -rf k8sTraining

# Part 1: Apache and nginx
kind create cluster --name=$clusterName --config=cluster-config.yaml
kubectl apply -k .

# Part 2: Deploying the dashboard
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml --validate=false
kubectl apply -f jenkins.yaml
kubectl create serviceaccount -n kubernetes-dashboard admin-user
kubectl create clusterrolebinding -n kubernetes-dashboard admin-user --clusterrole cluster-admin --serviceaccount=kubernetes-dashboard:admin-user

# Part 3: Deploying Istio
curl -L https://istio.io/downloadIstio | sh -
# Version has to be changed manually
cd istio-1.17.1
export PATH=$PWD/bin:$PATH
istioctl install --set profile=default
# You might have to do this to make gateway work properly as ingress:
kubectl label namespace default istio-injection=enabled
kubectl apply -f loadBalancerNginx.yaml
export INGRESS_NAME=istio-ingressgateway
export INGRESS_NS=istio-system
export INGRESS_HOST=127.0.0.1
# check manually
# kubectl get svc -n istio-system
# echo "INGRESS_HOST=$INGRESS_HOST, INGRESS_PORT=$INGRESS_PORT
export GATEWAY_URL=$INGRESS_HOST:$INGRESS_PORT

# Part 4: Installing Kiali
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.17/samples/addons/kiali.yaml --validate=false
# Uncomment the following line to open the dashboard
# istioctl dashboard kiali
