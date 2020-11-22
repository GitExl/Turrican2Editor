# Copyright (c) 2016, Dennis Meuwissen
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from ctypes import *

from renderlib.dll import dll


__all__ = ['Font']


fontGetCharWidth = dll.fontGetCharWidth
fontGetCharWidth.argtypes = [c_void_p]
fontGetCharWidth.restype = c_uint

fontGetCharHeight = dll.fontGetCharHeight
fontGetCharHeight.argtypes = [c_void_p]
fontGetCharHeight.restype = c_uint

fontLoad = dll.fontLoad
fontLoad.argtypes = [c_char_p]
fontLoad.restype = c_void_p

fontDestroy = dll.fontDestroy
fontDestroy.argtypes = [c_void_p]
fontDestroy.restype = None


class Font(object):
    """
    A drawable Font.
    """

    def __init__(self, ptr):
        self._font = ptr

    def __del__(self):
        fontDestroy(self._font)

    @classmethod
    def from_png(cls, filename):
        """
        Creates a new font from a PNG file.
        :param filename: the filename of the PNG file to create the font from.
        :return: a new Font object.
        """
        ptr = fontLoad(filename.encode())
        if not ptr:
            raise Exception('Could not load Font object from PNG file "{}".'.format(filename))

        return cls(ptr)

    @property
    def pointer(self):
        return self._font
