#!/usr/bin/env python

import os
import time

from setuptools import setup

r = 1
v = time.strftime("%Y%m%d%H%M")

projectname = "agora"

# os.system("./updateversion.sh") use Makefile!

setup(
  name=projectname,
  version=v,
  url="https://repo.zoidtechnologies.com/%s/" % (projectname),
  author="zoidtechnologies.com",
  author_email="%s@projects.zoidtechnologies.com" % (projectname),
  requires=["ttyio6", "bbsengine6"],
  scripts=["bin/agora"],
  license="GPLv2",
  provides=[projectname],
  packages=["agora"],
  long_description = """agora -- a boutique for bbsengine""",
  include_package_data = True,
)
