#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import urllib2

from fabric.api import (
    env, run, local, put, cd,
    prompt
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

    with cd(os.path.join(remote_path, "setuptools-7.0")):
        run(python_path + " setup.py install")

    # 6. install pip
    with cd(remote_path):
        run("tar xvf pip-1.5.6.tar.gz")

    with cd(os.path.join(remote_path, "pip-1.5.6")):
        run(python_path + " setup.py install")


def download_packages(*args):
    # TODO(crow): 考虑同时输入多个库的情况

    # pip install --download /path/to/download sentry 就会把所有 sentry 有关的包全下下来

    src_packages = [i.split('-')[0].lower() for i in os.listdir('src')]

    # 1. download all packages
    for i in args:
        if i in src_packages:
            force_choice = confirm("File exists, force download? ", default=False)


def install_package(remote_path="/opt/resource"):
    # pip install --no-index -f /path/to/packages sentry
    # 有个办法是用 pip --download 下载所有的包，上传上去，然后 pip install --no-index --find-links <local path> sentry，从本地放这些包的路径

    # 如果没有path则mkdir -p
    # 判断有没有python和pip
    # 如果没有则调用install_python和install_pip安装python和pip
    pass