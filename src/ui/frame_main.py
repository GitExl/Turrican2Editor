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

import os.path
import json

import wx

import ui.dialogs
import ui.tileselector
import ui.entitypicker

from ui.dialogs import FrameMainBase
from ui.dialog_about import DialogAbout

from ui.editmodes.editmodetiles import EditModeTiles
from ui.editmodes.editmodeentities import EditModeEntities
from ui.editmodes.editmodestart import EditModeStart

from renderlib.presenter import Presenter
from renderlib.surface import BlendOp
from renderlib.font import Font

from turrican2.world import World
from turrican2.tilemap import Tilemap
from turrican2.graphics import Graphics
from turrican2.level import Level

from camera import Camera

import config


class MouseState(object):
    NONE = 0
    MOVE = 1


class EditMode(object):
    TILES = 0
    ENTITIES = 1
    START = 2


COLOR_ORIGIN = 0xFFFFFFFF

COLOR_ENTITY_HOVER = 0xFFFFFFFF
COLOR_ENTITY_SELECTED = 0xFFFF0000


class FrameMain(FrameMainBase):

    def __init__(self):
        FrameMainBase.__init__(self, None)

        self.SetIcon(wx.Icon(u'res/icon-diamond.ico'))

        self.Enable(False)
        self.Status.SetFieldsCount(1)

        self._edit_mode_dialogs = {
            ui.dialogs.EDIT_TILES: EditMode.TILES,
            ui.dialogs.EDIT_ENTITIES: EditMode.ENTITIES,
            ui.dialogs.EDIT_START: EditMode.START
        }

        self._edit_mode_panels = {
            EditMode.TILES: self.PanelModeTiles,
            EditMode.ENTITIES: self.PanelModeEntities,
            EditMode.START: self.PanelModeStart
        }

        self._edit_modes = {
            EditMode.TILES: EditModeTiles(self),
            EditMode.ENTITIES: EditModeEntities(self),
            EditMode.START: EditModeStart(self),
        }
        self._edit_mode = None

        self._game_dir = None

        self._mouse_state = MouseState.NONE
        self._move_last_pos = 0

        self._graphics = None
        self._worlds = None
        self._world = None
        self._level = None

        self._presenter = None
        self._camera = None

        self._draw_tile_collision = False
        self._always_draw_entities = True
        self._draw_blockmap = False

        self._font = Font.from_png('fonts/zepto.png')

        self.set_mode(EditMode.TILES)
        self.update_menu_state()

        self.Tiles.Bind(ui.tileselector.TileSelector.EVT_SELECT_EVENT, self.selection_tile)
        self.Entities.Bind(ui.entitypicker.EntityPicker.EVT_ENTITY_PICK_EVENT, self.selection_entity)
        self.Bind(wx.EVT_CHAR_HOOK, self.char_hook)

        self.Maximize()
        self.Show()

        self.Enable(True)

    def open(self, event):
        dialog = wx.DirDialog(self, 'Select a Turrican II CDTV directory', '', wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dialog.ShowModal() != wx.ID_OK:
            return

        directory = dialog.GetPath()
        test_files = ['L1-1', 'L2-1', 'L3-1', 'L4-1', 'L5-1', 'LOADER', 'MAIN']
        for filename in test_files:
            if not os.path.exists(os.path.join(directory, filename)):
                wx.MessageBox('Not a valid Turrican II CDTV directory.', 'Invalid directory', wx.OK | wx.ICON_EXCLAMATION)
                return

        self._game_dir = directory
        self._graphics = Graphics(self._game_dir)
        self.load_worlds()

        self.Entities.set_graphics(self._graphics)
        self.Entities.set_font(self._font)

        self.LevelSelect.SetSelection(0)
        self.select_level(0, 0)
        self.update_menu_state()
        self.update_title()

    def char_hook(self, event):
        key_code = event.GetKeyCode()
        self._edit_mode.key_char(key_code)
        event.Skip()

    def load_worlds(self):
        with open('level-data.json', 'r') as fp:
            level_data = json.load(fp)

        self._worlds = []
        for data in level_data:
            world = World()
            world.load(os.path.join(self._game_dir, data['world_file']), data['levels'])
            self._worlds.append(world)

        for world_index, world in enumerate(self._worlds):
            for level_index, level in enumerate(world.levels):
                data = (world_index, level_index)
                self.LevelSelect.Append(level.name, data)

    def set_mode(self, new_mode):
        self._edit_mode = self._edit_modes[new_mode]

        # Show only the active mode panel.
        for panel in self._edit_mode_panels.values():
            panel.Hide()
        self._edit_mode_panels[new_mode].Show()

        self.Layout()
        self.Viewport.Refresh(False)

    def set_mode_from_menu(self, event):
        id = event.GetId()
        self.set_mode(self._edit_mode_dialogs[id])

    def viewport_resize(self, event):
        if not self._camera:
            return

        viewport_size = self.Viewport.GetSize()
        self._camera.set_size(viewport_size[0] / self._presenter.scale, viewport_size[1] / self._presenter.scale)

        self._presenter.resize()

    def viewport_paint(self, event):
        if not self._presenter:
            return

        surface = self._presenter.surface
        surface.clear()

        self._level.tilemap.render(surface, self._camera, self._world.tileset, self._draw_tile_collision)

        if self._draw_blockmap:
            _, _, block_width, block_height = self._level.get_blockmap_dimensions()
            block_width = int(block_width)
            block_height = int(block_height)
            for y in range(0, self._level.tilemap.height * 32, block_height):
                for x in range(-24, self._level.tilemap.width * 32 + 24, block_width):
                    rx, ry = self._camera.world_to_camera(x, y)
                    surface.box(rx, ry, block_width, block_height, 0xFFFF00FF)

        if self._always_draw_entities:
            editing_entities = (self._edit_mode == self._edit_modes[EditMode.ENTITIES])
            if editing_entities:
                hover_entity = self._edit_mode.get_hover_entity()
            else:
                hover_entity = None

            draw_origin = editing_entities
            translucent = not editing_entities
            self.paint_entities(surface, draw_origin, hover_entity, translucent)

        self._edit_mode.paint(surface, self._camera, self._graphics)

        self._presenter.present()

    def paint_entities(self, surface, draw_origin=False, hover_entity=None, translucent=False):
        if translucent:
            blend_op = BlendOp.ALPHA50
        else:
            blend_op = BlendOp.ALPHA_SIMPLE

        for entity in self._level.entities:
            template = self._level.get_entity_template(entity.type, entity.subtype)
            if template is None:
                continue

            origin_x, origin_y = self._camera.world_to_camera(entity.x * Level.ORIGIN_SIZE, entity.y * Level.ORIGIN_SIZE)
            origin_width = Level.ORIGIN_SIZE
            origin_height = Level.ORIGIN_SIZE

            sprite_surfaces = self._graphics.get_surfaces(template.gfx)

            if sprite_surfaces:
                sprite_surface = sprite_surfaces[template.gfx_index]
                sprite_x = origin_x + template.offset_x
                sprite_y = origin_y + template.offset_y
                sprite_width = sprite_surface.width
                sprite_height = sprite_surface.height
            else:
                sprite_surface = None
                sprite_x = origin_x
                sprite_y = origin_y
                sprite_width = 0
                sprite_height = 0

            x1 = min(origin_x, sprite_x)
            y1 = min(origin_y, sprite_y)
            x2 = max(origin_x + origin_width, sprite_x + sprite_width)
            y2 = max(origin_y + origin_height, sprite_y + sprite_height)

            if not self._camera.screen_contains(x1, y1, x2, y2):
                continue

            if sprite_surface is not None:
                surface.blit_blend(sprite_surface, sprite_x, sprite_y, blend_op)
                if entity == hover_entity:
                    surface.outline(sprite_surface, sprite_x, sprite_y, COLOR_ENTITY_HOVER)
                elif entity.selected:
                    surface.outline(sprite_surface, sprite_x, sprite_y, COLOR_ENTITY_SELECTED)

            if draw_origin:
                surface.box_fill(origin_x, origin_y, origin_width, origin_height, COLOR_ORIGIN, BlendOp.ALPHA50)

    def viewport_mouse_right_down(self, event):
        if not self._camera:
            return
        if not self._world:
            return

        self._mouse_state = MouseState.MOVE
        self.Viewport.SetCursor(wx.StockCursor(wx.CURSOR_SIZING))
        self._move_last_pos = event.GetPosition()

    def viewport_mouse_right_up(self, event):
        if not self._camera:
            return
        if not self._world:
            return

        self._mouse_state = MouseState.NONE
        self.Viewport.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

    def viewport_mouse_move(self, event):
        if not self._camera:
            return
        if not self._world:
            return

        pos = event.GetPosition()
        pos = self._camera.camera_to_world(pos.x / self._presenter.scale, pos.y / self._presenter.scale)
        self._edit_mode.set_mouse_position(pos)

        if self._mouse_state == MouseState.MOVE:
            pos = event.GetPosition()

            delta_x = -((pos.x - self._move_last_pos[0]) * config.MOVE_SENSITIVITY) / self._presenter.scale
            delta_y = -((pos.y - self._move_last_pos[1]) * config.MOVE_SENSITIVITY) / self._presenter.scale

            self._camera.move_relative(delta_x, delta_y)

            if abs(delta_x) > 0:
                self._move_last_pos[0] = pos.x
            if abs(delta_y) > 0:
                self._move_last_pos[1] = pos.y

        else:
            self._edit_mode.mouse_move()

        self.Viewport.Refresh(False)

    def viewport_mouse_left_down(self, event):
        if not self._world:
            return

        self._edit_mode.mouse_left_down()
        self.Viewport.Refresh(False)

    def viewport_mouse_left_up(self, event):
        if not self._world:
            return

        self._edit_mode.mouse_left_up()
        self.Viewport.Refresh(False)

    def set_show_entities_menu(self, event):
        self._always_draw_entities = not self._always_draw_entities
        self.update_menu_state()
        self.Viewport.Refresh(False)

    def set_show_collision_menu(self, event):
        self._draw_tile_collision = not self._draw_tile_collision
        self.update_menu_state()
        self.Viewport.Refresh(False)

    def set_show_blockmap_menu(self, event):
        self._draw_blockmap = not self._draw_blockmap
        self.update_menu_state()
        self.Viewport.Refresh(False)

    def update_menu_state(self):
        self.LevelShowEntities.Check(self._always_draw_entities)
        self.LevelShowCollision.Check(self._draw_tile_collision)
        self.LevelShowBlockmap.Check(self._draw_blockmap)
        self.Tiles.show_collision(self._draw_tile_collision)

    def about(self, event):
        about = DialogAbout()
        about.ShowModal()

    def level_choice(self, event):
        index = self.LevelSelect.GetSelection()
        data = self.LevelSelect.GetClientData(index)
        self.select_level(data[0], data[1])

    def goto_start(self, event):
        self.center_on_start()
        self.Viewport.Refresh(False)

    def select_level(self, world, level):
        self._world = self._worlds[world]
        self._level = self._world.levels[level]

        self._presenter = Presenter.from_window(self.Viewport.GetHandle(), config.SCALE)

        if self._level.camera:
            self._camera = self._level.camera
            self._camera.set_size(self._presenter.surface.width, self._presenter.surface.height)
        else:
            width = self._presenter.surface.width
            height = self._presenter.surface.height
            max_x = self._level.tilemap.width * Tilemap.TILE_SIZE
            max_y = self._level.tilemap.height * Tilemap.TILE_SIZE
            self._camera = Camera(width, height, max_x, max_y)
            self._level.camera = self._camera
            self.center_on_start()

        for edit_mode in self._edit_modes.values():
            edit_mode.set_level(self._world, self._level)

        self.Tiles.set_tileset(self._world.tileset)
        self.Entities.set_level(self._level)
        self.update_status()
        self.update_title()

        self.Layout()
        self.Viewport.Refresh(False)

    def center_on_start(self):
        if not self._world:
            return

        x = (self._level.camera_tile_x * Tilemap.TILE_SIZE) + 152 - self._camera.width / 2
        y = (self._level.camera_tile_y * Tilemap.TILE_SIZE) + 96 - self._camera.height / 2
        self._camera.move_absolute(x, y)

    def undo_add(self):

        # If the undo stack has reached it's maximum size, prune off the first item.
        if len(self._level.undo) == config.MAX_UNDO:
            self._level.undo = self._level.undo[1:]
            self._level.undo_index -= 1

        # Prune the stack up to and including the current item.
        self._level.undo = self._level.undo[0:self._level.undo_index + 1]

        self._level.undo.append(self.undo_store_item())
        self._level.undo_index += 1

    def undo_do_undo(self):
        if not self._world:
            return
        if self._level.undo_index == -1:
            return

        undo_item = self._level.undo[self._level.undo_index]
        self._level.undo_index -= 1
        self.undo_restore_item(undo_item)

    def undo_restore_item(self, item):
        editmode = self._edit_modes[item['editmode']]
        editmode.undo_restore_item(item['data'])

    def undo_store_item(self):
        value_index = self._edit_modes.values().index(self._edit_mode)
        edit_mode_key = self._edit_modes.keys()[value_index]

        return {
            'editmode': edit_mode_key,
            'data': self._edit_mode.undo_store_item()
        }

    def undo(self, event):
        if not self._world:
            return

        self.undo_do_undo()

    def save(self, event):
        if not self._world:
            return

        self._world.save()
        self.update_title()

    def close_menu(self, event):
        self.Close(False)

    def close(self, event):
        if not self._world:
            event.Skip()
            return

        modified = False
        for level in self._world.levels:
            modified = modified | level.modified

        if modified:
            result = wx.MessageBox('Do you want to save your changes?', 'Unsaved changes', wx.YES_NO | wx.CANCEL | wx.ICON_EXCLAMATION)
            if result == wx.YES:
                self._world.save()
            elif result == wx.CANCEL:
                return

        event.Skip()

    def update_title(self):
        if self._level.modified:
            modified = ' *'
        else:
            modified = ''
        self.SetTitle('{} - {}{}'.format(config.APP_NAME, self._level.name, modified))

    def refresh_viewport(self):
        self.Viewport.Refresh(False)

    def set_viewport_cursor(self, stock_cursor):
        self.Viewport.SetCursor(wx.StockCursor(stock_cursor))

    def selection_tile(self, event):
        self._edit_modes[EditMode.TILES].set_selection(event.selection)

    def selection_entity(self, event):
        self._edit_modes[EditMode.ENTITIES].set_template(event.template)

    def set_level_modified(self, is_modified):
        self._level.modified = is_modified
        self.update_title()

    def update_status(self):
        bytes_left = self._level.get_entity_bytes_left()
        if bytes_left < 0:
            self.Status.SetStatusText('No entity bytes left!', 0)
            wx.MessageBox('There is no more room for entities. Delete entities or move entites to create empty blockmap blocks to free up more room. This level cannot be saved until enough room is made available.', 'No more room for entities', wx.ICON_EXCLAMATION | wx.OK)
        else:
            self.Status.SetStatusText('{} entity bytes left'.format(bytes_left), 0)
