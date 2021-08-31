Create database users
=============

Be very careful with this script, it will add users and grant access to the DBs as configured

This script creates users and grants them privileges en several databases based on predefined business roles.
 

### How to run it
To run it locally you will need Python3 
You need to setup users and servers in the config.yaml

In main function you can change the code to run a connection test

```shell
~# python3 -m venv env && source env/bin/activate

~# pip install -r requirements.txt

~# python manager.py run-mode
```