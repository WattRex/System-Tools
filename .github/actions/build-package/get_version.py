
import subprocess
import toml
import re
import sys

if len(sys.argv) != 2:
    print("bash usage: python3 get_version.py <path to toml project file> ")    
    exit(1)
else:
    project_path = sys.argv[1]

vparse = lambda x: tuple(map(int, x.split('.')))
data = toml.load(f'{project_path}/pyproject.toml')

name = data['project']['name']
# checkout_version = data['project']['version']
checkout_version = subprocess.run('pip3 show system-config-tool | grep Version ' +
            '| tr -s \' \' | cut -d\' \' -f2', stdout=subprocess.PIPE, shell=True).stdout

checkout_version = re.findall(r'\d\.\d\.\d', str(checkout_version))[0]
pypi_version = subprocess.run(f'python3 -m pip index versions {name}',
                            shell=True, capture_output=True).stdout
pypi_version = pypi_version.split(b'\n', 1)[0].split(b' ')[1][1:-1].decode('utf-8')
print(pypi_version, checkout_version)
new_local_version = vparse(checkout_version) > vparse(pypi_version)
if new_local_version:
    new_version = checkout_version
else: 
    new_version = pypi_version
    patch = int(new_version[-1]) + 1
    new_version = f'{new_version[:-1]}{patch}'

subprocess.run(f'echo new-version={new_version} >> $GITHUB_OUTPUT', shell=True)
