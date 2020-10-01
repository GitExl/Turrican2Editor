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

import wx

from copy import copy

from renderlib.surface import BlendOp

from turrican2.tilemap import Tilemap

from ui.editmodes.editmode import EditMode


class State(object):
    NONE = 0
    SELECT = 1
    DRAW = 2


class SelectType(object):
    NONE = 0
    SELECT = 1
    FILL = 2


COLOR_TILE_SELECTION = 0xFFFFFFFF
COLOR_TILE_FILL = 0xFF00FF00


class EditModeTiles(EditMode):

    def __init__(self, frame):
        EditMode.__init__(self, frame)

        self._state = State.NONE

        self._select_start = None
        self._select_end = None
        self._select_type = SelectType.NONE

        self._selection = None

    def mouse_left_down(self):
        shift = wx.GetKeyState(wx.WXK_SHIFT)
        control = wx.GetKeyState(wx.WXK_CONTROL)

        # Enter tile select state.
        if shift:
            self._state = State.SELECT
            self._select_start = self.get_tile_position()
            self._select_end = self.get_tile_position()
            self._select_type = SelectType.SELECT
            self._frame.set_viewport_cursor(wx.Cursor(wx.CURSOR_CROSS))

        # Enter fill state.
        elif control and self._selection:
            self._state = State.SELECT
            self._select_start = self.get_tile_position()
            self._select_end = self.get_tile_position()
            self._select_type = SelectType.FILL
            self._frame.set_viewport_cursor(wx.Cursor(wx.CURSOR_CROSS))

        # Draw with the current selection.
        else:
            self._state = State.DRAW
            self._frame.undo_add()
            self.place_tile_selection()

    def mouse_left_up(self):
        if self._state == State.SELECT:
            x, y, width, height = self.get_selection_rectangle(self._select_start, self._select_end)
            if width and height:
                if self._select_type == SelectType.SELECT:
                    self._selection = Tilemap.from_tilemap(self._level.tilemap, x, y, x + width, y + height)
                elif self._select_type == SelectType.FILL:
                    self._frame.undo_add()
                    self._level.tilemap.fill_with(self._selection, x, y, x + width, y + height)
                    self._frame.set_level_modified(True)

            self._state = State.NONE
            self._frame.set_viewport_cursor(wx.Cursor(wx.CURSOR_DEFAULT))

        elif self._state == State.DRAW:
            self._state = State.NONE

    def mouse_move(self):
        if self._state == State.DRAW:
            self.place_tile_selection()

        elif self._state == State.SELECT:
            self._select_end = self.get_tile_position()

    def paint(self, surface, camera, graphics):
        shift = wx.GetKeyState(wx.WXK_SHIFT)

        # Draw current tilemap.
        if self._state == State.SELECT:
            x, y, width, height = self.get_selection_rectangle(self._select_start, self._select_end)

            x1 = x * Tilemap.TILE_SIZE
            y1 = y * Tilemap.TILE_SIZE
            x2 = x1 + (width * Tilemap.TILE_SIZE)
            y2 = y1 + (height * Tilemap.TILE_SIZE)

            x1, y1 = camera.world_to_camera(x1, y1)
            x2, y2 = camera.world_to_camera(x2, y2)

            color = 0
            if self._select_type == SelectType.SELECT:
                color = COLOR_TILE_SELECTION
            elif self._select_type == SelectType.FILL:
                color = COLOR_TILE_FILL

            surface.box_fill(x1, y1, x2 - x1, y2 - y1, color, BlendOp.ALPHA50)

        # Draw tile selection.
        elif not shift and self._selection:
            x, y = self.get_tile_selection_position()
            x, y = camera.world_to_camera(x, y)
            self._selection.render_all(surface, self._world.tileset, x, y, False)
            surface.box_fill(x, y, self._selection.width * Tilemap.TILE_SIZE, self._selection.height * Tilemap.TILE_SIZE, 0xFFFFFFFF, BlendOp.ALPHA50)

    def get_tile_selection_position(self):
        if not self._selection:
            return None, None

        x = int(self._mouse_position[0] - ((self._selection.width - 1) * Tilemap.TILE_SIZE) / 2)
        y = int(self._mouse_position[1] - ((self._selection.height - 1) * Tilemap.TILE_SIZE) / 2)

        x = int(x / Tilemap.TILE_SIZE) * Tilemap.TILE_SIZE
        y = int(y / Tilemap.TILE_SIZE) * Tilemap.TILE_SIZE

        return x, y

    def get_tile_position(self):
        x = int(self._mouse_position[0] / Tilemap.TILE_SIZE)
        y = int(self._mouse_position[1] / Tilemap.TILE_SIZE)

        return x, y

    def place_tile_selection(self):
        if not self._selection:
            return

        x, y = self.get_tile_selection_position()
        tile_x = int(x / Tilemap.TILE_SIZE)
        tile_y = int(y / Tilemap.TILE_SIZE)

        self._level.tilemap.put_from(self._selection, tile_x, tile_y)
        self._frame.set_level_modified(True)

    def level_changed(self):
        self._selection = None

    def set_selection(self, selection):
        self._selection = selection
        self._frame.refresh_viewport()

    def undo_restore_item(self, item):
        self._level.tilemap.tiles = item['tiles']
        self._frame.set_level_modified(True)
        self._frame.refresh_viewport()

    def undo_store_item(self):
        return {
            'tiles': copy(self._level.tilemap.tiles)
        }
