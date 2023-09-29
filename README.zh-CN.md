# k8s培训

Apache、Nginx、Jenkins、Istio、Kiali（目前）

查看**_培训路径项目.pdf_**完整的自述文件😊

要部署整个场景，请执行：

```bash
./autoDeploy.sh
```

如果你想慢慢地玩，只需：

```bash
git clone https://github.com/huzmgod/k8sTraining.git
cd k8sTraining
```

**_-----------------------------------------------------------------------------------------------------------------------_**

**_西班牙语完整自述文件（没有图像，在 pdf 中）：_**

**使用 K8s 将 Nginx 设置为 Apache 的反向代理。部署 Jenkins、Istio、K8s Dashboard 和 Kiali**

1.  **安装类型：[HTTPS://kind.四公司.可8是.IO/docs/user/quick-start/#installation](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)**
2.  **创建集群配置文件（cluster-config.yaml）：**

集群配置.yaml

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

**成绩：**

-   extraPortMappings 对于使用 Docker Desktop 的环境非常重要，因为否则该类型配置会阻止以后通过 localhost:30000（或另一个大于 30000 的端口）访问 Apache（或其他）服务器的内容。如需更多文档：[HTTPS://kind.四公司.可8是.IO/docs/user/configuration/#extra-port-mappings](https://kind.sigs.k8s.io/docs/user/configuration/#extra-port-mappings)\*\*

-   可以通过该行添加工人

```yaml
-role: worker
```

3.  **创建集群并检查状态：**

```bash
kind create cluster --config=cluster kubectl cluster-info
kubectl cluster-info
```

4.  **Pod 配置文件（Apache 和 Nginx）：**

**使用：**服务和部署都在同一个 yaml 中，以节省 kubectl apply -f 的时间。您还可以使用 kustomize 来节省部署时间。

**nginx.yaml：**

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

阿帕奇.yaml：

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

5.  **创建 ConfigMap 将 nginx 配置为反向代理 (nginx-conf.yaml)**

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

**成绩：**

-   _工人指令\_连接数控制 Nginx 工作进程可以处理的最大并发连接数。它必须根据流量进行缩放，1024 就是一个例子。_
-   _Apache端口80映射到8080以避免与nginx pod冲突。_

6.  **将配置应用到集群：**

```bash
kubectl apply -f nginx.yaml
kubectl apply -f apache.yaml
kubectl apply -f nginx-conf.yaml
```

我们检查一切是否顺利

```bash
kubectl get pods
kubectl exec <nombre de tu pod de nginx> -- cat /etc/nginx/nginx.conf
```

7.  **如果我们有自定义 HTML，我们可以使用它通过 nginx 查看它，并确保到目前为止一切正常。**

_我留下的文件称为 custom.html 和 custom.css，但它们可以是任何其他文件。这是一个非常酷的龙珠 html。_

-   **我们从 html 和 css 文件创建 ConfigMap：**

```bash
kubectl create configmap html --from-file=custom.html --from-file=custom.css
```

注意：html.yaml 文件也保留为 ConfigMap，以便与 kubectl 一起应用

```bash
apply -f html.yaml
```

_它相当于前面的命令。_

-   **我们更新 apache.yaml，创建挂载点并指定要使用的卷：**

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

-   **我们应用配置：**

```bash
kubectl apply -f apache.yaml
```

-   **我们检查所有内容是否已加载并且反向代理是否正常工作：**

```bash
kubectl exec <nombre de tu pod de nginx> -- curl localhost/custom.html
```

8.  **现在我们应该已经正确配置了。**

**通过 localhost:30000 我们将访问我们的 custom.html 网页**

9.  **如果到目前为止一切都很顺利，那就太好了，那就应该是这样。否则，我留下了一个 kustomization.yaml 文件，它使用 kustomize 自动构建所有内容。如果出现问题，请按照以下步骤操作：**

```bash
kind delete cluster –-name=<nombreDeTuCluster>
kind create cluster --config=cluster-config.yaml --name=<nombre-que-quieras>
kubectl apply -k .
```

**一切准备就绪。执行上述检查（nginx.conf、localhost:30000 等）注意：**

-   **复制和粘贴时要小心，脚本并不总是能很好地复制。**
-   **我知道这会更好，但我们必须从头开始检查所有事情**😊**.**

**---------------------------------- K8S 仪表板 -------------- ----------------------------**

**本节讨论的不是 Istio 配置，而是 K8s 仪表板的配置。很高兴看到指标并查看集群的状态（更多信息在\[[HTTPS://is TiO.IO/latest/docs/setup/platform](https://istio.io/latest/docs/setup/platform)- 设置/种类/#setup-dashboard-ui-for-kind):**]([HTTPS://is TiO.IO/latest/docs/setup/platform-setup/kind/#setup-dashboard-UI-佛如-kind](https://istio.io/latest/docs/setup/platform-setup/kind/#setup-dashboard-ui-for-kind))\*\*

1.  **我们部署仪表板部署：**

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommende d.yaml --validate=false
```

2.  \*\*我们验证 Pod 是否可用并且已正确创建：

```bash
kubectl get pod -n kubernetes-dashboard
```

3.  **我们创建一个 ServiceAccount 和一个 ClusterRoleBinding 来授予管理员对集群的访问权限：**

```bash
kubectl create serviceaccount -n kubernetes-dashboard admin-user

kubectl create clusterrolebinding  -n kubernetes-dashboard admin-user  --clusterrole cluster-admin --serviceaccount=kubernetes-dashboard:admin-user
```

4.  **我们生成令牌，然后它会要求我们登录：**

```bash
token=$(kubectl  -n  kubernetes-dashboard  describe  secret  $(kubectl  -n  kubernetes - dashboard get secret | awk '/^admin-user/{print $1}') | awk '$1=="token:"{print $2}')
```

5.  **我们检查它是否已正确存储在 token 变量中： echo $token**
6.  **我们可以通过 CLI 访问仪表板，方法如下：**

```bash
kubectl proxy
```

**现在我们可以从浏览器访问\[http&#x3A;//localhost:8001/api/v1/namespaces/kubernetes -dashboard/services/https&#x3A;kubernetes-dashboard:/proxy/#/login**](http&#x3A;//localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https&#x3A;kubernetes-dashboard:/proxy/#/login)\*\*

7.  **输入令牌后（例如服务等），我们可以从网络访问集群仪表板：**

**------------------------------------------------ 詹金斯 - ----------------------------------------------------**

1.  **为了完成集群，我们还将引入 Jenkins。正如我们将看到的，我们将创建映射到主机端口 30001 的 NodePort 类型的服务。包含部署和服务的 yaml 文件是：**

**詹金斯.yaml：**

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

2.  **此时，我们会想知道我们要在哪里暴露 Jenkins。这个想法是通过“location jenkins/”中的 nginx 来完成，并通过 localhost:30000/jenkins 访问 - 你只需要修改 nginx-conf.yaml 并添加**


    location /jenkins {

        proxy\_pass http://<jenkinsPodUsedIp>:30001/;
        proxy\_set\_header Host $host;
        proxy\_set\_header X-Real-IP $remote\_addr;
        proxy\_set\_header X-Forwarded-For $proxy\_add\_x\_forwarded\_for; proxy\_set\_header X-Forwarded-Proto $scheme;

    }

_就我而言，由于与 wsl2 的兼容性问题，我无法这样做。为此，我修改了 cluster-config.yaml 文件，编写了稍后需要的 extraPortMappings。此外，我还添加了几个工作人员，并在 master 中添加了一个标签，以便稍后添加入口控制器：_

**集群配置.yaml**

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

3.  **现在，您可以继续您的集群并添加 Jenkins。如果您在任何时候迷失了方向，有一个名为 autoDeploy.sh 的文件可以向您显示整个场景。对您未达到的部分进行评论，以便您可以尝试自己做并执行：**

```bash
./autoDeploy.sh
```

4.  **最后，我们可以通过localhost:30000访问nginx，通过localhost:30001访问Jenkins。我们已经知道 nginx 是如何运行的，让我们继续讨论 Jenkins：**

-   _解锁詹金斯：_**我们需要初始密码。我们执行：**

```bash
kubectl get pods
kubectl exec <nombre-pod-jenkins> -- cat** /var/jenkins\_home/secrets/initialAdminPassword**
```

-   **我们访问 localhost:30001 并输入初始密码。**

-   **安装推荐的插件，创建您的管理员用户并准备好！**

**成绩：**

-   **如果您想使用比“localhost”更有吸引力的名称，可以修改计算机上的 /etc/hosts 文件，添加行 127.0.0.1<nombre-de-dominio-guay>。你会得到这样的东西：**

-   **始终建议使用不同的命名空间（例如 pre、pro、dev 等）。我们不会在这个简短的实践中这样做，以免使问题进一步复杂化，但最好的办法是将 Jenkins 与其他服务分开，等等。**

** -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - - 这  -  -  -  - ----------------------------**

**我们转到 Istio。由于我的经验和我读过的文档很少，Istio 在使用本地集群时会导致很多问题，因为除其他外，我们不管理来自外部的流量。因此，我们要做的配置不会过于复杂，而是能够说明该服务的用处。**

**首先：**

-   _“网关”是一个 Istio 组件，充当外部流量进入集群的入口点。_
-   _“VirtualService”是一个 Istio 对象，允许您定义如何将流量从网关引导到集群中的后端服务。_

10. **在集群中安装 Istio：**

-   **下载并安装 Istio：**

```bash
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH
```

-   **检查 CRD 是否已安装：**

```bash
kubectl get crds | grep 'istio.io\|certmanager.k8s.io' | wc -l
```

-   **如果得到 0，则执行：**

```bash
istioctl install --set profile=default
```

-   **检查一切是否正常，以及是否已创建入口网关和 istio pod：**

```bash
kubectl get pods -n istio-system
```

-   **为部署 Apache、Nginx 和 Jenkins Pod 的命名空间启用 Istio：**

```bash
kubectl label namespace default istio-injection=enabled
```

11. **要在此场景中进行简单的 Istio 设置，我们可以使用 Istio 流量控制为 nginx 服务添加负载均衡器。为了它：**

-   **为 nginx 服务生成负载均衡器。我们在 Istio 中为 nginx 创建一个 VirtualService 和一个 Gateway：**

**loadBalancerNginx.yaml：**

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

**成绩：**

-   **理论上我们应该可以通过http&#x3A;//访问nginx<nodeIP>：30000。实际上，由于我们的环境不支持外部负载均衡器，因此在本地工作会使事情变得更加困难。如果不修改 kubelet 配置文件、cluster-config 等，则无法修复此问题。如果支持外部平衡器，则程序将修改导出如下（在我的例子中是 wsl2）：**

```bash
export INGRESS_NAME=istio-ingressgateway
export INGRESS_NS=istio-system

export INGRESS_HOST=127.0.0.1

#check
kubectl get svc -n istio-system
echo "INGRESS_HOST=$INGRESS_HOST, INGRESS_PORT=$INGRESS_PORT"

export GATEWAY_URL=$INGRESS_HOST:$INGRESS_PORT
```

**如果您想搞乱它，nginx-nodeport.yaml 文件是：nginx-nodeport.yaml：**

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

-   **您可能必须重新启动部署（或删除 pod），以便它们注入 istio：**

```bash
kubectl rollout restart deployment nginx
kubectl rollout restart deployment apache
kubectl delete pods --all**
```

-   **检查一切是否正常：**

```bash
istioctl analyze
kubectl get gateway
kubectl get vs
```

**--------------------------------------- 基亚利 ---------- ------------------------------------------**

**假设我们已经有一个负载均衡器，可以将所有内容重定向到 nginx 反向代理，我们继续查看以下工具。 Kiali 是一个 Istio 跟踪/仪表板工具，可提供 Istio 服务拓扑和网络流量信息的可视化和分析。它通常在配置 Istio 时使用（例如，如果配置了 Prometheus，则使用 Grafana；如果配置了 Elastic-Search，则使用 Kibana）。让我们安装它：**

12. **安装人员：**

```bash
kubectl  apply  -f  https://raw.githubuserconten 1.17/samples/addons/kiali.yaml --validate=false**
```

13. **检查安装：**

```bash
kubectl -n istio-system get svc kiali
```

14. **使用仪表板：**

```bash
istioctl dashboard kiali
```

**结论：**

**Istio 是一个非常完整的服务，可以与 Prometheus、Kubernetes 仪表板本身以及许多其他服务和平台集成。我们将在接下来的实验室中改进 Istio 配置，除其他外，我们将通过 Istio 安装 Prometheus，并更多地关注集群监控。**

**重要笔记：**

-   可以通过运行 autoDeploy.py 文件来组装整个场景，以防出现问题。该文件接受单个输入，即集群的名称。如果您想将其保留为默认值，则名称为“trainingPath”（按 Enter 键）。

```bash
python3 autoDeploy.py
```

-   如果您使用 wsl2 或 Linux 发行版，最好使用 autoDeploy.sh 文件，因为它可以避免 python 导出可能出现的问题。在空目录中，您必须执行：

```bash
./autoDeploy.sh
```

-   修改要安装的 Istio 版本很重要（最新[HTTPS://is TiO.IO/download is TiO](https://istio.io/downloadIstio))

**相关 Istio 参考资料：**

-   [HTTPS://is TiO.IO/latest/docs/tasks/traffic-management/ingress/ingress-control/#using-node-ports-of-他和-ingress-gateway-service](https://istio.io/latest/docs/tasks/traffic-management/ingress/ingress-control/#using-node-ports-of-the-ingress-gateway-service)

-   [HTTPS://is TiO.IO/latest/docs/tasks/traffic-management/ingress/ingress-control/#using-node-ports-of-他和-ingress-gateway-service](https://istio.io/latest/docs/tasks/traffic-management/ingress/ingress-control/#using-node-ports-of-the-ingress-gateway-service)

-   [HTTPS://is TiO.IO/latest/docs/examples/book info/#determine-他和-ingress-IP-安定-port](https://istio.io/latest/docs/examples/bookinfo/#determine-the-ingress-ip-and-port)

-   [HTTPS://is TiO.IO/latest/docs/examples/book info/#determine-他和-ingress-IP-安定-port](https://istio.io/latest/docs/examples/bookinfo/#determine-the-ingress-ip-and-port)
