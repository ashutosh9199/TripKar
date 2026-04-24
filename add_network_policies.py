import os

backend_services = [
    'user-service', 'search-service', 'booking-service', 
    'payment-service', 'notification-service'
]

# 1. Edge Services (Allow all ingress)
edge_np = """apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {{{{ include "{name}.fullname" . }}}}
spec:
  podSelector:
    matchLabels:
      app: {{{{ include "{name}.fullname" . }}}}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - {{}}
  egress:
  - {{}}
"""

# 2. Internal Backend Services (Allow only from api-gateway)
internal_np = """apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {{{{ include "{name}.fullname" . }}}}
spec:
  podSelector:
    matchLabels:
      app: {{{{ include "{name}.fullname" . }}}}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: {api_gateway_name}
  egress:
  - {{}}
"""

# 3. Database (Allow only from backend services)
db_np = """apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {{{{ include "{name}.fullname" . }}}}
spec:
  podSelector:
    matchLabels:
      app: {{{{ include "{name}.fullname" . }}}}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
"""
for svc in backend_services:
    db_np += f"    - podSelector:\n        matchLabels:\n          app: tripkar-{svc}\n"
db_np += "  egress:\n  - {{}}\n"

# Write Edge Policies
for svc in ['frontend', 'api-gateway']:
    path = os.path.join('helm/charts', svc, 'templates', 'networkpolicy.yaml')
    with open(path, 'w') as f:
        f.write(edge_np.format(name=svc))

# Write Internal Backend Policies
for svc in backend_services:
    path = os.path.join('helm/charts', svc, 'templates', 'networkpolicy.yaml')
    with open(path, 'w') as f:
        f.write(internal_np.format(name=svc, api_gateway_name='tripkar-api-gateway'))

# Write DB Policy
db_path = os.path.join('helm/charts', 'mongodb', 'templates', 'networkpolicy.yaml')
with open(db_path, 'w') as f:
    f.write(db_np.format(name='mongodb'))

print("Network Policies generated successfully.")
