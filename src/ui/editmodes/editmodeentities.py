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

from typing import Dict, List, Optional, Tuple

import wx

from copy import deepcopy

from renderlib.surface import BlendOp, Surface

from ui.camera import Camera
from ui.editmodes.editmode import EditMode

from turrican2.graphics import Graphics
from turrican2.level import Entity, EntityTemplate, Level


class State:
    NONE: int = 0
    SELECT: int = 1
    MOVE: int = 2


class EditModeEntities(EditMode):

    COLOR_ENTITY_ORIGIN: int = 0xFFFFFFFF
    COLOR_ENTITY_SELECTION: int = 0xFFFFFFFF

    def __init__(self, frame):
        EditMode.__init__(self, frame)

        self._state: int = State.NONE

        self._select_start: Optional[Tuple[int, int]] = None
        self._select_end: Optional[Tuple[int, int]] = None
        self._selection: List[Entity] = []

        self._template: Optional[EntityTemplate] = None

        self._entity_hover: Optional[Entity] = None

        self._entities_moving: Optional[List[Tuple[Entity, int, int]]] = None
        self._entities_moving_start: Optional[Tuple[int, int]] = None
        self._entity_moved: bool = False

    def key_char(self, key_code: int):
        if key_code == wx.WXK_DELETE:
            self.delete_entities()

    def mouse_left_down(self, event: wx.MouseEvent):
        control = wx.GetKeyState(wx.WXK_CONTROL)

        # Place an entity.
        if control:
            self.place_entity()

        # Move entities.
        elif self._entity_hover:
            if not len(self._selection):
                self._selection = [self._entity_hover]
                self.select_entities()

            elif not self._entity_hover.selected:
                self.deselect_entities()
                self._selection = [self._entity_hover]
                self.select_entities()

            self._state = State.MOVE
            self._entities_moving_start = self.get_entity_position()
            self._entities_moving = self.get_entity_movers()
            self._entity_moved = False

        # Select one or more entities.
        else:
            self._state = State.SELECT
            self._select_start = self.get_entity_position()
            self._select_end = self.get_entity_position()
            self._frame.set_viewport_cursor(wx.Cursor(wx.CURSOR_CROSS))

    def mouse_left_up(self, event: wx.MouseEvent):

        # Entity select state.
        if self._state == State.SELECT:
            self.deselect_entities()
            x, y, width, height = self.get_selection_rectangle(self._select_start, self._select_end)
            self._selection = self._level.get_entities_inside(x, y, x + width, y + height)
            self.select_entities()

            self._state = State.NONE
            self._frame.set_viewport_cursor(wx.Cursor(wx.CURSOR_DEFAULT))
            self._frame.refresh_viewport()

        # Entity move state.
        elif self._state == State.MOVE:
            self._state = State.NONE
            if self._entity_moved:
                self._frame.update_status()

    def mouse_move(self, event: wx.MouseEvent):
        if self._state == State.SELECT:
            self._select_end = self.get_entity_position()

        elif self._state == State.MOVE:
            x1, y1 = self._entities_moving_start
            x2, y2 = self.get_entity_position()
            dx = x2 - x1
            dy = y2 - y1

            if (dx or dy) and not self._entity_moved:
                self._frame.undo_add()
                self._entity_moved = True

            for mover in self._entities_moving:
                new_x = mover[1] + dx
                new_y = mover[2] + dy

                if new_x < 0:
                    new_x = 0
                elif new_x >= self._level.tilemap.width * 4:
                    new_x = self._level.tilemap.width * 4 - 1

                if new_y < 0:
                    new_y = 0
                elif new_y >= self._level.tilemap.height * 4:
                    new_y = self._level.tilemap.height * 4 - 1

                entity = mover[0]
                entity.x = new_x
                entity.y = new_y

            self._frame.set_level_modified(True)

        else:
            x, y = self.get_entity_position()
            self._entity_hover = self._level.get_entity_at(x, y)
            if self._entity_hover:
                self._frame.set_viewport_cursor(wx.Cursor(wx.CURSOR_HAND))
            else:
                self._frame.set_viewport_cursor(wx.Cursor(wx.CURSOR_DEFAULT))

    def paint(self, surface: Surface, camera: Camera, graphics: Graphics):
        control = wx.GetKeyState(wx.WXK_CONTROL)

        # Draw template entity.
        if self._state == State.NONE and self._template and control:
            origin_x, origin_y = self.get_entity_position()

            origin_x *= Level.ORIGIN_SIZE
            origin_y *= Level.ORIGIN_SIZE
            x = origin_x + self._template.offset_x
            y = origin_y + self._template.offset_y

            origin_x, origin_y = camera.world_to_camera(origin_x, origin_y)
            x, y = camera.world_to_camera(x, y)

            surfaces = graphics.get_surfaces(self._template.gfx)
            entity_surface = surfaces[self._template.gfx_index]
            surface.blit_blend(entity_surface, x, y, BlendOp.ALPHA_SIMPLE)

            surface.box_fill(origin_x, origin_y, Level.ORIGIN_SIZE, Level.ORIGIN_SIZE, EditModeEntities.COLOR_ENTITY_ORIGIN, BlendOp.ALPHA50)

        # Draw selection rectangle.
        elif self._state == State.SELECT and self._select_start:
            x1, y1, width, height = self.get_selection_rectangle(self._select_start, self._select_end)
            x1 *= Level.ORIGIN_SIZE
            y1 *= Level.ORIGIN_SIZE
            width *= Level.ORIGIN_SIZE
            height *= Level.ORIGIN_SIZE
            x2, y2 = x1 + width, y1 + height

            x1, y1 = camera.world_to_camera(x1, y1)
            x2, y2 = camera.world_to_camera(x2, y2)

            surface.box_fill(x1, y1, x2 - x1, y2 - y1, EditModeEntities.COLOR_ENTITY_SELECTION, BlendOp.ALPHA50)

    def level_changed(self):
        self._selection = self.get_selected_entities()
        self._template = None

    def place_entity(self):
        if not self._template:
            return

        self._frame.undo_add()

        origin_x, origin_y = self.get_entity_position()
        self._level.add_entity(self._template, origin_x, origin_y)

        self._frame.set_level_modified(True)
        self._frame.update_status()

    def get_entity_position(self) -> Tuple[int, int]:
        x = int(self._mouse_position[0] / Level.ORIGIN_SIZE)
        y = int(self._mouse_position[1] / Level.ORIGIN_SIZE)

        return x, y

    def get_entity_movers(self) -> List[Tuple[Entity, int, int]]:
        entities = []
        for entity in self._selection:
            entities.append((entity, entity.x, entity.y))

        return entities

    def deselect_entities(self):
        for entity in self._selection:
            entity.selected = False

    def select_entities(self):
        for entity in self._selection:
            entity.selected = True

        if len(self._selection) == 1:
            entity = self._selection[0]
            self._frame.Entities.set_selection(entity.type, entity.subtype)

    def delete_entities(self):
        self._frame.undo_add()

        if not len(self._selection) and self._entity_hover:
            self._level.remove_entity(self._entity_hover)
        else:
            for entity in self._selection:
                self._level.remove_entity(entity)
            self._selection = []

        self._frame.refresh_viewport()
        self._frame.update_status()
        self._frame.set_level_modified(True)

    def get_selected_entities(self) -> List[Entity]:
        entities = []
        for entity in self._level.entities:
            if entity.selected:
                entities.append(entity)

        return entities

    def set_template(self, template: EntityTemplate):
        self._template = template
        self._frame.refresh_viewport()

    def get_hover_entity(self) -> Optional[Entity]:
        return self._entity_hover

    def undo_restore_item(self, item: Dict):
        self._level.entities = item['entities']
        self._selection = self.get_selected_entities()

        self._frame.set_level_modified(True)
        self._frame.refresh_viewport()

    def undo_store_item(self) -> Dict:
        return {
            'entities': deepcopy(self._level.entities)
        }
