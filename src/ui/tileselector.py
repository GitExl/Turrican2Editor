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

import wx
import wx.lib.newevent

from renderlib.presenter import Presenter
from renderlib.surface import BlendOp

from turrican2.tilemap import Tilemap

from ui.camera import Camera

import config


class TileSelector(wx.Panel):

    SelectEvent, EVT_SELECT_EVENT = wx.lib.newevent.NewEvent()

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.NO_BORDER):
        wx.Panel.__init__(self, parent, id=id, pos=pos, size=size, style=style)

        self.Viewport = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER)
        self.Scrollbar = wx.ScrollBar(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SB_VERTICAL)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.Viewport, 1, wx.EXPAND, 0)
        sizer.Add(self.Scrollbar, 0, wx.EXPAND, 0)

        self.SetSizer(sizer)
        self.Layout()
        sizer.Fit(self)

        self.Scrollbar.SetScrollbar(0, 0, 0, 0)

        self._presenter = Presenter.from_window(self.Viewport.GetHandle(), config.SCALE)
        self._camera = Camera(0, 0, 0, 0)

        self._tilemap = None
        self._tileset = None
        self._select_start = None
        self._select_end = None

        self._show_collision = False

        self.Viewport.Bind(wx.EVT_PAINT, self.paint)
        self.Viewport.Bind(wx.EVT_SIZE, self.resize)
        self.Viewport.Bind(wx.EVT_MOUSEWHEEL, self.mouse_wheel)
        self.Viewport.Bind(wx.EVT_LEFT_DOWN, self.mouse_left_down)
        self.Viewport.Bind(wx.EVT_LEFT_UP, self.mouse_left_up)
        self.Viewport.Bind(wx.EVT_MOTION, self.mouse_move)
        self.Scrollbar.Bind(wx.EVT_SCROLL, self.scroll)

    def set_tileset(self, tileset):
        self._tileset = tileset
        self.populate_tiles()

        self.Viewport.Refresh(False)

    def populate_tiles(self):
        if not self._tileset:
            self._tilemap.clear()

        surface = self._presenter.surface

        tiles_width = int(math.floor(surface.width / float(Tilemap.TILE_SIZE)))
        tiles_height = int(math.ceil(len(self._tileset.tiles) / float(tiles_width)))

        tiles = range(0, len(self._tileset.tiles))
        self._tilemap = Tilemap(tiles, tiles_width, tiles_height)

        self._camera.set_max(tiles_width * Tilemap.TILE_SIZE, tiles_height * Tilemap.TILE_SIZE)
        self.Scrollbar.SetScrollbar(wx.VERTICAL, 0, surface.height, tiles_height, True)

        self.Scrollbar.SetThumbPosition(0)

    def resize(self, event):
        self._presenter.resize()
        surface = self._presenter.surface

        self._camera.set_size(surface.width, surface.height)

        if self._tileset:
            tiles_width = int(math.floor(surface.width / float(Tilemap.TILE_SIZE)))
            tiles_height = int(math.ceil((len(self._tileset.tiles) / tiles_width) * Tilemap.TILE_SIZE))

            diff = int(tiles_height - surface.height)
            if diff:
                position = self.Scrollbar.GetThumbPosition()
                self.Scrollbar.SetScrollbar(position, surface.height, tiles_height, Tilemap.TILE_SIZE)
            else:
                self.Scrollbar.SetScrollbar(0, 0, 0, 0)

    def paint(self, event):
        if not self._tileset:
            return

        surface = self._presenter.surface
        surface.clear()

        self._camera.move_absolute(0, self.Scrollbar.GetThumbPosition())
        self._tilemap.render(surface, self._camera, self._tileset, self._show_collision)

        if self._select_start:
            x1 = self._select_start[0] * Tilemap.TILE_SIZE
            y1 = self._select_start[1] * Tilemap.TILE_SIZE

            x2 = self._select_end[0] * Tilemap.TILE_SIZE
            y2 = self._select_end[1] * Tilemap.TILE_SIZE

            x1, y1 = self._camera.world_to_camera(x1, y1)
            x2, y2 = self._camera.world_to_camera(x2, y2)

            if x2 < x1:
                x2, x1 = x1, x2
            if y2 < y1:
                y2, y1 = y1, y2

            width = x2 - x1 + Tilemap.TILE_SIZE
            height = y2 - y1 + Tilemap.TILE_SIZE

            surface.box_fill(x1, y1, width, height, 0xFFFFFFFF, BlendOp.ALPHA50)

        self._presenter.present()

    def mouse_wheel(self, event):
        if not self._tileset:
            return

        position = self.Scrollbar.GetThumbPosition()
        position -= int(event.GetWheelRotation() / 20) * Tilemap.TILE_SIZE
        self.Scrollbar.SetThumbPosition(position)

        self.Viewport.Refresh(False)

    def mouse_left_down(self, event):
        if not self._tileset:
            return

        if self._select_start:
            return

        pos = event.GetPosition()
        x, y = self.get_tile_position(pos)

        self._select_start = (x, y)
        self._select_end = self._select_start

        self.Viewport.Refresh(False)

    def mouse_left_up(self, event):
        if not self._tilemap:
            return

        if not self._select_end:
            return

        x1, y1 = self._select_start
        x2, y2 = self._select_end

        if x2 < x1:
            x2, x1 = x1, x2
        if y2 < y1:
            y2, y1 = y1, y2

        width = x2 - x1 + 1
        height = y2 - y1 + 1

        self._select_start = None
        self._select_end = None

        self.Viewport.Refresh(False)

        if width and height:
            selection = Tilemap.from_tilemap(self._tilemap, x1, y1, x2 + 1, y2 + 1)
        else:
            selection = None

        event = TileSelector.SelectEvent(selection=selection)
        wx.PostEvent(self.GetEventHandler(), event)

    def mouse_move(self, event):
        if not self._select_start:
            return

        pos = event.GetPosition()
        x, y = self.get_tile_position(pos)

        self._select_end = (x, y)
        self.Viewport.Refresh(False)

    def scroll(self, event):
        self.Viewport.Refresh(False)

    def get_tile_position(self, pos):
        x = int(pos[0] / self._presenter.scale)
        y = int(pos[1] / self._presenter.scale)
        x, y = self._camera.camera_to_world(x, y)
        x = int(x / Tilemap.TILE_SIZE)
        y = int(y / Tilemap.TILE_SIZE)

        return x, y

    def show_collision(self, show):
        self._show_collision = show
        self.Viewport.Refresh(False)
