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

from renderlib.surface import BlendOp, Surface

from turrican2.graphics import Graphics
from turrican2.tilemap import Tilemap

from ui.camera import Camera
from ui.editmodes.editmode import EditMode


class State:
    NONE: int = 0
    MOVE_CAMERA: int = 1
    MOVE_PLAYER: int = 2


class EditModeStart(EditMode):

    COLOR_CAMERA: int = 0xFFFFFF00
    COLOR_PLAYER: int = 0xFFFF0000
    COLOR_HIGHLIGHT: int = 0xFFFFFFFF

    CAMERA_WIDTH: int = 304
    CAMERA_HEIGHT: int = 192

    PLAYER_WIDTH: int = 32
    PLAYER_HEIGHT: int = 36

    def __init__(self, frame):
        EditMode.__init__(self, frame)

        self._state: int = State.NONE

        self._highlight_camera: bool = False
        self._highlight_player: bool = False

        self._move_offset: Optional[Tuple[int, int]] = None

    def mouse_left_down(self, event: wx.MouseEvent):
        if self._state != State.NONE:
            return

        if self._highlight_player:
            self._state = State.MOVE_PLAYER
            self._frame.undo_add()

            x, y = self.get_player_position()
            ox = x - self._level.player_x
            oy = y - self._level.player_y
            self._move_offset = (ox, oy)

        elif self._highlight_camera:
            self._state = State.MOVE_CAMERA
            self._frame.undo_add()

            x, y = self.get_camera_position()
            ox = x - self._level.camera_tile_x
            oy = y - self._level.camera_tile_y
            self._move_offset = (ox, oy)

    def mouse_left_up(self, event: wx.MouseEvent):
        self._state = State.NONE

    def mouse_move(self, event: wx.MouseEvent):
        mouse = self._mouse_position

        if self._state == State.MOVE_PLAYER:
            player_x, player_y = self.get_player_position()
            x = player_x - self._move_offset[0]
            y = player_y - self._move_offset[1]

            if x < 0:
                x = 0
            if y < 0:
                y = 0
            if x + EditModeStart.PLAYER_WIDTH > EditModeStart.CAMERA_WIDTH:
                x = EditModeStart.CAMERA_WIDTH - EditModeStart.PLAYER_WIDTH
            if y + EditModeStart.PLAYER_HEIGHT > EditModeStart.CAMERA_HEIGHT:
                y = EditModeStart.CAMERA_HEIGHT - EditModeStart.PLAYER_HEIGHT

            self._level.player_x = x
            self._level.player_y = y

            self._frame.set_level_modified(True)

        elif self._state == State.MOVE_CAMERA:
            camera_x, camera_y = self.get_camera_position()
            self._level.camera_tile_x = camera_x - self._move_offset[0]
            self._level.camera_tile_y = camera_y - self._move_offset[1]

            x_max = self._level.tilemap.width * Tilemap.TILE_SIZE - 16
            if self._level.camera_tile_x < 1:
                self._level.camera_tile_x = 1
            elif self._level.camera_tile_x * Tilemap.TILE_SIZE + EditModeStart.CAMERA_WIDTH >= x_max:
                self._level.camera_tile_x = int(self._level.tilemap.width - EditModeStart.CAMERA_WIDTH / Tilemap.TILE_SIZE - 1)

            y_max = self._level.tilemap.height * Tilemap.TILE_SIZE - 32
            if self._level.camera_tile_y < 1:
                self._level.camera_tile_y = 1
            elif self._level.camera_tile_y * Tilemap.TILE_SIZE + EditModeStart.CAMERA_HEIGHT >= y_max:
                self._level.camera_tile_y = int(self._level.tilemap.height - EditModeStart.CAMERA_HEIGHT / Tilemap.TILE_SIZE - 1)

            self._frame.set_level_modified(True)

        else:

            x1 = self._level.camera_tile_x * Tilemap.TILE_SIZE
            y1 = self._level.camera_tile_y * Tilemap.TILE_SIZE
            x2 = x1 + EditModeStart.CAMERA_WIDTH
            y2 = y1 + EditModeStart.CAMERA_HEIGHT
            self._highlight_camera = not (mouse[0] < x1 or mouse[0] >= x2 or mouse[1] < y1 or mouse[1] >= y2)

            x1 += self._level.player_x
            y1 += self._level.player_y
            x2 = x1 + EditModeStart.PLAYER_WIDTH
            y2 = y1 + EditModeStart.PLAYER_HEIGHT
            self._highlight_player = not (mouse[0] < x1 or mouse[0] >= x2 or mouse[1] < y1 or mouse[1] >= y2)

            if self._highlight_camera or self._highlight_player:
                self._frame.set_viewport_cursor(wx.Cursor(wx.CURSOR_SIZING))
            else:
                self._frame.set_viewport_cursor(wx.Cursor(wx.CURSOR_DEFAULT))

    def paint(self, surface: Surface, camera: Camera, graphics: Graphics):
        x = self._level.camera_tile_x * Tilemap.TILE_SIZE
        y = self._level.camera_tile_y * Tilemap.TILE_SIZE
        x, y = camera.world_to_camera(x, y)
        if self._highlight_camera:
            color = EditModeStart.COLOR_HIGHLIGHT
        else:
            color = EditModeStart.COLOR_CAMERA
        surface.box(x, y, EditModeStart.CAMERA_WIDTH - 1, EditModeStart.CAMERA_HEIGHT - 1, color)

        x = int(x + self._level.player_x)
        y = int(y + self._level.player_y)
        if self._highlight_player:
            color = EditModeStart.COLOR_HIGHLIGHT
        else:
            color = EditModeStart.COLOR_PLAYER

        player = graphics.get_surfaces('player')[1]
        surface.blit_blend(player, x, y - 2, BlendOp.ALPHA_SIMPLE)
        surface.box(x, y, EditModeStart.PLAYER_WIDTH - 1, EditModeStart.PLAYER_HEIGHT - 1, color)

    def get_camera_position(self) -> Tuple[int, int]:
        x = self._mouse_position[0] / Tilemap.TILE_SIZE
        y = self._mouse_position[1] / Tilemap.TILE_SIZE

        return x, y

    def get_player_position(self) -> Tuple[int, int]:
        x = self._mouse_position[0] - self._level.camera_tile_x * Tilemap.TILE_SIZE
        y = self._mouse_position[1] - self._level.camera_tile_y * Tilemap.TILE_SIZE

        return x, y

    def undo_restore_item(self, item: Dict):
        self._level.camera_tile_x = item['camera_tile_x']
        self._level.camera_tile_y = item['camera_tile_y']
        self._level.player_x = item['player_x']
        self._level.player_y = item['player_y']

        self._frame.set_level_modified(True)
        self._frame.refresh_viewport()

    def undo_store_item(self) -> Dict:
        return {
            'camera_tile_x': self._level.camera_tile_x,
            'camera_tile_y': self._level.camera_tile_y,
            'player_x': self._level.player_x,
            'player_y': self._level.player_y
        }
