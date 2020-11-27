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

import math
from typing import Tuple


class Camera:

    def __init__(self, width: int, height: int, max_x: int, max_y: int):
        self._width: int = width
        self._height: int = height

        self._x: int = 0
        self._y: int = 0

        self._max_x: int = max_x
        self._max_y: int = max_y

    def move_relative(self, x: int, y: int):
        self._x += x
        self._y += y

        self.clamp()

    def move_absolute(self, x: int, y: int):
        self._x = x
        self._y = y

        self.clamp()

    def clamp(self):
        if self._x + self._width >= self._max_x:
            self._x = self._max_x - self._width
        if self._y + self._height >= self._max_y:
            self._y = self._max_y - self._height

        if self._x < 0:
            self._x = 0
        if self._y < 0:
            self._y = 0

    def camera_to_world(self, x: int, y: int) -> Tuple[int, int]:
        return int(math.floor(x + self._x)), int(math.floor(y + self._y))

    def world_to_camera(self, x, y) -> Tuple[int, int]:
        return int(math.floor(x - self._x)), int(math.floor(y - self._y))

    def set_max(self, max_x: int, max_y: int):
        self._max_x = max_x
        self._max_y = max_y

        self.clamp()

    def set_size(self, width: int, height: int):
        self._width = width
        self._height = height

        self.clamp()

    def world_contains(self, x1: int, y1: int, x2: int, y2: int):
        return not (x2 < self._x or y2 < self._y or x1 >= self._x + self._width or y1 >= self._y + self.height)

    def screen_contains(self, x1: int, y1: int, x2: int, y2: int):
        return not (x2 < 0 or y2 < 0 or x1 >= self._width or y1 >= self.height)

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height
