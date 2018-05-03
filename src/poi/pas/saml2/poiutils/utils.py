# -*- coding: utf-8 -*-

from sys import platform
import os


def xmlsec_path():
    if platform == "win32":
        import poi.pas.saml2
        ProgDirectory = os.path.abspath(poi.pas.saml2.__file__)
        sx = ProgDirectory.find('src')
        return ProgDirectory[0:sx]+'winlibs\\xmlsec1\\bin\\xmlsec1.exe'
    else:
        return '/usr/bin/xmlsec1'
