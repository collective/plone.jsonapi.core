# -*- coding: utf-8 -*-
#
# File: interfaces.py

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

from zope import interface


class IPloneJSONAPI(interface.Interface):
    """ API View
    """


class IInfo(interface.Interface):
    """ Info Interface
    """

# vim: set ft=python ts=4 sw=4 expandtab :
