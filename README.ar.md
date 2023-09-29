# تدريب k8s

Apache، Nginx، Jenkins، Istio، Kiali (في الوقت الحالي)

يفحص**_مشروع مسار التدريب.pdf_**للقراءة الكاملة 😊

لنشر السيناريو بأكمله، قم بتنفيذ:

```bash
./autoDeploy.sh
```

إذا كنت تفضل اللعب ببطء، فما عليك سوى:

```bash
git clone https://github.com/huzmgod/k8sTraining.git
cd k8sTraining
```

**_-----------------------------------------------------------------------------------------------------------------------_**

**_الملف التمهيدي الكامل باللغة الإسبانية (بدون الصور الموجودة في ملف pdf):_**

**إعداد Nginx كوكيل عكسي لـ Apache باستخدام K8s. تم نشر Jenkins وIstio وK8s Dashboard وKiali**

1.  **نوع التثبيت:[هتبص://كند.سجس.كقص.إيه/دكس/عصر/قيكسترة/#نستلت](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)**
2.  **إنشاء ملف تكوين المجموعة (cluster-config.yaml):**

الكتلة-config.yaml

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

**درجات:**

-   يعد extraPortMappings مهمًا للبيئات التي تستخدم Docker Desktop، وإلا فإن تكوين النوع يمنع الوصول لاحقًا إلى المحتوى من خادم Apache (أو خادم آخر) من خلال المضيف المحلي: 30000 (أو منفذ آخر أكبر من 30000). لمزيد من الوثائق:[هتبص://كند.سجس.كقص.إيه/دكس/عصر/كنفجرت/#إكسترابرتمبنجس](https://kind.sigs.k8s.io/docs/user/configuration/#extra-port-mappings)\*\*

-   يمكن إضافة العمال مع السطر

```yaml
-role: worker
```

3.  **إنشاء المجموعة والتحقق من الحالة:**

```bash
kind create cluster --config=cluster kubectl cluster-info
kubectl cluster-info
```

4.  **ملفات تكوين Pod (Apache وNginx):**

**يستخدم:**كل من الخدمة والنشر موجودان في نفس yaml، لحفظهما في kubectl Apply -f. يمكنك أيضًا استخدام kustomize لتوفير وقت النشر.

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

أباتشي.يامل:

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

5.  **قم بإنشاء ConfigMap لتكوين nginx كوكيل عكسي (nginx-conf.yaml)**

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

**درجات:**

-   _التوجيه العامل\_تتحكم الاتصالات في الحد الأقصى لعدد الاتصالات المتزامنة التي يمكن معالجتها بواسطة عملية عاملة في Nginx. يجب أن يتم تحجيمها إلى حركة المرور، 1024 مثال على ذلك._
-   _تم تعيين منفذ Apache 80 إلى 8080 لتجنب التعارضات مع nginx pod._

6.  **تطبيق التكوينات على المجموعة:**

```bash
kubectl apply -f nginx.yaml
kubectl apply -f apache.yaml
kubectl apply -f nginx-conf.yaml
```

نحن نتحقق من أن كل شيء يسير على ما يرام

```bash
kubectl get pods
kubectl exec <nombre de tu pod de nginx> -- cat /etc/nginx/nginx.conf
```

7.  **إذا كان لدينا HTML مخصص، فيمكننا استخدامه لعرضه من خلال nginx والتأكد من أن كل شيء يعمل بشكل جيد حتى هذه اللحظة.**

_الملفات التي أتركها تسمى custom.html وcustom.css، لكن من الممكن أن تكون أي ملفات أخرى. إنها لعبة Dragon ball html رائعة جدًا._

-   **نقوم بإنشاء ConfigMap من ملفات html و css:**

```bash
kubectl create configmap html --from-file=custom.html --from-file=custom.css
```

ملاحظة: يتم أيضًا ترك ملف html.yaml كـ ConfigMap ليتم تطبيقه مع kubectl

```bash
apply -f html.yaml
```

_وهو يعادل الأمر السابق._

-   **نقوم بتحديث ملف apache.yaml، وإنشاء نقطة تحميل وتحديد الحجم المطلوب استخدامه:**

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

-   **نطبق التكوينات:**

```bash
kubectl apply -f apache.yaml
```

-   **نتحقق من تحميل كل شيء وأن الوكيل العكسي يعمل بشكل صحيح:**

```bash
kubectl exec <nombre de tu pod de nginx> -- curl localhost/custom.html
```

8.  **الآن يجب علينا تكوين هذا بشكل صحيح.**

**ومن خلال localhost:30000 يمكننا الوصول إلى صفحة الويب custom.html الخاصة بنا**

9.  **إذا سار كل شيء على ما يرام حتى هذه اللحظة، فهذا رائع، فهذا ما ينبغي أن يكون. بخلاف ذلك، فقد تركت ملف kustomization.yaml الذي يستخدم kustomize لإنشاء كل شيء تلقائيًا. إذا حدث خطأ ما، فاتبع الخطوات التالية:**

```bash
kind delete cluster –-name=<nombreDeTuCluster>
kind create cluster --config=cluster-config.yaml --name=<nombre-que-quieras>
kubectl apply -k .
```

**كل شيء جاهز. قم بإجراء الفحوصات المذكورة أعلاه (nginx.conf، localhost:30000، وما إلى ذلك) ملاحظة:**

-   **كن حذرًا عند النسخ واللصق، فالنصوص البرمجية لا تُنسخ دائمًا بشكل جيد.**
-   **أعلم أن هذا كان سيصبح جيدًا عاجلاً، لكن علينا أن نراجع كل شيء من البداية**😊**.**

**---------------------------------- لوحة تحكم K8S -------------- ---------------------------**

**ما تتم مناقشته في هذا القسم ليس تكوين Istio، بل تكوين لوحة معلومات K8s للنوع. من الجيد جدًا رؤية المقاييس ورؤية حالة المجموعة (مزيد من المعلومات في \[[هتبص://إيست.إيه/لاتست/دكس/ستوب/بلطفرم](https://istio.io/latest/docs/setup/platform)- الإعداد/النوع/#setup-dashboard-ui-for-kind):**]([هتبص://إيست.إيه/لاتست/دكس/ستوب/بلطفرمستب/كند/#ستبدشبردفركند](https://istio.io/latest/docs/setup/platform-setup/kind/#setup-dashboard-ui-for-kind))\*\*

1.  **نقوم بنشر نشر لوحة المعلومات:**

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommende d.yaml --validate=false
```

2.  \*\*نتحقق من أن الكبسولة متاحة وأنه تم إنشاؤها بشكل صحيح:

```bash
kubectl get pod -n kubernetes-dashboard
```

3.  **نقوم بإنشاء ServiceAccount وClusterRoleBinding لمنح وصول المسؤول إلى المجموعة:**

```bash
kubectl create serviceaccount -n kubernetes-dashboard admin-user

kubectl create clusterrolebinding  -n kubernetes-dashboard admin-user  --clusterrole cluster-admin --serviceaccount=kubernetes-dashboard:admin-user
```

4.  **نقوم بإنشاء الرمز المميز الذي سيطلب منا بعد ذلك تسجيل الدخول:**

```bash
token=$(kubectl  -n  kubernetes-dashboard  describe  secret  $(kubectl  -n  kubernetes - dashboard get secret | awk '/^admin-user/{print $1}') | awk '$1=="token:"{print $2}')
```

5.  **نتحقق من تخزينه بشكل صحيح في متغير الرمز المميز: echo $token**
6.  **يمكننا الوصول إلى لوحة التحكم من خلال واجهة سطر الأوامر (CLI) عن طريق كتابة:**

```bash
kubectl proxy
```

**يمكننا الآن الوصول من المتصفح على \[http&#x3A;//localhost:8001/api/v1/namespaces/kubernetes - Dashboard/services/https&#x3A;kubernetes-dashboard:/proxy/#/login**](http&#x3A;//localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https&#x3A;kubernetes-dashboard:/proxy/#/login)\*\*

7.  **يمكننا الوصول إلى لوحة معلومات المجموعة من الويب، بمجرد إدخال الرمز المميز (مثل الخدمات، وما إلى ذلك):**

**------------------------------------------------ جنكينز - -----------------------------------------**

1.  **لإكمال المجموعة، سنقوم بتقديم جينكينز أيضًا. سوف نقوم بإنشاء خدمة من النوع NodePort المعينة إلى hostPort 30001، كما سنرى. ملف yaml الذي يحتوي على النشر والخدمة هو:**

**جنكينز.يامل:**

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

2.  **في هذه المرحلة، سوف نتساءل أين سنكشف جنكينز. ستكون الفكرة هي القيام بذلك من خلال nginx في "location jenkins/" والوصول من خلال المضيف المحلي:30000/jenkins - سيكون عليك فقط تعديل nginx-conf.yaml وإضافته**


    location /jenkins {

        proxy\_pass http://<jenkinsPodUsedIp>:30001/;
        proxy\_set\_header Host $host;
        proxy\_set\_header X-Real-IP $remote\_addr;
        proxy\_set\_header X-Forwarded-For $proxy\_add\_x\_forwarded\_for; proxy\_set\_header X-Forwarded-Proto $scheme;

    }

_في حالتي، لا أستطيع أن أفعل ذلك بسبب مشاكل التوافق مع wsl2. للقيام بذلك، قمت بتعديل ملف الكتلة-config.yaml، وكتابة extraPortMappings الذي سنحتاج إليه لاحقًا. بالإضافة إلى ذلك، قمت بإضافة اثنين من العمال وأضفت علامة في الملف الرئيسي لإضافة وحدة تحكم الدخول لاحقًا:_

**الكتلة-config.yaml**

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

3.  **Ahora bien, puedes seguir con tu cluster y agregar  Jenkins. Si en algún momento te has perdido, hay un fichero llamado autoDeploy.sh que te levanta el escenario entero. Comenta las partes a las que no has llegado para probar a hacerlas tú y ejecuta:**

```bash
./autoDeploy.sh
```

4.  **أخيرًا، يمكننا الوصول إلى nginx من خلال localhost:30000 وJenkins من خلال localhost:30001. نحن نعرف بالفعل كيف يعمل nginx، فلننتقل إلى Jenkins:**

-   _فتح جينكينز:_**نحن بحاجة إلى كلمة المرور الأولية. نقوم بتنفيذ:**

```bash
kubectl get pods
kubectl exec <nombre-pod-jenkins> -- cat** /var/jenkins\_home/secrets/initialAdminPassword**
```

-   **نذهب إلى localhost:30001 وندخل كلمة المرور الأولية.**

-   **قم بتثبيت المكونات الإضافية الموصى بها، وأنشئ مستخدمًا إداريًا وجاهزًا!**

**درجات:**

-   **إذا كنت تريد استخدام اسم أكثر جاذبية من "localhost"، فيمكنك تعديل الملف /etc/hosts على جهازك عن طريق إضافة السطر 127.0.0.1<nombre-de-dominio-guay>. سوف تحصل على شيء مثل هذا:**

-   **يُنصح دائمًا بالعمل مع مساحات أسماء مختلفة (على سبيل المثال، pre، وpro، وdev، وما إلى ذلك). نحن لا نفعل ذلك في هذه الممارسة الموجزة حتى لا نزيد الأمر تعقيدًا، ولكن أفضل شيء نفعله هو فصل Jenkins عن الخدمات الأخرى، وما إلى ذلك.**

**----------------------------------------- هذا -------- -----------------------------**

**نمر إلى إستيو. نظرًا لخبرتي القليلة والوثائق التي قرأتها، يتسبب Istio في الكثير من المشكلات في العمل مع المجموعة المحلية نظرًا لأننا، من بين أمور أخرى، لا ندير حركة المرور من الخارج. ولذلك، فإن التكوينات التي سنقوم بها ليست معقدة بشكل مفرط، ولكنها بالأحرى توضح مدى فائدة الخدمة.**

**أولاً:**

-   _"البوابة" هي أحد مكونات Istio التي تعمل كنقطة دخول لحركة المرور الخارجية التي تدخل المجموعة._
-   _"VirtualService" هو كائن Istio الذي يسمح لك بتحديد كيفية توجيه حركة المرور من البوابة إلى الخدمات الخلفية في المجموعة._

10. **تثبيت Istio في المجموعة:**

-   **تنزيل وتثبيت Istio:**

```bash
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH
```

-   **تأكد من تثبيت CRDs مع:**

```bash
kubectl get crds | grep 'istio.io\|certmanager.k8s.io' | wc -l
```

-   **إذا حصلنا على 0، تنفيذ:**

```bash
istioctl install --set profile=default
```

-   **Comprobar que funciona  todo  y que se ha creado un ingress  Gateway  y un pod de istio:**

```bash
kubectl get pods -n istio-system
```

-   **قم بتمكين Istio لمساحة الاسم التي يتم فيها نشر كبسولات Apache وNginx وJenkins:**

```bash
kubectl label namespace default istio-injection=enabled
```

11. **لإجراء إعداد بسيط لـ Istio في هذا السيناريو، يمكننا إضافة موازن تحميل لخدمة nginx باستخدام التحكم في حركة مرور Istio. لذلك:**

-   **قم بإنشاء موازن تحميل لخدمة nginx. نقوم بإنشاء VirtualService وبوابة في Istio لـ nginx:**

**LoadBalancerNginx.yaml:**

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

**درجات:**

-   **من الناحية النظرية يجب أن نكون قادرين على الوصول إلى nginx من خلال http&#x3A;//<nodeIP>:30000. في الواقع، العمل على النوع المحلي يجعل الأمور أكثر صعوبة بالنسبة لنا نظرًا لأن بيئتنا لا تدعم موازنات الأحمال الخارجية. لا يمكن إصلاح ذلك دون تعديل ملف تكوين kubelet، وتكوين المجموعة، وما إلى ذلك. إذا تم دعم موازن خارجي، فسيكون الإجراء هو تعديل عمليات التصدير على النحو التالي (في حالتي بالنسبة لـ wsl2):**

```bash
export INGRESS_NAME=istio-ingressgateway
export INGRESS_NS=istio-system

export INGRESS_HOST=127.0.0.1

#check
kubectl get svc -n istio-system
echo "INGRESS_HOST=$INGRESS_HOST, INGRESS_PORT=$INGRESS_PORT"

export GATEWAY_URL=$INGRESS_HOST:$INGRESS_PORT
```

**ملف nginx-nodeport.yaml، في حالة رغبتك في العبث به، هو: nginx-nodeport.yaml:**

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

-   **من الممكن أن تضطر إلى إعادة تشغيل عمليات النشر (أو حذف القرون) بحيث يتم حقنها:**

```bash
kubectl rollout restart deployment nginx
kubectl rollout restart deployment apache
kubectl delete pods --all**
```

-   **تأكد من أن كل شيء يعمل بشكل جيد مع:**

```bash
istioctl analyze
kubectl get gateway
kubectl get vs
```

**--------------------------------------- كيالي ---------- ------------------------------**

**بافتراض أن لدينا بالفعل موازن تحميل يعيد توجيه كل شيء إلى الوكيل العكسي لـ nginx، ننتقل لرؤية الأداة التالية. Kiali هي أداة تتبع/لوحة معلومات Istio توفر تصورات وتحليلات لهيكل خدمة Istio ومعلومات حركة مرور الشبكة. يتم استخدامه عادةً عندما يتم تكوين Istio (مثل Grafana إذا تم تكوين Prometheus أو Kibana إذا تم تكوين Elastic-Search). لنقم بتثبيته:**

12. **المثبت:**

```bash
kubectl  apply  -f  https://raw.githubuserconten 1.17/samples/addons/kiali.yaml --validate=false**
```

13. **التحقق من التثبيت:**

```bash
kubectl -n istio-system get svc kiali
```

14. **استخدم لوحة القيادة:**

```bash
istioctl dashboard kiali
```

**خاتمة:**

**Istio هي خدمة كاملة جدًا يمكن دمجها مع Prometheus ولوحة تحكم Kubernetes نفسها والعديد من الخدمات والمنصات الأخرى. سنقوم بتحسين تكوينات Istio في المختبرات القادمة، حيث سنقوم، من بين أمور أخرى، بتثبيت Prometheus من خلال Istio، والتركيز أكثر على مراقبة المجموعة.**

**ملاحظات هامة:**

-   يمكن تجميع السيناريو بأكمله عن طريق تشغيل ملف autoDeploy.py، في حالة حدوث مشكلة. يقبل الملف إدخالاً واحدًا، وهو اسم المجموعة. إذا كنت تريد تركه افتراضيًا، فالاسم هو "trainingPath" (اضغط على Enter).

```bash
python3 autoDeploy.py
```

-   إذا كنت تستخدم wsl2 أو توزيعة Linux، فمن الأفضل استخدام ملف autoDeploy.sh، لأنه يتجنب المشاكل المحتملة مع عمليات تصدير python. في دليل فارغ عليك تنفيذ:

```bash
./autoDeploy.sh
```

-   من المهم تعديل إصدار Istio لتثبيته (الأحدث في[هتبص://إيست.إيه/دونلودصش](https://istio.io/downloadIstio))

**مراجع الاسم ذات الصلة:**

-   [هتبص://إيست.إيه/لاتست/دكس/تزقز/طرفكمنجمنة/انغرس/انغرسكنترل/#سينجندبرتسفثنجرسجتويسرفك](https://istio.io/latest/docs/tasks/traffic-management/ingress/ingress-control/#using-node-ports-of-the-ingress-gateway-service)

-   [هتبص://إيست.إيه/لاتست/دكس/تزقز/طرفكمنجمنة/انغرس/انغرسكنترل/#سينجندبرتسفثنجرسجتويسرفك](https://istio.io/latest/docs/tasks/traffic-management/ingress/ingress-control/#using-node-ports-of-the-ingress-gateway-service)

-   [هتبص://إيست.إيه/لاتست/دكس/كسمبلص/بكينفه/#ديترمنثنجرسبندبرة](https://istio.io/latest/docs/examples/bookinfo/#determine-the-ingress-ip-and-port)

-   [هتبص://إيست.إيه/لاتست/دكس/كسمبلص/بكينفه/#ديترمنثنجرسبندبرة](https://istio.io/latest/docs/examples/bookinfo/#determine-the-ingress-ip-and-port)
