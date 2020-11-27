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

from renderlib.surface import Surface
from renderlib.dll import dll


__all__ = ['Presenter']


presenterCreate = dll.presenterCreate
presenterCreate.argtypes = [c_uint32, c_uint]
presenterCreate.restype = c_void_p

presenterDestroy = dll.presenterDestroy
presenterDestroy.argtypes = [c_void_p]
presenterDestroy.restype = None

presenterSetScale = dll.presenterSetScale
presenterSetScale.argtypes = [c_void_p, c_uint]
presenterSetScale.restype = None

presenterGetScale = dll.presenterGetScale
presenterGetScale.argtypes = [c_void_p]
presenterGetScale.restype = c_uint

presenterResize = dll.presenterResize
presenterResize.argtypes = [c_void_p]
presenterResize.restype = None

presenterGetSurface = dll.presenterGetSurface
presenterGetSurface.argtypes = [c_void_p]
presenterGetSurface.restype = c_void_p

presenterPresent = dll.presenterPresent
presenterPresent.argtypes = [c_void_p]
presenterPresent.restype = None


class Presenter(object):
    """
    Handles displaying a Surface onto a GDI window.
    """

    def __init__(self, ptr: int):
        self._presenter: int = ptr
        self._scale: int = presenterGetScale(self._presenter)
        self._surface: Surface = Surface(presenterGetSurface(self._presenter), destroy=False)

    def __del__(self):
        presenterDestroy(self._presenter)

    @classmethod
    def from_window(cls, hwnd: int, scale: int):
        """
        Creates a new presenter for a window.
        :param hwnd: the handle of the GDI window to create a presenter for.
        :param scale: the pixel scale of the presenter surface.
        :return: a new Presenter object.
        """
        ptr = presenterCreate(hwnd, scale)
        if not ptr:
            raise Exception('Could not create Presenter object.')

        return cls(ptr)

    def resize(self):
        """
        Resizes this presenter's surface to that of the window it presents to.
        """
        presenterResize(self._presenter)

    def present(self):
        """
        Displays this presenter's surface onto the window.
        """
        presenterPresent(self._presenter)

    @property
    def scale(self) -> int:
        """
        :return: The pixel scale of this presenter.
        """
        return self._scale

    @scale.setter
    def scale(self, scale: int):
        """
        Sets the pixel scale of this presenter.
        :param scale: the new pixel scale.
        """
        presenterSetScale(self._presenter, scale)
        self._scale = scale

    @property
    def surface(self) -> Surface:
        """
        :return: The surface object of this presenter.
        """
        return self._surface
