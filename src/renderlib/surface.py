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
from renderlib.utils import Rectangle


__all__ = ['Surface']


# Surface functions.
surfaceFlipY = dll.surfaceFlipY
surfaceFlipY.argtypes = [c_void_p]
surfaceFlipY.restype = c_void_p

surfaceGetWidth = dll.surfaceGetWidth
surfaceGetWidth.argtypes = [c_void_p]
surfaceGetWidth.restype = c_uint

surfaceGetHeight = dll.surfaceGetHeight
surfaceGetHeight.argtypes = [c_void_p]
surfaceGetHeight.restype = c_uint

surfaceWriteToPNG = dll.surfaceWriteToPNG
surfaceWriteToPNG.argtypes = [c_void_p, c_char_p, c_uint]
surfaceWriteToPNG.restype = c_bool

surfaceReadFromPNG = dll.surfaceReadFromPNG
surfaceReadFromPNG.argtypes = [c_char_p]
surfaceReadFromPNG.restype = c_void_p

surfaceCreate = dll.surfaceCreate
surfaceCreate.argtypes = [c_uint, c_uint]
surfaceCreate.restype = c_void_p

surfaceDestroy = dll.surfaceDestroy
surfaceDestroy.argtypes = [c_void_p]
surfaceDestroy.restype = None

surfaceExtract = dll.surfaceExtract
surfaceExtract.argtypes = [c_void_p, c_void_p, c_int, c_int]
surfaceExtract.restype = None

surfaceFill = dll.surfaceFill
surfaceFill.argtypes = [c_void_p, c_uint]
surfaceFill.restype = None

surfaceClear = dll.surfaceClear
surfaceClear.argtypes = [c_void_p]
surfaceClear.restype = None

surfaceClone = dll.surfaceClone
surfaceClone.argtypes = [c_void_p]
surfaceClone.restype = c_void_p

surfaceUsedRect = dll.surfaceUsedRect
surfaceUsedRect.argtypes = [c_void_p]
surfaceUsedRect.restype = Rectangle

# Render functions.
renderOutline = dll.renderOutline
renderOutline.argtypes = [c_void_p, c_void_p, c_int, c_int, c_uint]
renderOutline.restype = None

renderLine = dll.renderLine
renderLine.argtypes = [c_void_p, c_int, c_int, c_int, c_int, c_uint]
renderLine.restype = None

renderText = dll.renderText
renderText.argtypes = [c_void_p, c_void_p, c_int, c_int, c_char_p, c_uint]
renderText.restype = None

renderBox = dll.renderBox
renderBox.argtypes = [c_void_p, c_int, c_int, c_int, c_int, c_uint]
renderBox.restype = None

renderBlit = dll.renderBlit
renderBlit.argtypes = [c_void_p, c_void_p, c_int, c_int]
renderBlit.restype = None

renderBoxFill = dll.renderBoxFill
renderBoxFill.argtypes = [c_void_p, c_int, c_int, c_int, c_int, c_uint, c_uint8]
renderBoxFill.restype = None

renderBlitBlend = dll.renderBlitBlend
renderBlitBlend.argtypes = [c_void_p, c_void_p, c_int, c_int, c_uint8]
renderBlitBlend.restype = None

renderBlitBlendScale = dll.renderBlitBlendScale
renderBlitBlendScale.argtypes = [c_void_p, c_void_p, c_int, c_int, c_int, c_int, c_uint8]
renderBlitBlendScale.restype = None


class BlendOp(object):
    SOLID = 0
    ALPHA50 = 1
    ALPHA = 2
    ALPHA_SIMPLE = 3


class Surface(object):

    def __init__(self, ptr, destroy=True):
        self._surface = ptr
        self._destroy = destroy

    def __del__(self):
        if self._destroy:
            surfaceDestroy(self._surface)

    @classmethod
    def empty(cls, width, height):
        ptr = surfaceCreate(width, height)
        if not ptr:
            raise Exception('Could not create Surface object with size {}x{}.'.format(width, height))

        return cls(ptr)

    @classmethod
    def from_png(cls, filename):
        ptr = surfaceReadFromPNG(filename.encode())
        if not ptr:
            raise Exception('Could not read Surface object from PNG "{}".'.format(filename))

        return cls(ptr)

    def clone(self):
        surface_ptr = surfaceClone(self._surface)
        return Surface(surface_ptr)

    def flipped_y(self):
        surface_ptr = surfaceFlipY(self._surface)
        return Surface(surface_ptr)

    def write_to_png(self, filename):
        return surfaceWriteToPNG(filename.encode())

    def extract(self, surface_dest, x, y):
        surfaceExtract(self._surface, surface_dest.pointer, x, y)

    def fill(self, color):
        surfaceFill(self._surface, color)

    def clear(self):
        surfaceClear(self._surface)

    def outline(self, surface_source, x, y, color):
        renderOutline(self._surface, surface_source.pointer, x, y, color)

    def line(self, x1, y1, x2, y2, color):
        renderLine(self._surface, x1, y1, x2, y2, color)

    def text(self, font, x, y, text, color):
        renderText(self._surface, font.pointer, x, y, text.encode(), color)

    def box(self, x, y, width, height, color):
        renderBox(self._surface, x, y, width, height, color)

    def blit(self, surface_source, x, y):
        renderBlit(self._surface, surface_source.pointer, x, y)

    def box_fill(self, x, y, width, height, color, blend_op):
        renderBoxFill(self._surface, x, y, width, height, color, blend_op)

    def blit_blend(self, surface_source, x, y, blend_op):
        renderBlitBlend(self._surface, surface_source.pointer, x, y, blend_op)

    def blit_blend_scale(self, surface_source, x, y, width, height, blend_op):
        renderBlitBlendScale(self._surface, surface_source.pointer, x, y, width, height, blend_op)

    def get_used_rectangle(self):
        return surfaceUsedRect(self._surface)

    @property
    def pointer(self):
        return self._surface

    @property
    def width(self):
        return surfaceGetWidth(self._surface)

    @property
    def height(self):
        return surfaceGetHeight(self._surface)
