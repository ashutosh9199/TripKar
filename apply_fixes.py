import os
import glob

# Fix Frontend URLs
frontend_files = glob.glob('src/appwrite/*.js')
for fpath in frontend_files:
    with open(fpath, 'r') as f:
        content = f.read()
    content = content.replace('http://localhost:5000', '')
    with open(fpath, 'w') as f:
        f.write(content)

print("Fixed frontend URLs.")

# Fix Backend Database Passwords
backend_configmaps = glob.glob('helm/charts/*/templates/configmap.yaml')
for fpath in backend_configmaps:
    with open(fpath, 'r') as f:
        content = f.read()
    content = content.replace('admin:secret@mongodb', 'admin:secretpassword123@mongodb')
    with open(fpath, 'w') as f:
        f.write(content)

print("Fixed backend database passwords.")
