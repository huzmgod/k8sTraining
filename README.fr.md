# k8sFormation

Apache, Nginx, Jenkins, Istio, Kiali (pour le moment)

Vérifier**_TrainingPathProject.pdf_**pour un fichier Lisez-moi complet 😊

Pour déployer l'ensemble du scénario, exécutez :

```bash
./autoDeploy.sh
```

Si vous préférez jouer lentement, il suffit de :

```bash
git clone https://github.com/huzmgod/k8sTraining.git
cd k8sTraining
```

**_-----------------------------------------------------------------------------------------------------------------------_**

**_README complet en espagnol (sans les images, qui sont dans le pdf) :_**

**Configuration de Nginx en tant que proxy inverse pour Apache à l'aide de K8. Jenkins, Istio, K8s Dashboard et Kiali déployés**

1.  **Type d'installation :<https://kind.sigs.k8s.io/docs/user/quick-start/#installation>**
2.  **Créez le fichier de configuration du cluster (cluster-config.yaml) :**

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

**NOTES :**

-   L'extraPortMappings est important pour les environnements qui utilisent Docker Desktop, car sinon la configuration kind empêche l'accès ultérieur au contenu du serveur Apache (ou autre) via localhost:30000 (ou un autre port supérieur à 30000). Pour plus de documentation :<https://kind.sigs.k8s.io/docs/user/configuration/#extra-port-mappings>\*\*

-   Les travailleurs pourraient être ajoutés avec la ligne

```yaml
-role: worker
```

3.  **Créez le cluster et vérifiez l'état :**

```bash
kind create cluster --config=cluster kubectl cluster-info
kubectl cluster-info
```

4.  **Fichiers de configuration des pods (Apache et Nginx) :**

**UTILISER:**Le service et le déploiement sont dans le même yaml, à enregistrer sur kubectl apply -f. Vous pouvez également utiliser kustomize pour gagner du temps de déploiement.

**nginx.yaml :**

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

apache.yaml :

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

5.  **Créez le ConfigMap pour configurer nginx en tant que proxy inverse (nginx-conf.yaml)**

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

**NOTES :**

-   _La directive sur les travailleurs_connexions contrôle le nombre maximum de connexions simultanées pouvant être gérées par un processus de travail Nginx. Il doit être adapté au trafic, 1024 en est un exemple._
-   _Le port Apache 80 est mappé sur 8080 pour éviter les conflits avec le pod nginx._

6.  **Appliquez les configurations au cluster :**

```bash
kubectl apply -f nginx.yaml
kubectl apply -f apache.yaml
kubectl apply -f nginx-conf.yaml
```

On vérifie que tout va bien

```bash
kubectl get pods
kubectl exec <nombre de tu pod de nginx> -- cat /etc/nginx/nginx.conf
```

7.  **Si nous avons du HTML personnalisé, nous pouvons l'utiliser pour le visualiser via nginx et nous assurer que tout fonctionne bien jusqu'à présent.**

_Les fichiers que je laisse s'appellent custom.html et custom.css, mais ils peuvent être n'importe quel autre. C'est un HTML Dragon Ball qui est plutôt cool._

-   **Nous créons le ConfigMap à partir des fichiers html et css :**

```bash
kubectl create configmap html --from-file=custom.html --from-file=custom.css
```

REMARQUE : Le fichier html.yaml est également laissé en tant que ConfigMap à appliquer avec kubectl

```bash
apply -f html.yaml
```

_C'est équivalent à la commande précédente._

-   **Nous mettons à jour le fichier apache.yaml, en créant un point de montage et en spécifiant le volume à utiliser :**

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

-   **Nous appliquons les configurations :**

```bash
kubectl apply -f apache.yaml
```

-   **On vérifie que tout a été chargé et que le reverse proxy fonctionne correctement :**

```bash
kubectl exec <nombre de tu pod de nginx> -- curl localhost/custom.html
```

8.  **À présent, nous devrions avoir configuré correctement cela.**

**Et via localhost:30000, nous accéderions à notre page Web custom.html**

9.  **Si tout s’est bien passé jusqu’à présent, tant mieux, c’est comme ça que ça devrait être. Sinon, j'ai laissé un fichier kustomization.yaml qui utilise kustomize pour tout construire automatiquement. Si quelque chose ne va pas, suivez les étapes suivantes :**

```bash
kind delete cluster –-name=<nombreDeTuCluster>
kind create cluster --config=cluster-config.yaml --name=<nombre-que-quieras>
kubectl apply -k .
```

**Tout prêt. Effectuez les vérifications ci-dessus (nginx.conf, localhost:30000, etc.) REMARQUE :**

-   **Attention au copier-coller, les scripts ne se copient pas toujours bien.**
-   **Je sais que ça aurait été bien plus tôt, mais il faut tout reprendre depuis le début**😊**.**

**---------------------------------- TABLEAU DE BORD K8S -------------- --------------------------------**

**Ce qui est abordé dans cette section n'est pas la configuration d'Istio, mais plutôt la configuration du tableau de bord du K8s. C'est très bien de voir les métriques et de voir l'état du cluster (plus d'informations dans \[<https://istio.io/latest/docs/setup/platform>- setup/kind/#setup-dashboard-ui-for-kind) :**](<https://istio.io/latest/docs/setup/platform-setup/kind/#setup-dashboard-ui-for-kind>)\*\*

1.  **Nous déployons le déploiement du tableau de bord :**

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommende d.yaml --validate=false
```

2.  \*\*Nous vérifions que le pod est disponible et qu'il a été correctement créé :

```bash
kubectl get pod -n kubernetes-dashboard
```

3.  **Nous créons un ServiceAccount et un ClusterRoleBinding pour donner un accès administrateur au cluster :**

```bash
kubectl create serviceaccount -n kubernetes-dashboard admin-user

kubectl create clusterrolebinding  -n kubernetes-dashboard admin-user  --clusterrole cluster-admin --serviceaccount=kubernetes-dashboard:admin-user
```

4.  **Nous générons le token qui nous demandera ensuite de nous connecter :**

```bash
token=$(kubectl  -n  kubernetes-dashboard  describe  secret  $(kubectl  -n  kubernetes - dashboard get secret | awk '/^admin-user/{print $1}') | awk '$1=="token:"{print $2}')
```

5.  **On vérifie qu'il a été correctement stocké dans la variable token : echo $token**
6.  **Nous pouvons accéder au tableau de bord via CLI en écrivant :**

```bash
kubectl proxy
```

**Nous pouvons désormais accéder depuis le navigateur à l'adresse \[http&#x3A;//localhost:8001/api/v1/namespaces/kubernetes - Dashboard/services/https&#x3A;kubernetes-dashboard:/proxy/#/login**](http&#x3A;//localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https&#x3A;kubernetes-dashboard:/proxy/#/login)\*\*

7.  **On accède au tableau de bord du cluster depuis le web, une fois le token renseigné (ex. Services, etc.) :**

**------------------------------------------------ JENKINS - -----------------------------------------**

1.  **Pour compléter le cluster, nous allons également présenter Jenkins. Nous allons créer un service de type NodePort mappé sur hostPort 30001, comme nous le verrons. Le fichier yaml qui contient le déploiement et le service est :**

**jenkins.yaml :**

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

2.  **À ce stade, nous nous demanderons où nous allons exposer Jenkins. L'idée serait de le faire via nginx dans « location jenkins/ » et d'y accéder via localhost:30000/jenkins - il vous suffirait de modifier nginx-conf.yaml et d'ajouter**


    location /jenkins {

        proxy\_pass http://<jenkinsPodUsedIp>:30001/;
        proxy\_set\_header Host $host;
        proxy\_set\_header X-Real-IP $remote\_addr;
        proxy\_set\_header X-Forwarded-For $proxy\_add\_x\_forwarded\_for; proxy\_set\_header X-Forwarded-Proto $scheme;

    }

_Dans mon cas, je ne peux pas le faire comme ça en raison de problèmes de compatibilité avec wsl2. Pour ce faire, j'ai modifié le fichier cluster-config.yaml, en écrivant les extraPortMappings dont nous aurons besoin plus tard. De plus, j'ai ajouté quelques travailleurs et ajouté une balise dans le maître pour ajouter un contrôleur d'entrée plus tard :_

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

3.  **Maintenant, vous pouvez continuer avec votre cluster et ajouter Jenkins. Si à un moment donné vous vous êtes perdu, il existe un fichier appelé autoDeploy.sh qui vous montre l'intégralité du scénario. Commentez les parties que vous n'avez pas atteintes afin de pouvoir essayer de les faire vous-même et exécuter :**

```bash
./autoDeploy.sh
```

4.  **Enfin, nous pouvons accéder à nginx via localhost:30000 et Jenkins via localhost:30001. Nous savons déjà comment fonctionne nginx, passons à Jenkins :**

-   _Débloquez Jenkins :_**nous avons besoin du mot de passe initial. Nous exécutons :**

```bash
kubectl get pods
kubectl exec <nombre-pod-jenkins> -- cat** /var/jenkins\_home/secrets/initialAdminPassword**
```

-   **Nous allons sur localhost:30001 et entrons le mot de passe initial.**

-   **Installez les plugins recommandés, créez votre utilisateur administrateur et c'est prêt !**

**NOTES :**

-   **Si vous souhaitez utiliser un nom plus attractif que « localhost », vous pouvez modifier le fichier /etc/hosts sur votre machine en ajoutant la ligne 127.0.0.1<nombre-de-dominio-guay>. Vous obtiendriez quelque chose comme ceci :**

-   **Il est toujours conseillé de travailler avec différents espaces de noms (par exemple pre, pro, dev, etc.). Nous ne le faisons pas dans cette brève pratique pour ne pas compliquer davantage les choses, mais la meilleure chose à faire serait de séparer Jenkins des autres services, etc.**

**----------------------------------------- CE -------- -----------------------------**

**Nous passons à Istio. De par mon peu d'expérience et la documentation que j'ai lue, Istio pose beaucoup de problèmes pour travailler avec un cluster local puisque, entre autres, nous ne gérons pas le trafic venant de l'extérieur. Les configurations que nous allons faire ne sont donc pas excessivement complexes, mais plutôt illustratives de l’utilité du service.**

**Avant tout:**

-   _La « Gateway » est un composant Istio qui fait office de point d'entrée pour le trafic externe entrant dans le cluster._
-   _Le « VirtualService » est un objet Istio qui vous permet de définir la manière dont le trafic doit être dirigé de la passerelle vers les services back-end du cluster._

10. **Installation d'Istio en cluster :**

-   **Téléchargez et installez Istio :**

```bash
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH
```

-   **Vérifiez que les CRD sont installés avec :**

```bash
kubectl get crds | grep 'istio.io\|certmanager.k8s.io' | wc -l
```

-   **Si nous obtenons 0, exécutez :**

```bash
istioctl install --set profile=default
```

-   **Vérifiez que tout fonctionne et qu'une passerelle d'entrée et un pod istio ont été créés :**

```bash
kubectl get pods -n istio-system
```

-   **Activez Istio pour l'espace de noms dans lequel les pods Apache, Nginx et Jenkins sont déployés :**

```bash
kubectl label namespace default istio-injection=enabled
```

11. **Pour effectuer une configuration simple d'Istio dans ce scénario, nous pourrions ajouter un équilibreur de charge pour le service nginx à l'aide du contrôle du trafic Istio. Pour cela:**

-   **Générez un équilibreur de charge pour le service nginx. Nous créons un VirtualService et une Gateway dans Istio pour nginx :**

**loadBalancerNginx.yaml :**

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

**NOTES :**

-   **Théoriquement, nous devrions pouvoir accéder à nginx via http&#x3A;//<nodeIP>:30000. En réalité, travailler sur du type local nous rend les choses plus difficiles puisque notre environnement ne prend pas en charge les équilibreurs de charge externes. Cela ne peut pas être résolu sans modifier le fichier de configuration de kubelet, la configuration du cluster, etc. Si un équilibreur externe était pris en charge, la procédure serait de modifier les exportations comme suit (dans mon cas pour wsl2) :**

```bash
export INGRESS_NAME=istio-ingressgateway
export INGRESS_NS=istio-system

export INGRESS_HOST=127.0.0.1

#check
kubectl get svc -n istio-system
echo "INGRESS_HOST=$INGRESS_HOST, INGRESS_PORT=$INGRESS_PORT"

export GATEWAY_URL=$INGRESS_HOST:$INGRESS_PORT
```

**Le fichier nginx-nodeport.yaml, au cas où vous voudriez vous amuser avec, est : nginx-nodeport.yaml :**

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

-   **Il est possible que vous deviez redémarrer les déploiements (ou supprimer les pods) pour qu'ils aient injecté istio :**

```bash
kubectl rollout restart deployment nginx
kubectl rollout restart deployment apache
kubectl delete pods --all**
```

-   **Vérifiez que tout fonctionne bien avec :**

```bash
istioctl analyze
kubectl get gateway
kubectl get vs
```

**--------------------------------------- KIALI ---------- -------------------------------**

**En supposant que nous disposons déjà d'un équilibreur de charge qui redirige tout vers le proxy inverse nginx, nous passons à l'outil suivant. Kiali est un outil de suivi/tableau de bord Istio qui fournit des visualisations et des analyses de la topologie du service Istio et des informations sur le trafic réseau. Il est généralement utilisé chaque fois qu'Istio est configuré (comme Grafana si Prometheus est configuré ou Kibana si Elastic-Search est configuré). Installons-le :**

12. **Installateur :**

```bash
kubectl  apply  -f  https://raw.githubuserconten 1.17/samples/addons/kiali.yaml --validate=false**
```

13. **Vérifiez l'installation :**

```bash
kubectl -n istio-system get svc kiali
```

14. **Utilisez le tableau de bord :**

```bash
istioctl dashboard kiali
```

**CONCLUSION:**

**Istio est un service très complet qui peut être intégré à Prometheus, au tableau de bord Kubernetes lui-même et à de nombreux autres services et plateformes. Nous améliorerons les configurations d'Istio dans les prochains laboratoires où, entre autres, nous installerons Prometheus via Istio et nous concentrerons davantage sur la surveillance des clusters.**

**NOTES IMPORTANTES:**

-   L'ensemble du scénario peut être assemblé en exécutant le fichier autoDeploy.py, en cas de problème. Le fichier accepte une seule entrée, qui est le nom du cluster. Si vous souhaitez le laisser par défaut, le nom est « trainingPath » (appuyez sur Entrée).

```bash
python3 autoDeploy.py
```

-   Si vous utilisez wsl2 ou une distribution Linux, il est préférable d'utiliser le fichier autoDeploy.sh, car il évite d'éventuels problèmes avec les exportations Python. Dans un répertoire vide vous devez exécuter :

```bash
./autoDeploy.sh
```

-   Il est important de modifier la version d'Istio à installer (dernière version<https://istio.io/downloadIstio>)

**Références Istio pertinentes :**

-   <https://istio.io/latest/docs/tasks/traffic-management/ingress/ingress-control/#using-node-ports-of-the-ingress-gateway-service>

-   <https://istio.io/latest/docs/tasks/traffic-management/ingress/ingress-control/#using-node-ports-of-the-ingress-gateway-service>

-   <https://istio.io/latest/docs/examples/bookinfo/#determine-the-ingress-ip-and-port>

-   <https://istio.io/latest/docs/examples/bookinfo/#determine-the-ingress-ip-and-port>
