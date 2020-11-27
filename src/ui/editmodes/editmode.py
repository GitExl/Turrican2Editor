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

from typing import Dict, Optional, Tuple

import wx

from renderlib.surface import Surface

from turrican2.graphics import Graphics
from turrican2.level import Level
from turrican2.world import World

from ui.camera import Camera


class EditMode:

    def __init__(self, frame):
        self._frame = frame

        self._mouse_position: Tuple[int, int] = (0, 0)
        self._world: Optional[World] = None
        self._level: Optional[Level] = None

    def mouse_left_down(self, event: wx.MouseEvent):
        pass

    def mouse_left_up(self, event: wx.MouseEvent):
        pass

    def mouse_move(self, event: wx.MouseEvent):
        pass

    def paint(self, surface: Surface, camera: Camera, graphics: Graphics):
        pass

    def key_char(self, key_code: int):
        pass

    def level_changed(self):
        pass

    def undo_restore_item(self, item: Dict):
        pass

    def undo_store_item(self) -> Dict:
        pass

    def set_mouse_position(self, position: Tuple[int, int]):
        self._mouse_position = position

    def set_level(self, world: World, level: Level):
        self._world = world
        self._level = level
        self.level_changed()

    @staticmethod
    def get_selection_rectangle(start: Tuple[int, int], end: Tuple[int, int]):
        x1, y1 = start
        x2, y2 = end

        if x2 < x1:
            x1, x2 = x2, x1
        if y2 < y1:
            y1, y2 = y2, y1

        width = x2 - x1 + 1
        height = y2 - y1 + 1

        return x1, y1, width, height
