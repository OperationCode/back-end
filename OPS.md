# Deploying a new backend version

Once a release is built and deployed by CircleCI, deploy it to an environment using ArgoCD.

1. First, to connect to ArgoCD:
```
kubectl -n argocd port-forward service/argocd-server 8443:443 &
open https://localhost:8443
```
2. login - credentials are in 1password, or ask someone for help
3. pick up the new version in staging.
  - go to https://localhost:8443/applications/pyback-staging,
  - click the hamburger menu (3 dots, blue button), -> Details -> Parameters
  - update the images field with the build ID as the tag, like: `operationcode/back-end:staging-846`
  - as the new pods deploy, tail their logs to check for errors
  - validate the staging environment (notes below)
4. repeat those steps for the production environment

# Validating the staging environment

This requires a working node or docker environment.  I found docker to be easier and more reliable but that was me :shrug:

When you run the front-end repo in localdev mode, it automatically connects to the staging environment.
1. install dependencies:  `docker run -it -v ${PWD}:/src -w /src node:lts yarn`
2. run the dev server:  `docker run -it -v ${PWD}:/src -w /src -p 127.0.0.1:3000:3000/tcp node:lts yarn dev --hostname 0.0.0.0`
3. Connect to the dev server: `open http://localhost:3000`

# Certificate management with certbot

Certbot runs continously as a kube operator and refreshes certs for you.  To ensure it is working,
check the logs of the `cert-manager` pod, like:
```
kubectl -n cert-manager logs -f cert-manager-dcc48bf99-skhn7
```

Current version running is v0.10.1

if you need for some reason to upgrade:
1. read the release notes for all versions between current and desired, watch for breaking changes
2. ignore the instructions about helm and kubectly apply, one minor version at a time
```
kubectl apply \
  --validate=false \
  -f https://github.com/jetstack/cert-manager/releases/download/v0.10.1/cert-manager.yaml
```

certificates installed:
```
$ kubectl get Certificates --all-namespaces
NAMESPACE               NAME                READY   SECRET              AGE
monitoring              grafana-tls         True    grafana-tls         299d
operationcode-staging   back-end-tls        True    back-end-tls        264d
operationcode-staging   resources-api-tls   True    resources-api-tls   299d
operationcode           back-end-tls        True    back-end-tls        264d
operationcode           resources-api-tls   True    resources-api-tls   299d
```

