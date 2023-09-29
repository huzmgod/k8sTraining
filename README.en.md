# k8sTraining

Apache, Nginx, Jenkins, Istio, Kiali (for the moment)

Check**_TrainingPathProject.pdf_**for full readme 😊

To deploy the whole scenario execute:

```bash
./autoDeploy.sh
```

If you'd rather play it slowly, just:

```bash
git clone https://github.com/huzmgod/k8sTraining.git
cd k8sTraining
```

**_-----------------------------------------------------------------------------------------------------------------------_**

**_Spanish Full README (without images, which are in the pdf):_**

**Setting up Nginx as a Reverse Proxy for Apache using K8s. Jenkins, Istio, K8s Dashboard and Kiali deployed**

1.  **Instalar kind:<https://kind.sigs.k8s.io/docs/user/quick-start/#installation>**
2.  **Create cluster configuration file (cluster-config.yaml):**

cluster-config.yaml

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
 extraPortMappings:
 - containerPort: 30000
   hostPort: 30000
   protocol: TCP
```

**GRADES:**

-   The extraPortMappings is important for environments that use Docker Desktop, because otherwise the kind configuration prevents later accessing content from the Apache (or other) server through localhost:30000 (or another port larger than 30000). For more documentation:<https://kind.sigs.k8s.io/docs/user/configuration/#extra-port-mappings>\*\*

-   Workers could be added with the line

```yaml
-role: worker
```

3.  **Create the cluster and check status:**

```bash
kind create cluster --config=cluster kubectl cluster-info
kubectl cluster-info
```

4.  **Pod configuration files (Apache and Nginx):**

**USE:**Both the service and the deployment are in the same yaml, to save on kubectl apply -f. You could also use kustomize to save deployment time.

**nginx.yaml:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx
spec:
  type: NodePort
  ports:
  - name: http
    port: 80
    protocol: TCP
    targetPort: 80
    nodePort: 30000
  selector:
    app: nginx
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  selector:
    matchLabels:
      app: nginx
  replicas: 1
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
        volumeMounts:
        - name: nginx-conf
          mountPath: /etc/nginx/
      volumes:
      - name: nginx-conf
        configMap:
          name: nginx-conf
```

apache.yaml:

```yaml

apiVersion: v1
kind: Service
metadata:
  name: apache
  labels:
    app: apache
spec:
  ports:
  - name: http
    port: 8080
    targetPort: 80
  selector:
    app: apache
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: apache
spec:
  selector:
    matchLabels:
      app: apache
  replicas: 1
  template:
    metadata:
      labels:
        app: apache
    spec:
      containers:
      - name: apache
        image: httpd:latest
        ports:
        - containerPort: 80
        volumeMounts:
        - name: html
          mountPath: /usr/local/apache2/htdocs/
      volumes:
      - name: html
        configMap:
          name: html
```

5.  **Create the ConfigMap to configure nginx as a reverse proxy (nginx-conf.yaml)**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-conf
data:
  nginx.conf: |
    events {
      worker_connections  1024;
    }

    http {
      server {
        listen 80;
        server_name localhost;

        location / {
          index index.html;
          proxy_pass http://apache:8080/;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
      }
    }
```

**GRADES:**

-   _The worker directive_connections controls the maximum number of simultaneous connections that can be handled by an Nginx worker process. It must be scaled to traffic, 1024 is an example._
-   _Apache port 80 is mapped to 8080 to avoid conflicts with the nginx pod._

6.  **Apply configurations to the cluster:**

```bash
kubectl apply -f nginx.yaml
kubectl apply -f apache.yaml
kubectl apply -f nginx-conf.yaml
```

We check that everything is going well

```bash
kubectl get pods
kubectl exec <nombre de tu pod de nginx> -- cat /etc/nginx/nginx.conf
```

7.  **If we have custom HTML we can use it to view it through nginx and make sure everything is working well up to this point.**

_The files I leave are called custom.html and custom.css, but they can be any other. It's a Dragon ball html that's pretty cool._

-   **We create the ConfigMap from the html and css files:**

```bash
kubectl create configmap html --from-file=custom.html --from-file=custom.css
```

NOTE: The html.yaml file is also left as ConfigMap to be applied with kubectl

```bash
apply -f html.yaml
```

_It is equivalent to the previous command._

-   **We update the apache.yaml, creating a mount point and specifying the volume to use:**

```yaml
...
spec:
      containers:
      - name: apache
        image: httpd:latest
        ports:
        - containerPort: 80
        volumeMounts:
        - name: html
          mountPath: /usr/local/apache2/htdocs/
      volumes:
      - name: html
        configMap:
          name: html
```

-   **We apply the configurations:**

```bash
kubectl apply -f apache.yaml
```

-   **We check that everything has been loaded and the reverse proxy is working correctly:**

```bash
kubectl exec <nombre de tu pod de nginx> -- curl localhost/custom.html
```

8.  **By now we should have this configured correctly.**

**And through localhost:30000 we would access our custom.html web page**

9.  **If everything has gone well up to this point, great, that's what it should be. Otherwise, I have left a kustomization.yaml file that uses kustomize to build everything automatically. If something had gone wrong, follow the following steps:**

```bash
kind delete cluster –-name=<nombreDeTuCluster>
kind create cluster --config=cluster-config.yaml --name=<nombre-que-quieras>
kubectl apply -k .
```

**All ready. Do the above checks (nginx.conf, localhost:30000, etc.) NOTE:**

-   **Be careful with copying and pasting, scripts do not always copy well.**
-   **I know this would have been good sooner, but we have to go over everything from the beginning**😊**.**

**---------------------------------- K8S DASHBOARD -----------------------------------------**

**What is discussed in this section is not the Istio configuration, but rather the configuration of the K8s dashboard for kind. It is very good to see metrics and see the status of the cluster (more info in \[<https://istio.io/latest/docs/setup/platform>- setup/kind/#setup-dashboard-ui-for-kind):**](<https://istio.io/latest/docs/setup/platform-setup/kind/#setup-dashboard-ui-for-kind>)\*\*

1.  **We deploy the dashboard deployment:**

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommende d.yaml --validate=false
```

2.  \*\*We verify that the pod is available and that it has been created correctly:

```bash
kubectl get pod -n kubernetes-dashboard
```

3.  **We create a ServiceAccount and a ClusterRoleBinding to give administrator access to the cluster:**

```bash
kubectl create serviceaccount -n kubernetes-dashboard admin-user

kubectl create clusterrolebinding  -n kubernetes-dashboard admin-user  --clusterrole cluster-admin --serviceaccount=kubernetes-dashboard:admin-user
```

4.  **We generate the token that it will then ask us to log in:**

```bash
token=$(kubectl  -n  kubernetes-dashboard  describe  secret  $(kubectl  -n  kubernetes - dashboard get secret | awk '/^admin-user/{print $1}') | awk '$1=="token:"{print $2}')
```

5.  **We check that it has been stored correctly in the token variable: echo $token**
6.  **We can access the Dashboard through CLI by writing:**

```bash
kubectl proxy
```

**Now we can access from the browser at \[http&#x3A;//localhost:8001/api/v1/namespaces/kubernetes - dashboard/services/https&#x3A;kubernetes-dashboard:/proxy/#/login**](http&#x3A;//localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https&#x3A;kubernetes-dashboard:/proxy/#/login)\*\*

7.  **We access the cluster dashboard from the web, once the token has been entered (e.g. Services, etc.):**

**------------------------------------------------ JENKINS ------------------------------------------**

1.  **To complete the cluster, we are going to introduce Jenkins as well. We will create a service of type NodePort mapped to hostPort 30001, as we will see. The yaml file that contains the deployment and the service is:**

**jenkins.yaml:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: jenkins
spec:
  type: NodePort
  selector:
    app: jenkins
  ports:
    - name: http
      port: 8080
      targetPort: 8080
      nodePort: 30001
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jenkins
spec:
  selector:
    matchLabels:
      app: jenkins
  replicas: 1
  template:
    metadata:
      labels:
        app: jenkins
    spec:
      containers:
        - name: jenkins
          image: jenkins/jenkins:lts
          ports:
            - containerPort: 8080
            - containerPort: 50000
```

2.  **At this point, we will be wondering where we are going to expose Jenkins. The idea would be to do it through nginx in “location jenkins/” and access through localhost:30000/jenkins - you would only have to modify nginx-conf.yaml and add**


    location /jenkins {

        proxy\_pass http://<jenkinsPodUsedIp>:30001/;
        proxy\_set\_header Host $host;
        proxy\_set\_header X-Real-IP $remote\_addr;
        proxy\_set\_header X-Forwarded-For $proxy\_add\_x\_forwarded\_for; proxy\_set\_header X-Forwarded-Proto $scheme;

    }

_In my case, I can't do it like this due to kind compatibility problems with wsl2. To do this, I have modified the cluster-config.yaml file, writing the extraPortMappings that we will need later. Additionally, I've added a couple of workers and added a tag in the master to add an ingress controller later:_

**cluster-config.yaml**

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
  - containerPort: 8080
    hostPort: 8080
    protocol: TCP
  - containerPort: 30000
    hostPort: 30000
    protocol: TCP
  - containerPort: 30001
    hostPort: 30001
    protocol: TCP
- role: worker
- role: worker
```

3.  **Now, you can continue with your cluster and add Jenkins. If at any point you have gotten lost, there is a file called autoDeploy.sh that shows you the entire scenario. Comment on the parts you haven't reached so you can try doing them yourself and execute:**

```bash
./autoDeploy.sh
```

4.  **Finally, we can access nginx through localhost:30000 and Jenkins through localhost:30001. We already know how nginx goes, let's move on to Jenkins:**

-   _Unlock Jenkins:_**we need the initial password. We execute:**

```bash
kubectl get pods
kubectl exec <nombre-pod-jenkins> -- cat** /var/jenkins\_home/secrets/initialAdminPassword**
```

-   **We go to localhost:30001 and enter the initial password.**

-   **Install the recommended plugins, create your administrator user and that's it!**

**GRADES:**

-   **If you want to use a more attractive name than “localhost”, you can modify the /etc/hosts file on your machine by adding the line 127.0.0.1<nombre-de-dominio-guay>. You would get something like this:**

-   **It is always advisable to work with different namespaces (e.g. pre, pro, dev, etc.). We do not do it in this brief practice so as not to complicate the matter further, but the best thing to do would be to separate Jenkins from the other services, etc.**

**----------------------------------------- THIS -------- -----------------------------**

**We pass to Istio. Due to my little experience and the documentation I have read, Istio causes a lot of problems working with a local cluster since, among other things, we do not manage traffic from outside. Therefore, the configurations that we are going to make are not excessively complex, but are rather illustrative of what the usefulness of the service is.**

**First of all:**

-   _The "Gateway" is an Istio component that acts as an entrypoint for external traffic entering the cluster._
-   _The "VirtualService" is an Istio object that allows you to define how traffic should be directed from the Gateway to the back-end services in the cluster._

10. **Installing Istio in cluster:**

-   **Download and install Istio:**

```bash
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH
```

-   **Check that the CRDs are installed with:**

```bash
kubectl get crds | grep 'istio.io\|certmanager.k8s.io' | wc -l
```

-   **If we get 0, execute:**

```bash
istioctl install --set profile=default
```

-   **Check that everything works and that an ingress gateway and an istio pod have been created:**

```bash
kubectl get pods -n istio-system
```

-   **Enable Istio for the namespace in which the Apache, Nginx and Jenkins pods are deployed:**

```bash
kubectl label namespace default istio-injection=enabled
```

11. **To do a simple Istio setup in this scenario, we could add a load balancer for the nginx service using Istio traffic control. For it:**

-   **Generate a load balancer for the nginx service. We create a VirtualService and a Gateway in Istio for nginx:**

**loadBalancerNginx.yaml:**

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: nginx-vs
spec:
  hosts:
  - "*"
  gateways:
  - istio-gateway
  http:
  - match:
    - uri:
        prefix: /
    route:
    - destination:
        host: nginx
        port:
          number: 80
---
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: istio-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"

```

```bash
kubectl apply -f loadBalancerNginx.yaml
```

**GRADES:**

-   **Theoretically we should be able to access nginx through http&#x3A;//<nodeIP>:30000. In reality, working on local kind makes things more difficult for us since our environment does not support external load balancers. This cannot be fixed without modifying the kubelet configuration file, cluster-config, etc. If an external balancer were supported, the procedure would be to modify the exports as follows (in my case for wsl2):**

```bash
export INGRESS_NAME=istio-ingressgateway
export INGRESS_NS=istio-system

export INGRESS_HOST=127.0.0.1

#check
kubectl get svc -n istio-system
echo "INGRESS_HOST=$INGRESS_HOST, INGRESS_PORT=$INGRESS_PORT"

export GATEWAY_URL=$INGRESS_HOST:$INGRESS_PORT
```

**The nginx-nodeport.yaml file, in case you want to mess around with it, is: nginx-nodeport.yaml:**

```bash
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: nginx-nodeport-vs
spec:
  hosts:
  - "*"
  gateways:
  - istio-gateway
  http:
  - match:
    - port: 30000
    route:
    - destination:
        host: nginx
        port:
          number: 80
```

-   **It is possible that you will have to restart the deployments (or delete the pods) so that they have istio injected:**

```bash
kubectl rollout restart deployment nginx
kubectl rollout restart deployment apache
kubectl delete pods --all**
```

-   **Check that everything works well with:**

```bash
istioctl analyze
kubectl get gateway
kubectl get vs
```

**--------------------------------------- KIALI ---------- ------------------------------**

**Assuming that we already have a load balancer that redirects everything to the nginx reverse-proxy, we proceed to see the following tool. Kiali is an Istio tracking/dashboard tool that provides visualizations and analysis of Istio service topology and network traffic information. It is typically used whenever Istio is configured (such as Grafana if Prometheus is configured or Kibana if Elastic-Search is configured). Let's install it:**

12. **Installer:**

```bash
kubectl  apply  -f  https://raw.githubuserconten 1.17/samples/addons/kiali.yaml --validate=false**
```

13. **Check installation:**

```bash
kubectl -n istio-system get svc kiali
```

14. **Use the dashboard:**

```bash
istioctl dashboard kiali
```

**CONCLUSION:**

**Istio is a very complete service that can be integrated with Prometheus, the Kubernetes dashboard itself, and many other services and platforms. We will improve Istio configurations in the next labs where, among other things, we will install Prometheus through Istio, and focus more on cluster monitoring.**

**IMPORTANT NOTES:**

-   The entire scenario can be assembled by running the autoDeploy.py file, in case there is ever a problem. The file accepts a single input, which is the name of the cluster. If you want to leave it as default, the name is “trainingPath” (press Enter).

```bash
python3 autoDeploy.py
```

-   If you are using wsl2 or a Linux distro, it is better to use the autoDeploy.sh file, as it avoids possible problems with python exports. In an empty directory you have to execute:

```bash
./autoDeploy.sh
```

-   It is important to modify the version of Istio to install (latest in<https://istio.io/downloadIstio>)

**Relevant Istio References:**

-   <https://istio.io/latest/docs/tasks/traffic-management/ingress/ingress-control/#using-node-ports-of-the-ingress-gateway-service>

-   <https://istio.io/latest/docs/tasks/traffic-management/ingress/ingress-control/#using-node-ports-of-the-ingress-gateway-service>

-   <https://istio.io/latest/docs/examples/bookinfo/#determine-the-ingress-ip-and-port>

-   <https://istio.io/latest/docs/examples/bookinfo/#determine-the-ingress-ip-and-port>
