
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
kubectl port-forward --namespace default <api container> 5001:5001
kubectl port-forward --namespace default <plivo container> 5002:5002

# Check health
http :5001/health/
http :5002/health/

# Clean-up
kubectl delete -f api-deployment.yaml,api-tcp-service.yaml,cluster-network-networkpolicy.yaml,plivo-deployment.yaml,plivo-service.yaml,plivo-tcp-service.yaml -n auto-playlist

# Run commmand
kubectl run curl --image=radial/busyboxplus:curl -i --tty

```


# Helm
```sh

# From cfgs/helm

# Install
helm install -n auto-playlist auto-playlist .

# Uninstall
helm install -n auto-playlist auto-playlist .
```