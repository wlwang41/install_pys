# Install_pys

[![The MIT License](http://img.shields.io/badge/license-MIT-red.svg?style=flat)](https://github.com/wlwang41/install_pys/blob/master/LICENSE)

Install_pys is a fabric script that can easily install third python packages for the internal servers.

-----

## How to use

### First step

Change the `config.py` for your own situation.
you **should** specify the servers here, and the local path.

* `servers`: the remote servers
* `local_path`: the relative path that saves the python packages in your local machine


### Second step

Install the requirements.

    pip install -r requirements.txt


### Third step

You can just run one command to install.

    fab install_pys:<YOUR_PYTHON_PACKAGES1>,<YOUR_PYTHON_PACKAGES2>

* All packages will upload to `/opt/resource` in servers
* Python will be installed in `/opt/python`

Or you can run the other functions in `fabfile.py`.
In this way, you can specify the remote path.
