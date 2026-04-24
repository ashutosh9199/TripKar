import os
import glob

files = glob.glob('helm/charts/*/templates/deployment.yaml')
for file in files:
    with open(file, 'r') as f:
        content = f.read()
    
    # Fix the indentation of 'resources:'
    content = content.replace("                    resources:", "          resources:")
    
    with open(file, 'w') as f:
        f.write(content)

print("Indentation fixed.")
