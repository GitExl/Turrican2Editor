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


__all__ = ['create_bgra', 'create_rgba', 'swap_rgba', 'Rectangle', 'Endianness']


createBGRA = dll.createBGRA
createBGRA.argtypes = [c_ubyte, c_ubyte, c_ubyte, c_ubyte]
createBGRA.restype = c_uint32

createRGBA = dll.createRGBA
createRGBA.argtypes = [c_ubyte, c_ubyte, c_ubyte, c_ubyte]
createRGBA.restype = c_uint32

swapRGBA = dll.swapRGBA
swapRGBA.argtypes = [c_uint32]
swapRGBA.restype = c_uint32


class Endianness:
    LITTLE: int = 0
    BIG: int = 1


class Rectangle(Structure):
    _fields_ = [
        ('x1', c_int),
        ('y1', c_int),
        ('x2', c_int),
        ('y2', c_int)
    ]


def create_bgra(r: int, g: int, b: int, a: int) -> int:
    return createBGRA(r, g, b, a)


def create_rgba(r: int, g: int, b: int, a: int) -> int:
    return createRGBA(r, g, b, a)


def swap_rgba(color: int) -> int:
    return swapRGBA(color)
