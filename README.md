
## Build docker image
```sh
docker build --no-cache -t jkleve/auto-playlist:latest .
docker run -d -p 5000:5000 jkleve/auto-playlist
docker push jkleve/auto-playlist:latest
```

##### Other docker commands
```sh
# Remove <none> images
docker rmi $(docker images -f “dangling=true” -q)
```

## docker-compose
```sh
docker-compose exec <service> <cmd>

# Build images
docker-compose build --no-cache

# Push images
docker-compose push
```

## Push docker image
```sh
docker push jkleve/auto-playlist:latest
```

## Deploy app
```sh
# Deploy
kubectl apply -f auto-playlist-deployment.yaml

# View
kubectl get deployments
kubectl get pods
kubectl get nodes

# Create load balancer
kubectl expose deployment auto-playlist-deployment --name=auto-playlist-service --type=LoadBalancer --port 80 --target-port 5000

# View services and external-IP
kubectl get service

# Context & config
kubectl config view
kubectl config get-contexts
kubectl config current-context
kubectl config set-context <cluster>

# Delete
kubectl delete pods --all
kubectl delete deployments flask-deployment
```

# Deploy
```sh
# Convert docker-compose.yaml to kubernetes manifests
kompose convert -o cfgs/k8s

# Deploy
cd cfgs/k8s
kubectl apply -f api-deployment.yaml,api-tcp-service.yaml,cluster-network-networkpolicy.yaml,plivo-deployment.yaml,plivo-service.yaml,plivo-tcp-service.yaml -n auto-playlist

# Forward ports
kubectl port-forward -n auto-playlist svc/api 5001:5001
kubectl port-forward -n auto-playlist svc/plivo 5002:5002

# Get ingress
kubectl describe ingress nginx-ingress -n auto-playlist

# Check health
http :5001/health/
http :5002/health/

# Clean-up
kubectl delete -f api-deployment.yaml,api-tcp-service.yaml,cluster-network-networkpolicy.yaml,plivo-deployment.yaml,plivo-service.yaml,plivo-tcp-service.yaml -n auto-playlist

# Run commmand
kubectl run curl --image=radial/busyboxplus:curl -i --tty

# Follow logs
kubectl log -f <pod id>
```


# Helm
```sh

# From cfgs/helm

# Install
helm install -n auto-playlist auto-playlist .

# Uninstall
helm install -n auto-playlist auto-playlist .
```

# ArgoCD Install
```sh
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Don't think this was needed. We can port forward
#kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'

# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo

# Forward localhost 8080 to the argocd server
kubectl -n argocd port-forward svc/argocd-server 8080:443

# Login
argocd login 127.0.0.1:8080

# After login you should be able to access the UI via the browser 
# You'll always need to forward the port though to do this
```