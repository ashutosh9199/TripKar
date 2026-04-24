import os

services = [
    'frontend', 'api-gateway', 'user-service', 'search-service', 
    'booking-service', 'payment-service', 'notification-service', 'mongodb'
]

hpa_template = """apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{{{ include "{name}.fullname" . }}}}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: {{{{ if .Values.useStatefulSet }}}}StatefulSet{{{{ else }}}}Deployment{{{{ end }}}}
    name: {{{{ include "{name}.fullname" . }}}}
  minReplicas: {{{{ .Values.autoscaling.minReplicas }}}}
  maxReplicas: {{{{ .Values.autoscaling.maxReplicas }}}}
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{{{ .Values.autoscaling.targetCPUUtilizationPercentage }}}}
"""

statefulset_template = """{{{{- if .Values.useStatefulSet }}}}
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: {{{{ include "{name}.fullname" . }}}}
spec:
  serviceName: {{{{ include "{name}.fullname" . }}}}
  replicas: {{{{ .Values.replicaCount }}}}
  selector:
    matchLabels:
      app: {{{{ include "{name}.fullname" . }}}}
  template:
    metadata:
      labels:
        app: {{{{ include "{name}.fullname" . }}}}
    spec:
      containers:
        - name: {{{{ .Chart.Name }}}}
          image: "{{{{ .Values.image.repository }}}}:{{{{ .Values.image.tag | default .Chart.AppVersion }}}}"
          ports:
            - containerPort: {{{{ .Values.service.port }}}}
          resources:
            requests:
              cpu: {{{{ .Values.resources.requests.cpu }}}}
              memory: {{{{ .Values.resources.requests.memory }}}}
            limits:
              cpu: {{{{ .Values.resources.limits.cpu }}}}
              memory: {{{{ .Values.resources.limits.memory }}}}
{{{{- end }}}}
"""

gateway_template = """{{{{- if .Values.gateway.enabled }}}}
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: {{{{ include "{name}.fullname" . }}}}-gateway
spec:
  gatewayClassName: {{{{ .Values.gateway.className }}}}
  listeners:
  - name: http
    protocol: HTTP
    port: 80
{{{{- end }}}}
"""

httproute_template = """apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: {{{{ include "{name}.fullname" . }}}}
spec:
{{{{- if .Values.gateway.enabled }}}}
  parentRefs:
  - name: {{{{ include "{name}.fullname" . }}}}-gateway
{{{{- end }}}}
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: {{{{ .Values.route.path }}}}
    backendRefs:
    - name: {{{{ include "{name}.fullname" . }}}}
      port: {{{{ .Values.service.port }}}}
"""

for svc in services:
    chart_dir = os.path.join('helm/charts', svc)
    templates_dir = os.path.join(chart_dir, 'templates')
    
    # 1. HPA
    with open(os.path.join(templates_dir, 'hpa.yaml'), 'w') as f:
        f.write(hpa_template.format(name=svc))
        
    # 2. StatefulSet
    with open(os.path.join(templates_dir, 'statefulset.yaml'), 'w') as f:
        f.write(statefulset_template.format(name=svc))
        
    # 3. Gateway & HTTPRoute
    with open(os.path.join(templates_dir, 'gateway.yaml'), 'w') as f:
        f.write(gateway_template.format(name=svc))
        
    with open(os.path.join(templates_dir, 'httproute.yaml'), 'w') as f:
        f.write(httproute_template.format(name=svc))
        
    # 4. Modify Deployment (Add if condition and resources)
    deploy_path = os.path.join(templates_dir, 'deployment.yaml')
    with open(deploy_path, 'r') as f:
        content = f.read()
    
    if 'resources:' not in content:
        # Insert resources block before livenessProbe or volumeMounts or envFrom
        parts = content.split('ports:')
        if len(parts) > 1:
            port_part = parts[1].split('envFrom:', 1)
            split_keyword = 'envFrom:'
            if len(port_part) == 1:
                port_part = parts[1].split('volumeMounts:', 1)
                split_keyword = 'volumeMounts:'
            if len(port_part) == 1:
                port_part = parts[1].split('livenessProbe:', 1)
                split_keyword = 'livenessProbe:'
                
            if len(port_part) > 1:
                new_content = parts[0] + 'ports:' + port_part[0] + """          resources:
            requests:
              cpu: {{ .Values.resources.requests.cpu }}
              memory: {{ .Values.resources.requests.memory }}
            limits:
              cpu: {{ .Values.resources.limits.cpu }}
              memory: {{ .Values.resources.limits.memory }}\n          """ + split_keyword + port_part[1]
                content = new_content
                
    if '{{- if not .Values.useStatefulSet }}' not in content:
        content = '{{- if not .Values.useStatefulSet }}\n' + content + '\n{{- end }}\n'
        
    with open(deploy_path, 'w') as f:
        f.write(content)
        
    # 5. Append values to values.yaml
    values_path = os.path.join(chart_dir, 'values.yaml')
    with open(values_path, 'a') as f:
        f.write(f"""
useStatefulSet: false

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 200m
    memory: 256Mi

autoscaling:
  minReplicas: 1
  maxReplicas: 5
  targetCPUUtilizationPercentage: 80

gateway:
  enabled: true
  className: "eg"

route:
  path: "/"
""")

    # 6. Create local .env file
    if svc != 'mongodb' and svc != 'frontend':
        env_dir = os.path.join('backend', svc)
        os.makedirs(env_dir, exist_ok=True)
        with open(os.path.join(env_dir, '.env'), 'w') as f:
            f.write(f"PORT=5000\nNODE_ENV=development\nMONGO_URI=mongodb://admin:secretpassword123@localhost:27017\n")
            
print("Advanced K8s resources applied to all charts.")
