import os

services = [
    'api-gateway', 'user-service', 'search-service', 
    'booking-service', 'payment-service', 'notification-service'
]

# 1. Update Backend Dockerfiles & .dockerignore
dockerfile_content = """# Build Stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

# Production Stage
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app ./
USER node
EXPOSE {port}
CMD ["npm", "start"]
"""

dockerignore_content = """node_modules
.git
.env
helm
k8s
Dockerfile
README.md
"""

ports = {
    'api-gateway': 5000, 'user-service': 5001, 'search-service': 5002,
    'booking-service': 5003, 'payment-service': 5004, 'notification-service': 5005
}

for svc in services:
    path = os.path.join('backend', svc)
    # Dockerfile
    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(dockerfile_content.format(port=ports[svc]))
    # .dockerignore
    with open(os.path.join(path, '.dockerignore'), 'w') as f:
        f.write(dockerignore_content)

# Update Frontend Dockerfile & .dockerignore
frontend_dockerfile = """# Build Stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Serve Stage (using Vite preview for simple serving, or nginx)
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app ./
USER node
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
"""
with open('Dockerfile', 'w') as f:
    f.write(frontend_dockerfile)
with open('.dockerignore', 'w') as f:
    f.write(dockerignore_content)

# 2. Advanced Helm Configurations
deployment_template = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{{{ include "{name}.fullname" . }}}}
spec:
  replicas: {{{{ .Values.replicaCount }}}}
  selector:
    matchLabels:
      app: {{{{ include "{name}.fullname" . }}}}
  template:
    metadata:
      labels:
        app: {{{{ include "{name}.fullname" . }}}}
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
      containers:
        - name: {{{{ .Chart.Name }}}}
          image: "{{{{ .Values.image.repository }}}}:{{{{ .Values.image.tag | default .Chart.AppVersion }}}}"
          ports:
            - containerPort: {{{{ .Values.service.port }}}}
          envFrom:
            - configMapRef:
                name: {{{{ include "{name}.fullname" . }}}}-config
{env_secret}
          livenessProbe:
            tcpSocket:
              port: {{{{ .Values.service.port }}}}
            initialDelaySeconds: 15
            periodSeconds: 20
          readinessProbe:
            tcpSocket:
              port: {{{{ .Values.service.port }}}}
            initialDelaySeconds: 5
            periodSeconds: 10
"""

configmap_template = """apiVersion: v1
kind: ConfigMap
metadata:
  name: {{{{ include "{name}.fullname" . }}}}-config
data:
  NODE_ENV: "production"
  PORT: "{{{{ .Values.service.port }}}}"
{extra_data}
"""

for svc in services + ['frontend']:
    chart_dir = os.path.join('helm/charts', svc, 'templates')
    
    # Extra data for backend config maps
    extra_data = '  MONGO_URI: "mongodb://admin:secret@mongodb:27017"' if svc != 'frontend' and svc != 'api-gateway' else ''
    
    # Write ConfigMap
    with open(os.path.join(chart_dir, 'configmap.yaml'), 'w') as f:
        f.write(configmap_template.format(name=svc, extra_data=extra_data))
        
    # Overwrite Deployment
    env_secret = ""
    if svc != 'frontend' and svc != 'api-gateway':
        env_secret = """            - secretRef:
                name: mongodb-secret"""

    with open(os.path.join(chart_dir, 'deployment.yaml'), 'w') as f:
        f.write(deployment_template.format(name=svc, env_secret=env_secret))

# 3. MongoDB Advanced Config (StatefulSet/Deployment with PV, PVC, Secret)
mongo_chart = 'helm/charts/mongodb/templates'

mongo_secret = """apiVersion: v1
kind: Secret
metadata:
  name: mongodb-secret
type: Opaque
stringData:
  MONGO_INITDB_ROOT_USERNAME: "admin"
  MONGO_INITDB_ROOT_PASSWORD: "secretpassword123"
"""
with open(os.path.join(mongo_chart, 'secret.yaml'), 'w') as f:
    f.write(mongo_secret)

mongo_pvc = """apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mongodb-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
"""
with open(os.path.join(mongo_chart, 'pvc.yaml'), 'w') as f:
    f.write(mongo_pvc)

mongo_deploy = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongodb
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
        - name: mongodb
          image: "mongo:5.0"
          ports:
            - containerPort: 27017
          envFrom:
            - secretRef:
                name: mongodb-secret
          volumeMounts:
            - name: mongo-data
              mountPath: /data/db
      volumes:
        - name: mongo-data
          persistentVolumeClaim:
            claimName: mongodb-pvc
"""
with open(os.path.join(mongo_chart, 'deployment.yaml'), 'w') as f:
    f.write(mongo_deploy)

print("K8s and Docker hardening applied.")
