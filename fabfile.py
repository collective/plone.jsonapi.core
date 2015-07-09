# -*- coding: utf-8 -*-

import os
import re
import json
import datetime
import fileinput

# Fabric imports
from fabric.api import env
from fabric.api import lcd
from fabric.api import task
from fabric.api import local
from fabric.colors import yellow
from fabric.colors import green
from fabric.tasks import execute


env.version_file = "src/plone.jsonapi.core/plone/jsonapi/core/version.py"

if not os.path.exists("buildout.cfg"):
    raise RuntimeError("Must be run in the buildout directory")

env.version_file = "src/plone/jsonapi/core/version.py"


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------

@task
def test():
    local("./bin/test -s plone.jsonapi.core")


@task
def make_docs():
    with lcd("docs"):
        local("make html")


@task
def preview_docs():
    with lcd("docs"):
        local("open _build/html/index.html")


@task
def reload():
    execute(bump_version)
    local("wget --delete-after http://admin:admin@localhost:8080/@@reload?action=code")
    print green("RELOADED CODE")


@task
def version():
    print green(json.dumps(get_version()))


@task
def bump_version():
    """Bump up the version number"""
    print yellow("bumping version ...")
    write_version_info()
    print green("adding file '%s' to next commit." % env.version_file)
    local("git add " + env.version_file)
    execute(version)


# -----------------------------------------------------------------------------
# Functional Helpers
# -----------------------------------------------------------------------------

def get_version():
    f = env.version_file
    out = {}
    lines = file(f).readlines()
    for l in lines:
        if "=" in l and l.split("=")[0].strip() in ("__build__", "__date__", "__version__"):
            name, value = l.split("=")
            name = name.strip(" _\n\r")
            value = value.strip(' "\'\n\r')
            out[name] = value
    return out


def write_version_info():
    """ updates the build and date of the version module
    """
    f = env.version_file
    if not os.path.exists(f):
        raise RuntimeError("File '%s' does not exist." % f)

    for line in fileinput.input(f, inplace=1):
        if re.findall("__build__.*=", line):
            build = int(line.split("=")[1])
            line = "__build__ = %d" % (build + 1)
        elif re.findall("__date__.*=", line):
            now = datetime.datetime.now().strftime("%Y-%m-%d")
            line = "__date__ = '%s'" % now
        print line.strip("\n")
