#!/usr/bin/python3
"""
This script finds out the last version of a package and increase it by one
It also checks if there is any version if not initilize at 0.0.1
"""

import re
import sys
import subprocess
import toml

def merge_version():
    """Compares the version of the project into the local version .
    """
    use_test_pypi = False
    if len(sys.argv) == 2:
        project_path = sys.argv[1]
    elif len(sys.argv) == 3 and sys.argv[2] == 'test':
        print("check version for test pypi")
        use_test_pypi = True
        project_path = sys.argv[1]
    else:
        print("bash usage: python3 get_version.py <path to toml project file> [test]")
        sys.exit(1)

    vparse = lambda x: tuple(map(int, x.split('.'))) # pylint: disable= unnecessary-lambda-assignment
    toml_proj_path = f'{project_path}/pyproject.toml'
    data = toml.load(toml_proj_path)

    name = data['project']['name']
    # checkout_version = data['project']['version']
    # checkout_version = subprocess.run('pip3 show system-config-tool | grep Version ' +
    #             '| tr -s \' \' | cut -d\' \' -f2', stdout=subprocess.PIPE, shell=True).stdout
    checkout_version = subprocess.run('python3 -m setuptools_scm -r ./ ' +
                    f'--config {toml_proj_path}', stdout=subprocess.PIPE,
                    shell=True, check=False).stdout

    print(f"Local version: {checkout_version}")
    checkout_version = re.findall(r'\d\.\d\.\d', str(checkout_version))[0]
    if use_test_pypi:
        cmd = f"python3 -m pip index versions -i https://test.pypi.org/project/ {name}"
    else:
        cmd = f"python3 -m pip index versions {name}"
    pypi_check = subprocess.run(cmd,
                            shell=True, capture_output=True, check= False)
    new_local_version = False
    if pypi_check.returncode > 0:
        new_local_version = True
    else:
        pypi_version = pypi_check.stdout
        print(f"Pypi version: {pypi_version}")
        pypi_version = pypi_version.split(b'\n', 1)[0].split(b' ')[1][1:-1].decode('utf-8')
        new_local_version = vparse(checkout_version) > vparse(pypi_version)

    if new_local_version:
        new_version = checkout_version
    else:
        new_version = pypi_version
        patch = int(new_version[-1]) + 1
        new_version = f'{new_version[:-1]}{patch}'

    print(f"New version package is: {new_version}")
    subprocess.run(f'echo new-version={new_version} >> $GITHUB_OUTPUT', shell=True, check=False)

if __name__ == "__main__":
    merge_version()
