# @author: ivan perez dona (ivan.perez.dona@gmail.com)

import os
clusterName= input("Introduce your cluster name (default 'trainingPath'): ") or "trainingPath"

# Define the commands to be executed
commands = {
    "Part 0: Download the materials": [
        f"mkdir {clusterName}",
        f"cd {clusterName}",
        "git clone https://github.com/huzmgod/k8sTraining.git",
        "mv k8sTraining/* .",
        "rm -rf k8sTraining"
    ],
    
    "Part 1: Apache and nginx": [
        f"kind create cluster --name={clusterName} --config=cluster-config.yaml",
        "kubectl apply -k .",
    ],
    "Part 2: Deploying the dashboard": [
        "kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml --validate=false",
        "kubectl apply -f jenkins.yaml",
        # "kubectl get pods -n kubernetes-dashboard",
        "kubectl create serviceaccount -n kubernetes-dashboard admin-user",
        "kubectl create clusterrolebinding -n kubernetes-dashboard admin-user --clusterrole cluster-admin --serviceaccount=kubernetes-dashboard:admin-user",
        # Get the token manually
        # "token=$(kubectl -n kubernetes-dashboard describe secret $(kubectl -n kubernetes-dashboard get secret | awk '/^admin-user/{print $1}') | awk '$1==\"token:\"{print $2}')",
        # "echo $token",
        # Enter manually to see the dashboard
        # "kubectl proxy",
        # Use a browser to access the dashboard
        # "firefox http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/#/login",
    ],
    "Part 3: Deploying Istio": [
        
        "curl -L https://istio.io/downloadIstio | sh -",
        #TODO: Check if the version is the same. If not, change the following line accordingly
        "cd istio-1.17.1",
        "export PATH=$PWD/bin:$PATH",
        # Execute manually
        # "kubectl get crds | grep 'istio.io\|certmanager.k8s.io' | wc -l",
        "istioctl install --set profile=default",
        "kubectl label namespace default istio-injection=enabled",
        "kubectl apply -f loadBalancernginx.yaml",
        "export INGRESS_NAME=istio-ingressgateway",
        "export INGRESS_NS=istio-system",
        "export INGRESS_HOST=127.0.0.1",
        # check manually
        # kubectl get svc -n istio-system
        # echo "INGRESS_HOST=$INGRESS_HOST, INGRESS_PORT=$INGRESS_PORT
        "export GATEWAY_URL=$INGRESS_HOST:$INGRESS_PORT", 
       
    ],
    "Part 4: Installing Kiali": [
        "kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.17/samples/addons/kiali.yaml --validate=false",
        # Uncomment the following line to open the dashboard
        #"istioctl dashboard kiali",
    ],
}

# Execute each command group
for title, command_list in commands.items():
    print(f"Executing {title}")
    for command in command_list:
        print(f"Executing: {command}")
        if (command.startswith("cd")):
            os.chdir(command.split(" ")[1])
            print(f"Current directory: {os.getcwd()}")
        elif (command.startswith("export")):
            os.environ[command.split("=")[0].split(" ")[1]] = command.split("=")[1]
            # print(f"Current environment: {os.environ}")
        else:
            os.system(command)
