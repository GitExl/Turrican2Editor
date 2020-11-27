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
from renderlib.palette import Palette
from renderlib.stream_read import StreamRead
from renderlib.surface import Surface


__all__ = ['Bitplane', 'MaskMode', 'BitplaneType']


bitplaneCreateFromStream = dll.bitplaneCreateFromStream
bitplaneCreateFromStream.argtypes = [c_void_p, c_uint, c_uint, c_uint, c_uint]
bitplaneCreateFromStream.restype = c_void_p

bitplaneDestroy = dll.bitplaneDestroy
bitplaneDestroy.argtypes = [c_void_p]
bitplaneDestroy.restype = None

bitplaneToSurface = dll.bitplaneToSurface
bitplaneToSurface.argtypes = [c_void_p, c_void_p, c_void_p, c_uint, c_int, c_uint]
bitplaneToSurface.restype = c_void_p


class BitplaneType:
    CHUNKY: int = 0
    PLANAR: int = 1
    AMIGA_SPRITE: int = 2


class MaskMode:
    NONE: int = 0
    INDEX: int = 1
    BITPLANE: int = 2


class Bitplane:
    """
    A bitplane holds a number of 8 bit pixels, without a palette. It can read a bitmap from a series of bitplanes.
    """

    def __init__(self, ptr: int):
        self._bitplane: int = ptr

    def __del__(self):
        bitplaneDestroy(self._bitplane)

    @classmethod
    def from_stream(cls, stream: StreamRead, bitplane_type: BitplaneType, width: int, height: int, planes: int):
        """
        Creates a new bitplane by reading it from a stream.
        :param stream: the stream to read from.
        :param bitplane_type: a BitplaneType value.
        :param width: the width of the bitmap.
        :param height: the height of the bitmap.
        :param planes: the number of bitplanes in the bitmap.
        :return: a new Bitplane object.
        """
        ptr = bitplaneCreateFromStream(stream.pointer, bitplane_type, width, height, planes)
        if not ptr:
            raise Exception('Could not create Bitplane object from stream.')

        return cls(ptr)

    def create_surface(self, mask, palette: Palette, mask_color: int, shift: int, mask_mode: MaskMode):
        """
        Creates a Surface from this Bitplane.
        :param mask: the bitplane to use as the mask.
        :param palette: the palette object to use for color conversion.
        :param mask_color: the color in the mask bitplane that is transparent.
        :param shift: the amount of bits to shift the bitplane's colors with.
        :param mask_mode: the masking mode from MaskMode.
        :return:
        """
        if mask is None:
            mask_pointer = 0
        else:
            mask_pointer = mask.pointer

        ptr = bitplaneToSurface(self._bitplane, mask_pointer, palette.pointer, mask_color, shift, mask_mode)
        if not ptr:
            raise Exception('Could not create Surface from Bitplane object.')

        return Surface(ptr)

    @property
    def pointer(self) -> int:
        return self._bitplane
