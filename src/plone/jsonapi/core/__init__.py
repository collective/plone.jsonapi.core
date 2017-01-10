# -*- coding: utf-8 -*-

import logging

import version
from browser import router
from browser import decorators

logger = logging.getLogger("plone.jsonapi.routes")


def initialize(context):
    """ Initializer called when used as a Zope 2 product.
    """
    logger.info("### PLONE.JSONAPI.CORE INITIALIZE ###")

    # Make pyflakes happy
    version
    router
    decorators
