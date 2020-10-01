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
import wx.lib.newevent

from renderlib.presenter import Presenter
from renderlib.surface import BlendOp
from renderlib.utils import swap_rgba

import config


ICON_WIDTH = 32
ICON_HEIGHT = 28
ICON_SPACING = 1


class PickerEntity(object):

    def __init__(self, name, template, surface):
        self.name = name.upper()
        self.template = template
        self.surface = surface


class EntityPicker(wx.Panel):

    PickEvent, EVT_ENTITY_PICK_EVENT = wx.lib.newevent.NewEvent()

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

        self._presenter = Presenter.from_window(self.Viewport.GetHandle(), config.SCALE)

        self._graphics = None
        self._font = None
        self._entities = None

        self._selected_index = -1

        self.Viewport.Bind(wx.EVT_PAINT, self.paint)
        self.Viewport.Bind(wx.EVT_SIZE, self.resize)
        self.Viewport.Bind(wx.EVT_MOUSEWHEEL, self.mouse_wheel)
        self.Viewport.Bind(wx.EVT_LEFT_DOWN, self.mouse_left_down)
        self.Scrollbar.Bind(wx.EVT_SCROLL, self.scroll)

    def set_graphics(self, graphics):
        self._graphics = graphics

    def set_font(self, font):
        self._font = font

    def set_level(self, level):
        self._entities = []

        templates = level.get_entity_templates()
        for keys, template in templates.items():
            src_surface = self._graphics.get_surfaces(template.gfx)[template.gfx_index]

            src_rect = src_surface.get_used_rectangle()
            src_width = src_rect.x2 - src_rect.x1
            src_height = src_rect.y2 - src_rect.y1

            surface = src_surface.empty(ICON_WIDTH, ICON_HEIGHT)
            x = int(ICON_WIDTH / 2 - src_width / 2 - src_rect.x1)
            y = int(ICON_HEIGHT / 2 - src_height / 2 - src_rect.y1)

            surface.blit_blend(src_surface, x, y, BlendOp.ALPHA_SIMPLE)

            self._entities.append(PickerEntity(template.name.upper(), template, surface))

        self._selected_index = -1

        self.set_scrollbar()
        self.Viewport.Refresh(False)

    def paint(self, event):
        if not self._entities:
            return

        surface = self._presenter.surface
        surface.clear()

        color_background = swap_rgba(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DDKSHADOW).GetRGBA())
        color_highlight = swap_rgba(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT).GetRGBA())
        color_text = swap_rgba(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT).GetRGBA())

        y = -self.Scrollbar.GetThumbPosition()

        for index, entity in enumerate(self._entities):
            if index == self._selected_index:
                color = color_highlight
            else:
                color = color_background

            surface.box_fill(0, y, surface.width, ICON_HEIGHT, color, BlendOp.SOLID)
            surface.blit_blend(entity.surface, 0, y, BlendOp.ALPHA_SIMPLE)
            surface.text(self._font, ICON_WIDTH + 6, int(y + ICON_HEIGHT / 2 - 3), entity.name, color_text)

            y += ICON_HEIGHT + ICON_SPACING

        self._presenter.present()

    def resize(self, event):
        self._presenter.resize()
        self.set_scrollbar()

    def mouse_wheel(self, event):
        position = self.Scrollbar.GetThumbPosition()
        position -= int(event.GetWheelRotation() / 20) * ICON_HEIGHT
        self.Scrollbar.SetThumbPosition(position)

        self.Viewport.Refresh(False)

    def mouse_left_down(self, event):
        if not self._entities:
            return

        y = int((event.GetPosition()[1] / config.SCALE) + self.Scrollbar.GetThumbPosition())
        index = int(y / (ICON_HEIGHT + ICON_SPACING))
        self._selected_index = index

        self.Viewport.Refresh(False)
        self.set_template()

    def set_template(self):
        template = self._entities[self._selected_index].template
        event = EntityPicker.PickEvent(template=template)
        wx.PostEvent(self.GetEventHandler(), event)

    def scroll(self, event):
        self.Viewport.Refresh(False)

    def set_selection(self, type, subtype):
        for index, entity in enumerate(self._entities):
            if entity.template.type == type and entity.template.subtype == subtype:
                self._selected_index = index
                self.set_template()

                item_height = ICON_HEIGHT + ICON_SPACING
                y = self._selected_index * item_height + int(item_height / 2) - int(self._presenter.surface.height / 2)
                self.Scrollbar.SetThumbPosition(y)

                break

        self.Viewport.Refresh(False)

    def set_scrollbar(self):
        if not self._entities:
            self.Scrollbar.SetScrollbar(0, 0, 0, 0)
            return

        surface = self._presenter.surface
        position = self.Scrollbar.GetThumbPosition()
        height = len(self._entities) * (ICON_HEIGHT + ICON_SPACING)
        self.Scrollbar.SetScrollbar(position, surface.height, height, ICON_HEIGHT)
