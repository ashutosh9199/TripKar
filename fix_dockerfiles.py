import glob

dockerfiles = glob.glob('**/Dockerfile', recursive=True)
for df in dockerfiles:
    with open(df, 'r') as f:
        content = f.read()
    
    # Replace npm ci with npm install
    content = content.replace("RUN npm ci", "RUN npm install")
    
    with open(df, 'w') as f:
        f.write(content)

print("Fixed Dockerfiles.")
