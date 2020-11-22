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


__all__ = ['Palette']


paletteReadFromStream = dll.paletteReadFromStream
paletteReadFromStream.argtypes = [c_void_p, c_uint, c_uint, c_bool]
paletteReadFromStream.restype = c_void_p

paletteDestroy = dll.paletteDestroy
paletteDestroy.argtypes = [c_void_p]
paletteDestroy.restype = None


class Palette(object):
    """
    Contains an arbitrary number of color values. Normally used with a Bitplane to create a Surface.
    """

    def __init__(self, ptr):
        self._palette = ptr

    def __del__(self):
        paletteDestroy(self._palette)

    @classmethod
    def from_stream(cls, stream, length, bits_per_channel, read_alpha=False):
        """
        Creates a new palette by reading it from a stream.
        :param stream: the stream to read from.
        :param length: the number of colors to read.
        :param bits_per_channel: the number of bits per channel of each color.
        :param read_alpha: True if an alpha component should be read alongside the RGB components.
        :return: a new Palette object.
        """
        ptr = paletteReadFromStream(stream.pointer, length, bits_per_channel, read_alpha)
        if not ptr:
            raise Exception('Could not create Palette object from stream.')

        return cls(ptr)

    @property
    def pointer(self):
        return self._palette
