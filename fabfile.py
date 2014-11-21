#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import urllib2

from fabric.api import (
    env, run, local, put, cd,
    prompt, settings
)
from fabric.contrib.console import confirm
from fabric.contrib.files import exists as remote_exists

import config

env.hosts = config.servers
local_path = config.local_path

if not os.path.exists(local_path):
    os.makedirs(local_path)


def my_ssh_key():
    local("cat ~/.ssh/id_rsa.pub")


def add_key(key):
    run("echo {} >> ~/.ssh/authorized_keys".format(key))


# def download_dirs(func):
#     def _(*args, **kwargs):
#         if not os.path.exists(local_path):
#             os.makedirs(local_path)
#         return func(*args, **kwargs)
#     return _


def ignore_error(func):
    def _(*args, **kwargs):
        with settings(warn_only=True):
            return func(*args, **kwargs)
    return _


def _occur_error(msg):
    sys.stderr.write("\nFatal error: {}\n".format(msg))
    sys.stderr.write("\nAborting.\n")
    sys.exit(1)


def _download_file(url, path):
    _ = urllib2.urlopen(url)
    with open(path, "w") as f:
        print "downloading ..."
        f.write(_.read())
        print "done"


def install_python(remote_path="/opt/resource", install_path="/opt/python"):
    # 0. check if python package exists in local_path
    python_path = os.path.join(local_path, "Python-2.7.8.tgz")

    if not os.path.exists(python_path):
        # 1. download python source code
        _download_file("https://www.python.org/ftp/python/2.7.8/Python-2.7.8.tgz", python_path)

    # 2. put to server
    put(python_path, remote_path)

    # 3. install python
    with cd(remote_path):
        run("tar xvf Python-2.7.8.tgz")
        run("rm Python-2.7.8.tgz")

    with cd(os.path.join(remote_path, "Python-2.7.8")):
        run("./configure --prefix=" + install_path + " && make && make install")


def install_pip(remote_path="/opt/resource", python_path="/opt/python/bin/python2.7"):
    # 1. check python exists in servers
    if not remote_exists(python_path):
        print "Not found python in python_path."
        need_install = confirm("Install python? ", default=False)
        if not need_install:
            _occur_error("Please install python first.")

        python_prefix = prompt("Python install path: ", default="/opt/python")
        install_python(remote_path, python_prefix)
        python_path = os.path.join(python_prefix, "bin", "python2.7")

    # 2. download setuptools
    setuptools_path = os.path.join(local_path, "setuptools-7.0.tar.gz")
    if not os.path.exists(setuptools_path):
        _download_file("https://pypi.python.org/packages/source/s/setuptools/setuptools-7.0.tar.gz#md5=6245d6752e2ef803c365f560f7f2f940", setuptools_path)

    # 3. download pip source code
    pip_path = os.path.join(local_path, "pip-1.5.6.tar.gz")
    if not os.path.exists(pip_path):
        _download_file("https://pypi.python.org/packages/source/p/pip/pip-1.5.6.tar.gz#md5=01026f87978932060cc86c1dc527903e", pip_path)

    # 4. put to server
    put(setuptools_path, remote_path)
    put(pip_path, remote_path)

    # 5. install setuptools
    with cd(remote_path):
        run("tar xvf setuptools-7.0.tar.gz")
        run("rm setuptools-7.0.tar.gz")

    with cd(os.path.join(remote_path, "setuptools-7.0")):
        run(python_path + " setup.py install")

    # 6. install pip
    with cd(remote_path):
        run("tar xvf pip-1.5.6.tar.gz")
        run("rm pip-1.5.6.tar.gz")

    with cd(os.path.join(remote_path, "pip-1.5.6")):
        run(python_path + " setup.py install")


@ignore_error
def download_packages(*args, **kwargs):
    # TODO(crow): make parallel
    args = [i.lower() for i in args]

    src_packages = [i.split('-')[0].lower() for i in os.listdir(local_path)]

    # 1. download all packages
    for i in args:
        if i in src_packages:
            force_choice = confirm("File exists, force download? ", default=False)
            if force_choice:
                # download this package
                local("pip install --download " + local_path + " " + i)
        else:
            local("pip install --download " + local_path + " " + i)


def install_packages(remote_path="/opt/resource", pip_path="/opt/python/bin/pip"):
    # 1. put local_path to servers
    put(local_path, remote_path)

    # 2. get all files in local_path
    _ = run(os.path.join(remote_path, local_path)).split()
    src_list = [i.split('-')[0].lower()
                for i in _
                if i.split('-')[0].lower() != 'python'
                and i.split('-')[0].lower() != 'pip'
                and i.split('-')[0].lower() != 'setuptools']

    # 3. pip install
    [run(pip_path + ' install --no-index -f ' + os.path.join(remote_path, local_path) + ' ' + i)
     for i in src_list]


def install_pys(*args):
    # install_pip
    install_pip()

    # download_packages
    download_packages(*args)

    # install_packages
    install_packages()
