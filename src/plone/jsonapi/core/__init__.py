# -*- coding: utf-8 -*-

# Imported for their import-time side effects: `version` registers the
# /version route, and router/decorators set up the framework.
from . import version  # noqa: F401
from .browser import decorators  # noqa: F401
from .browser import router  # noqa: F401

import logging


logger = logging.getLogger("plone.jsonapi.core")


def initialize(context):
    """ Initializer called when used as a Zope 2 product.
    """
    logger.info("### PLONE.JSONAPI.CORE INITIALIZE ###")
