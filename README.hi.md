# k8sप्रशिक्षण

अपाचे, नग्नेक्स, जेनकिंस, इस्तियो, किआली (फिलहाल)

जाँच करना**_ट्रेनिंगपाथप्रोजेक्ट.पीडीएफ_**पूर्ण पढ़ने के लिए 😊

पूरे परिदृश्य को लागू करने के लिए निष्पादित करें:

```bash
./autoDeploy.sh
```

यदि आप इसे धीरे-धीरे खेलना चाहेंगे, तो बस:

```bash
git clone https://github.com/huzmgod/k8sTraining.git
cd k8sTraining
```

**_-----------------------------------------------------------------------------------------------------------------------_**

**_स्पैनिश पूर्ण README (छवियों के बिना, जो पीडीएफ में हैं):_**

**K8s का उपयोग करके Apache के लिए Nginx को रिवर्स प्रॉक्सी के रूप में सेट करना। जेनकिंस, इस्तियो, K8s डैशबोर्ड और किआली तैनात**

1.  **इंस्टालर प्रकार:[हत्तपः://काइंड.सिग्स.ख8स.ीो/डॉक्स/यूजर/क्विक-स्टार्ट/#इंस्टालेशन](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)**
2.  **क्लस्टर कॉन्फ़िगरेशन फ़ाइल बनाएं (cluster-config.yaml):**

क्लस्टर-config.yaml

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

**ग्रेड:**

-   एक्स्ट्रापोर्टमैपिंग उन वातावरणों के लिए महत्वपूर्ण है जो डॉकर डेस्कटॉप का उपयोग करते हैं, क्योंकि अन्यथा प्रकार का कॉन्फ़िगरेशन लोकलहोस्ट: 30000 (या 30000 से बड़ा कोई अन्य पोर्ट) के माध्यम से अपाचे (या अन्य) सर्वर से सामग्री तक पहुंचने से रोकता है। अधिक दस्तावेज़ के लिए:[हत्तपः://काइंड.सिग्स.ख8स.ीो/डॉक्स/यूजर/कॉन्फ़िगरेशन/#एक्स्ट्रा-पोर्ट-मप्पिंग्स](https://kind.sigs.k8s.io/docs/user/configuration/#extra-port-mappings)\*\*

-   श्रमिकों को लाइन के साथ जोड़ा जा सकता है

```yaml
-role: worker
```

3.  **क्लस्टर बनाएं और स्थिति जांचें:**

```bash
kind create cluster --config=cluster kubectl cluster-info
kubectl cluster-info
```

4.  **पॉड कॉन्फ़िगरेशन फ़ाइलें (अपाचे और Nginx):**

**उपयोग:**Kubectl apply -f पर बचत करने के लिए सेवा और परिनियोजन दोनों एक ही yaml में हैं। आप परिनियोजन समय बचाने के लिए कस्टमाइज़ का भी उपयोग कर सकते हैं।

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

अपाचे.yaml:

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

5.  **nginx को रिवर्स प्रॉक्सी के रूप में कॉन्फ़िगर करने के लिए कॉन्फिग मैप बनाएं (nginx-conf.yaml)**

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

**ग्रेड:**

-   _कार्यकर्ता निर्देश\_कनेक्शन एक साथ कनेक्शन की अधिकतम संख्या को नियंत्रित करता है जिसे Nginx कार्यकर्ता प्रक्रिया द्वारा नियंत्रित किया जा सकता है। इसे ट्रैफ़िक के अनुसार स्केल किया जाना चाहिए, 1024 एक उदाहरण है।_
-   _nginx पॉड के साथ टकराव से बचने के लिए अपाचे पोर्ट 80 को 8080 पर मैप किया गया है।_

6.  **क्लस्टर में कॉन्फ़िगरेशन लागू करें:**

```bash
kubectl apply -f nginx.yaml
kubectl apply -f apache.yaml
kubectl apply -f nginx-conf.yaml
```

हम जाँचते हैं कि सब कुछ ठीक चल रहा है

```bash
kubectl get pods
kubectl exec <nombre de tu pod de nginx> -- cat /etc/nginx/nginx.conf
```

7.  **यदि हमारे पास कस्टम HTML है तो हम इसे nginx के माध्यम से देखने के लिए उपयोग कर सकते हैं और सुनिश्चित कर सकते हैं कि इस बिंदु तक सब कुछ ठीक से काम कर रहा है।**

_मेरे द्वारा छोड़ी गई फ़ाइलों को कस्टम.एचटीएमएल और कस्टम.सीएसएस कहा जाता है, लेकिन वे कोई अन्य भी हो सकती हैं। यह एक ड्रैगन बॉल html है जो बहुत बढ़िया है।_

-   **हम html और css फ़ाइलों से कॉन्फ़िगमैप बनाते हैं:**

```bash
kubectl create configmap html --from-file=custom.html --from-file=custom.css
```

ध्यान दें: html.yaml फ़ाइल को kubectl के साथ लागू करने के लिए कॉन्फ़िगमैप के रूप में भी छोड़ा गया है

```bash
apply -f html.yaml
```

_यह पिछले कमांड के बराबर है।_

-   **हम apache.yaml को अपडेट करते हैं, एक माउंट पॉइंट बनाते हैं और उपयोग करने के लिए वॉल्यूम निर्दिष्ट करते हैं:**

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

-   **हम कॉन्फ़िगरेशन लागू करते हैं:**

```bash
kubectl apply -f apache.yaml
```

-   **हम जाँचते हैं कि सब कुछ लोड हो गया है और रिवर्स प्रॉक्सी सही ढंग से काम कर रही है:**

```bash
kubectl exec <nombre de tu pod de nginx> -- curl localhost/custom.html
```

8.  **अब तक हमें इसे सही ढंग से कॉन्फ़िगर कर लेना चाहिए।**

**और localhost:30000 के माध्यम से हम अपने customer.html वेब पेज तक पहुंच पाएंगे**

9.  **यदि अब तक सब कुछ ठीक रहा है, तो बढ़िया है, यही होना चाहिए। अन्यथा, मैंने एक kustomization.yaml फ़ाइल छोड़ी है जो सब कुछ स्वचालित रूप से बनाने के लिए kustomize का उपयोग करती है। यदि कुछ गलत हुआ हो, तो निम्न चरणों का पालन करें:**

```bash
kind delete cluster –-name=<nombreDeTuCluster>
kind create cluster --config=cluster-config.yaml --name=<nombre-que-quieras>
kubectl apply -k .
```

**सब तैयार। उपरोक्त जाँच करें (nginx.conf, localhost:30000, आदि) नोट:**

-   **कॉपी और पेस्ट करते समय सावधान रहें, स्क्रिप्ट हमेशा अच्छी तरह से कॉपी नहीं होती हैं।**
-   **मैं जानता हूं कि यह पहले ही अच्छा होता, लेकिन हमें शुरू से ही हर चीज पर विचार करना होगा**😊**.**

**---------------------------------- K8S डैशबोर्ड---------------- ----------------------**

**इस अनुभाग में जो चर्चा की गई है वह इस्तियो कॉन्फ़िगरेशन नहीं है, बल्कि K8s डैशबोर्ड का कॉन्फ़िगरेशन है। मेट्रिक्स देखना और क्लस्टर की स्थिति देखना बहुत अच्छा है (अधिक जानकारी \[में)[हत्तपः://िस्तिओ.ीो/लेटेस्ट/डॉक्स/सेटअप/प्लेटफार्म](https://istio.io/latest/docs/setup/platform)- सेटअप/तरह/#सेटअप-डैशबोर्ड-यूआई-फॉर-काइंड):**]([हत्तपः://िस्तिओ.ीो/लेटेस्ट/डॉक्स/सेटअप/प्लेटफार्म-सेटअप/काइंड/#सेटअप-डैशबोर्ड-ुइ-फॉर-काइंड](https://istio.io/latest/docs/setup/platform-setup/kind/#setup-dashboard-ui-for-kind))\*\*

1.  **हम डैशबोर्ड परिनियोजन तैनात करते हैं:**

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommende d.yaml --validate=false
```

2.  \*\*हम सत्यापित करते हैं कि पॉड उपलब्ध है और इसे सही ढंग से बनाया गया है:

```bash
kubectl get pod -n kubernetes-dashboard
```

3.  **हम क्लस्टर तक व्यवस्थापक पहुंच प्रदान करने के लिए एक ServiceAccount और ClusterRoleBinding बनाते हैं:**

```bash
kubectl create serviceaccount -n kubernetes-dashboard admin-user

kubectl create clusterrolebinding  -n kubernetes-dashboard admin-user  --clusterrole cluster-admin --serviceaccount=kubernetes-dashboard:admin-user
```

4.  **हम टोकन जनरेट करते हैं जो फिर हमसे लॉग इन करने के लिए कहेगा:**

```bash
token=$(kubectl  -n  kubernetes-dashboard  describe  secret  $(kubectl  -n  kubernetes - dashboard get secret | awk '/^admin-user/{print $1}') | awk '$1=="token:"{print $2}')
```

5.  **हम जांचते हैं कि इसे टोकन वेरिएबल: इको $टोकन में सही ढंग से संग्रहीत किया गया है**
6.  **हम सीएलआई के माध्यम से डैशबोर्ड तक यह लिखकर पहुंच सकते हैं:**

```bash
kubectl proxy
```

**अब हम ब्राउज़र से \[http&#x3A;//localhost:8001/api/v1/namespaces/kubernetes - Dashboard/services/https&#x3A;kubernetes-dashboard:/proxy/#/login पर पहुंच सकते हैं**](http&#x3A;//localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https&#x3A;kubernetes-dashboard:/proxy/#/login)\*\*

7.  **एक बार टोकन दर्ज करने के बाद, हम वेब से क्लस्टर डैशबोर्ड तक पहुंचते हैं (जैसे सेवाएं, आदि):**

**------------------------------------------------ जेनकींस - ------------------------------------------------**

1.  **क्लस्टर को पूरा करने के लिए, हम जेनकिंस को भी पेश करने जा रहे हैं। हम होस्टपोर्ट 30001 पर मैप किए गए नोडपोर्ट प्रकार की एक सेवा बनाएंगे, जैसा कि हम देखेंगे। yaml फ़ाइल जिसमें परिनियोजन और सेवा शामिल है वह है:**

**जेनकींस.yaml:**

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

2.  **इस बिंदु पर, हम सोच रहे होंगे कि हम जेनकिंस को कहां बेनकाब करने जा रहे हैं। विचार यह होगा कि इसे "स्थान जेनकींस/" में nginx के माध्यम से किया जाए और लोकलहोस्ट:30000/जेनकींस के माध्यम से एक्सेस किया जाए - आपको केवल nginx-conf.yaml को संशोधित करना होगा और जोड़ना होगा**


    location /jenkins {

        proxy\_pass http://<jenkinsPodUsedIp>:30001/;
        proxy\_set\_header Host $host;
        proxy\_set\_header X-Real-IP $remote\_addr;
        proxy\_set\_header X-Forwarded-For $proxy\_add\_x\_forwarded\_for; proxy\_set\_header X-Forwarded-Proto $scheme;

    }

_मेरे मामले में, wsl2 के साथ संगतता समस्याओं के कारण मैं इसे इस तरह नहीं कर सकता। ऐसा करने के लिए, मैंने क्लस्टर-config.yaml फ़ाइल को संशोधित किया है, एक्स्ट्रापोर्टमैपिंग लिख रहा हूं जिसकी हमें बाद में आवश्यकता होगी। इसके अतिरिक्त, मैंने कुछ कर्मचारियों को जोड़ा है और बाद में एक इनग्रेस कंट्रोलर जोड़ने के लिए मास्टर में एक टैग जोड़ा है:_

**क्लस्टर-config.yaml**

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

3.  **अब, आप अपने क्लस्टर को जारी रख सकते हैं और जेनकींस जोड़ सकते हैं। यदि किसी भी बिंदु पर आप खो गए हैं, तो autoDeploy.sh नामक एक फ़ाइल है जो आपको संपूर्ण परिदृश्य दिखाती है। उन हिस्सों पर टिप्पणी करें जिन तक आप नहीं पहुँचे हैं ताकि आप उन्हें स्वयं करने का प्रयास कर सकें और निष्पादित कर सकें:**

```bash
./autoDeploy.sh
```

4.  **अंत में, हम nginx को localhost:30000 के माध्यम से और जेनकिंस को localhost:30001 के माध्यम से एक्सेस कर सकते हैं। हम पहले से ही जानते हैं कि nginx कैसे चलता है, आइए जेनकींस पर चलते हैं:**

-   _जेनकींस अनलॉक करें:_**हमें प्रारंभिक पासवर्ड की आवश्यकता है. हम निष्पादित करते हैं:**

```bash
kubectl get pods
kubectl exec <nombre-pod-jenkins> -- cat** /var/jenkins\_home/secrets/initialAdminPassword**
```

-   **हम लोकलहोस्ट:30001 पर जाते हैं और प्रारंभिक पासवर्ड दर्ज करते हैं।**

-   **अनुशंसित प्लगइन्स इंस्टॉल करें, अपना व्यवस्थापक उपयोगकर्ता बनाएं और तैयार!**

**ग्रेड:**

-   **यदि आप "लोकलहोस्ट" से अधिक आकर्षक नाम का उपयोग करना चाहते हैं, तो आप अपनी मशीन पर 127.0.0.1 लाइन जोड़कर /etc/hosts फ़ाइल को संशोधित कर सकते हैं।<nombre-de-dominio-guay>. आपको कुछ इस तरह मिलेगा:**

-   **हमेशा अलग-अलग नामस्थानों (जैसे प्री, प्रो, डेव, आदि) के साथ काम करने की सलाह दी जाती है। हम इस संक्षिप्त अभ्यास में ऐसा नहीं करते हैं ताकि मामला और अधिक जटिल न हो, लेकिन सबसे अच्छी बात यह होगी कि जेनकिंस को अन्य सेवाओं आदि से अलग कर दिया जाए।**

**----------------------------------------- यह -------- --------------------------------**

**हम इस्तियो के पास जाते हैं। मेरे थोड़े से अनुभव और मेरे द्वारा पढ़े गए दस्तावेज़ के कारण, इस्तियो स्थानीय क्लस्टर के साथ काम करने में बहुत सारी समस्याएं पैदा करता है क्योंकि, अन्य बातों के अलावा, हम बाहर से आने वाले ट्रैफ़िक का प्रबंधन नहीं करते हैं। इसलिए, जो कॉन्फ़िगरेशन हम बनाने जा रहे हैं वह अत्यधिक जटिल नहीं हैं, बल्कि यह दर्शाते हैं कि सेवा की उपयोगिता क्या है।**

**सबसे पहले:**

-   _"गेटवे" एक इस्तियो घटक है जो क्लस्टर में प्रवेश करने वाले बाहरी ट्रैफ़िक के लिए प्रवेश बिंदु के रूप में कार्य करता है।_
-   _"वर्चुअल सर्विस" एक इस्तियो ऑब्जेक्ट है जो आपको यह परिभाषित करने की अनुमति देता है कि गेटवे से क्लस्टर में बैक-एंड सेवाओं तक ट्रैफ़िक को कैसे निर्देशित किया जाना चाहिए।_

10. **क्लस्टर में इस्तियो स्थापित करना:**

-   **इस्तियो डाउनलोड और इंस्टॉल करें:**

```bash
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH
```

-   **जांचें कि सीआरडी इसके साथ स्थापित हैं:**

```bash
kubectl get crds | grep 'istio.io\|certmanager.k8s.io' | wc -l
```

-   **यदि हमें 0 मिलता है, तो निष्पादित करें:**

```bash
istioctl install --set profile=default
```

-   **जांचें कि सब कुछ काम करता है और एक प्रवेश द्वार और एक इस्तिओ पॉड बनाया गया है:**

```bash
kubectl get pods -n istio-system
```

-   **उस नेमस्पेस के लिए इस्तियो को सक्षम करें जिसमें अपाचे, नेग्नेक्स और जेनकिंस पॉड तैनात हैं:**

```bash
kubectl label namespace default istio-injection=enabled
```

11. **इस परिदृश्य में एक सरल इस्तियो सेटअप करने के लिए, हम इस्तियो ट्रैफ़िक नियंत्रण का उपयोग करके nginx सेवा के लिए एक लोड बैलेंसर जोड़ सकते हैं। इसके लिए:**

-   **nginx सेवा के लिए एक लोड बैलेंसर उत्पन्न करें। हम nginx के लिए इस्तियो में एक वर्चुअल सर्विस और एक गेटवे बनाते हैं:**

**लोडबैलेंसरNginx.yaml:**

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

**ग्रेड:**

-   **सैद्धांतिक रूप से हमें http&#x3A;// के माध्यम से nginx तक पहुंचने में सक्षम होना चाहिए<nodeIP>:30000. वास्तव में, स्थानीय प्रकार पर काम करना हमारे लिए चीजों को और अधिक कठिन बना देता है क्योंकि हमारा पर्यावरण बाहरी लोड बैलेंसर्स का समर्थन नहीं करता है। क्यूबलेट कॉन्फ़िगरेशन फ़ाइल, क्लस्टर-कॉन्फिगरेशन इत्यादि को संशोधित किए बिना इसे ठीक नहीं किया जा सकता है। यदि एक बाहरी बैलेंसर समर्थित था, तो प्रक्रिया निम्नानुसार निर्यात को संशोधित करने की होगी (मेरे मामले में wsl2 के लिए):**

```bash
export INGRESS_NAME=istio-ingressgateway
export INGRESS_NS=istio-system

export INGRESS_HOST=127.0.0.1

#check
kubectl get svc -n istio-system
echo "INGRESS_HOST=$INGRESS_HOST, INGRESS_PORT=$INGRESS_PORT"

export GATEWAY_URL=$INGRESS_HOST:$INGRESS_PORT
```

**यदि आप इसके साथ खिलवाड़ करना चाहते हैं तो nginx-nodeport.yaml फ़ाइल है: nginx-nodeport.yaml:**

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

-   **यह संभव है कि आपको तैनाती को फिर से शुरू करना होगा (या पॉड्स को हटाना होगा) ताकि उनमें आईस्टियो इंजेक्ट किया जा सके:**

```bash
kubectl rollout restart deployment nginx
kubectl rollout restart deployment apache
kubectl delete pods --all**
```

-   **जांचें कि सब कुछ ठीक से काम करता है:**

```bash
istioctl analyze
kubectl get gateway
kubectl get vs
```

**------------------------------------------------ किआली -------- --------------------------------**

**यह मानते हुए कि हमारे पास पहले से ही एक लोड बैलेंसर है जो सब कुछ nginx रिवर्स-प्रॉक्सी पर रीडायरेक्ट करता है, हम निम्नलिखित टूल को देखने के लिए आगे बढ़ते हैं। किआली एक इस्तियो ट्रैकिंग/डैशबोर्ड टूल है जो इस्तियो सेवा टोपोलॉजी और नेटवर्क ट्रैफ़िक जानकारी का विज़ुअलाइज़ेशन और विश्लेषण प्रदान करता है। इसका उपयोग आम तौर पर तब किया जाता है जब इस्तियो को कॉन्फ़िगर किया जाता है (जैसे कि यदि प्रोमेथियस कॉन्फ़िगर किया गया है तो ग्राफाना या यदि इलास्टिक-सर्च कॉन्फ़िगर किया गया है तो किबाना)। आइए इसे इंस्टॉल करें:**

12. **इंस्टालर किअलि:**

```bash
kubectl  apply  -f  https://raw.githubuserconten 1.17/samples/addons/kiali.yaml --validate=false**
```

13. **स्थापना की जाँच करें:**

```bash
kubectl -n istio-system get svc kiali
```

14. **डैशबोर्ड का उपयोग करें:**

```bash
istioctl dashboard kiali
```

**निष्कर्ष:**

**इस्तियो एक बहुत ही संपूर्ण सेवा है जिसे प्रोमेथियस, कुबेरनेट्स डैशबोर्ड और कई अन्य सेवाओं और प्लेटफार्मों के साथ एकीकृत किया जा सकता है। हम अगली प्रयोगशालाओं में इस्तियो कॉन्फ़िगरेशन में सुधार करेंगे, जहां अन्य चीजों के अलावा, हम इस्तियो के माध्यम से प्रोमेथियस स्थापित करेंगे, और क्लस्टर निगरानी पर अधिक ध्यान केंद्रित करेंगे।**

**महत्वपूर्ण लेख:**

-   यदि कभी कोई समस्या हो, तो संपूर्ण परिदृश्य को autoDeploy.py फ़ाइल चलाकर एकत्रित किया जा सकता है। फ़ाइल एकल इनपुट स्वीकार करती है, जो क्लस्टर का नाम है। यदि आप इसे डिफ़ॉल्ट के रूप में छोड़ना चाहते हैं, तो नाम "ट्रेनिंगपाथ" है (एंटर दबाएं)।

```bash
python3 autoDeploy.py
```

-   यदि आप wsl2 या Linux डिस्ट्रो का उपयोग कर रहे हैं, तो autoDeploy.sh फ़ाइल का उपयोग करना बेहतर है, क्योंकि यह पायथन निर्यात के साथ संभावित समस्याओं से बचाता है। एक खाली निर्देशिका में आपको निष्पादित करना होगा:

```bash
./autoDeploy.sh
```

-   (नवीनतम) स्थापित करने के लिए इस्तियो के संस्करण को संशोधित करना महत्वपूर्ण है[हत्तपः://िस्तिओ.ीो/डौन्लोडिस्टिव](https://istio.io/downloadIstio))

**प्रासंगिक इस्तियो संदर्भ:**

-   [हत्तपः://िस्तिओ.ीो/लेटेस्ट/डॉक्स/टास्कस/ट्रैफिक-मैनेजमेंट/इन्ग्रेस्स/इन्ग्रेस्स-कण्ट्रोल/#ुसिंग-नोड-पोर्ट्स-ऑफ़-थे-इन्ग्रेस्स-गेटवे-सर्विस](https://istio.io/latest/docs/tasks/traffic-management/ingress/ingress-control/#using-node-ports-of-the-ingress-gateway-service)

-   [हत्तपः://िस्तिओ.ीो/लेटेस्ट/डॉक्स/टास्कस/ट्रैफिक-मैनेजमेंट/इन्ग्रेस्स/इन्ग्रेस्स-कण्ट्रोल/#ुसिंग-नोड-पोर्ट्स-ऑफ़-थे-इन्ग्रेस्स-गेटवे-सर्विस](https://istio.io/latest/docs/tasks/traffic-management/ingress/ingress-control/#using-node-ports-of-the-ingress-gateway-service)

-   [हत्तपः://िस्तिओ.ीो/लेटेस्ट/डॉक्स/एक्साम्प्लेस/बुकइंफो/#डेटर्मिने-थे-इन्ग्रेस्स-िप-एंड-पोर्ट](https://istio.io/latest/docs/examples/bookinfo/#determine-the-ingress-ip-and-port)

-   [हत्तपः://िस्तिओ.ीो/लेटेस्ट/डॉक्स/एक्साम्प्लेस/बुकइंफो/#डेटर्मिने-थे-इन्ग्रेस्स-िप-एंड-पोर्ट](https://istio.io/latest/docs/examples/bookinfo/#determine-the-ingress-ip-and-port)
