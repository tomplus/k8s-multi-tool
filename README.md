# k8s-multi-tool

Set of tools to manage your Kubernetes clusters.

# Requirements

* Python >= 3.5.2
* [kubernetes_asyncio](https://github.com/tomplus/kubernetes_asyncio)

# Instalation

This application is distributed as a Python package. You can install it globally
in your system:

```
pip install k8smtool
```

or in the virtual environment:

```
# create virtalenv
virtualenv -ppython3 env

# activate
. env/bin/activate

# instalation
pip install k8smtool
``

# Usage

All scripts read the confguration from `.kube/config` or from a file defined by `KUBECONFIG` as _kubectl_ does it.

Common arguments:

A positional argument - `FILTER`, which exists in some scripts can have values:
* `@namespace` - get objects from `namespace` only
* `~name` - get objects with name like `name*`
* `labe~value` - get objects which has `label` equals `value`
This argument can be joined and repeated like this `@namespace1 @namespace2 ~my-pod-name stage~dev`


## Actions on PODs

Script `pod.py` can list pods, images, execute commands or print logs from PODs.

```
usage: pod.py [-h] [--cmd CMD] [--batch-size BATCH_SIZE] [--follow]
              [--lines LINES]
              {delete-broken,exec,images,ls,tail} [filters [filters ...]]

Execute actions on pods

positional arguments:
  {delete-broken,exec,images,ls,tail}
                        command to execute
  filters               @namespace, ~name, label-name~value

optional arguments:
  -h, --help            show this help message and exit

Option for `exec` command::
  --cmd CMD             command to execute
  --batch-size BATCH_SIZE
                        batch size

Option for `tail` command::
  --follow              follow logs
  --lines LINES         show the last lines
```

### list pods

```
# all pods from all namespaces
pod.py ls

# pods from my-namespace
pod.py ls @my-namespace

# pods with name like "dns"
pod.py ls ~dns

# pods with label team=bears
pod.py ls team~bears

```

Example output:

```
NAMESPACE    PODS                                                 VERSION                         STATUS   CONDITIONS                      NODE
kube-system  event-exporter-v0.1.9-5cfff98cdb-9ksr6               v0.1.9;v0.2.2                   Running  Initialized+PodScheduled+Ready  cluster-1-default-pool-b43b0116-j0vb
kube-system  fluentd-gcp-v2.0.17-cffq6                            2.0.17;v0.2.2                   Running  Initialized+PodScheduled+Ready  cluster-1-default-pool-b43b0116-j0vb
kube-system  fluentd-gcp-v2.0.17-ltfff                            2.0.17;v0.2.2                   Running  Initialized+PodScheduled+Ready  cluster-1-default-pool-b43b0116-mnpm
kube-system  heapster-v1.5.2-56fb496f65-ffffs                     v1.5.2;v0.2.2;1.8.1             Running  Initialized+PodScheduled+Ready  cluster-1-default-pool-b43b0116-j0vb
kube-system  kube-dns-56dc69f5bd-mmffw                            1.14.10;1.14.10;v0.2.3;1.14.10  Running  Initialized+PodScheduled+Ready  cluster-1-default-pool-b43b0116-mnpm
kube-system  kube-dns-autoscaler-7db4ffb9b7-f5hbx                 1.1.2-r2                        Running  Initialized+PodScheduled+Ready  cluster-1-default-pool-b43b0116-j0vb
kube-system  kube-proxy-cluster-1-default-pool-b4ff0116-mfxf      v1.9.7-gke.5                    Running  Initialized+PodScheduled+Ready  cluster-1-default-pool-b43b0116-mmx0
kube-system  kubernetes-dashboard-85c74f8997-kbfwf                v1.8.3                          Running  Initialized+PodScheduled+Ready  cluster-1-default-pool-b43b0116-mmx0
kube-system  metrics-server-v0.2.1-7f8dd98c8f-ftkfs               v0.2.1;1.8.1                    Running  Initialized+PodScheduled+Ready  cluster-1-default-pool-b43b0116-mnpm
```

Notice: VERSION contains version of images of all containers within POD.

### list used images

```
pod.py images @default
```

Example output:
```
IMAGE                                              NAMESACE  POD-STATUS
gcr.io/google-samples/hello-app:1.0                default   Running
quay.io/coreos/configmap-reload:v0.0.1             default   Running
quay.io/coreos/prometheus-config-reloader:v0.22.1  default   Running
quay.io/coreos/prometheus-operator:v0.22.1         default   Running
quay.io/prometheus/prometheus:v2.3.1               default   Running
tpimages/airly-exporter:latest                     default   Running
```

### send exec command to multiple pods

```
# exec command "date" on all pods from namespace default (in the same time)
pod.py exec @default --cmd date

# exec command in batch mode (eg. 2 pods at a time)
pod.py exec @default --cmd date --batch-size 2

# you will be asked about command
pod.py exec @default
```

### tail logs from multiple pods

```
# print out last 10 lines from all pods with names started with "kube-dns"
pod.py tail ~kube-dns --lines 10

# follow new logs
pod.py tail ~kube-dns --follow
```

### delete "broken" pods

```
# delete pods which are not in ready state, confirmation is needed
pod.py delete-broken
```

## Searching Kubernetes' objects

Script `search.py` searches Kubernetes objects.

```
usage: search.py [-h] query [filters [filters ...]]

Search objects

positional arguments:
  query       regexp pattern
  filters     @namespace, ~name, label-name~value

optional arguments:
  -h, --help  show this help message and exit
```

Example:

```
# list objects which contains phrase "prometheus" in defintion
search.py prometheus

# list objects which have defined port=8080
search.py "port.*?8080"
```

Output:

```
NAMESPACE    TYPE       OBJECT                                RESULT
default      pod        prometheus-operator-6dd95b9d7b-gghrf  'ports': [{'container_port': 8080,
kube-system  endpoints  default-http-backend                  'ports': [{'name': 'http', 'port': 8080, 'protoco
kube-system  pod        l7-default-backend-6497bcdb4d-bvwhq   'port': 8080,
kube-system  service    default-http-backend                  ,"spec":{"ports":[{"name":"http","port":80,"protocol":"TCP","targetPort":8080}],"select
```

| RESULT contains this part of object's definition where searched phrase was found

## Recently created objects

Script `just.py` list newly created objects.

```
usage: just.py [-h] [--age AGE] [filters [filters ...]]

List objects created about 5 minutes ago

positional arguments:
  filters     @namespace, ~name, label-name~value

optional arguments:
  -h, --help  show this help message and exit
  --age AGE
```

Example:

```
# list objects created about 1h ago
just.py --age 3600
```
