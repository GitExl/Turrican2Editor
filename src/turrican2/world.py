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

import wx

from renderlib.stream_read import StreamRead, Endianness
from renderlib.stream_write import StreamWrite
from renderlib.palette import Palette

from turrican2.tileset import TileSet
from turrican2.level import Level


WORLD_BASE_OFFSET = 0x20700


class World(object):

    def __init__(self):
        self._filename = None
        self._world_index = 0

        self._offset_tile_gfx = 0
        self._offset_tile_collision = 0
        self._offset_palette = 0
        self._offset_u1 = 0
        self._offset_u2 = 0
        self._level_offsets = None

        self._levels = None
        self._palette = None
        self._tileset = None
        self._sprites = None

    def save(self):
        stream = StreamWrite.from_file(self._filename, Endianness.BIG)
        levels_not_saved = 0

        for level_index, level in enumerate(self._levels):
            if level.modified:

                if not level.can_save():
                    levels_not_saved += 1
                    continue

                # Write entities first.
                level.write_entities(stream)

                # Save level data.
                if level_index == 0:
                    level.save(stream)
                else:
                    filename = 'L{}-{}'.format(self._world_index + 1, level_index + 1)
                    game_dir = os.path.dirname(self._filename)
                    filename = os.path.join(game_dir, filename)

                    level_stream = StreamWrite.from_file(filename, Endianness.BIG)

                    if self._world_index == 2 and level_index == 1:
                        offset = 19620
                    else:
                        offset = 0
                    level.save(level_stream, offset)
                    level_stream.write_to_file(filename)

                # Save level header.
                stream.seek(self._level_offsets[level_index])
                level.save_header(stream)
                level.modified = False

        stream.write_to_file(self._filename)

        if levels_not_saved:
            wx.MessageBox('{} level(s) could not be saved.'.format(levels_not_saved), 'Levels not saved', wx.ICON_INFORMATION | wx.OK)

    def load(self, filename, data):
        self._filename = filename
        self._world_index = int(os.path.basename(filename)[1]) - 1

        stream = StreamRead.from_file(filename, Endianness.BIG)

        self._offset_tile_gfx = stream.read_uint() - WORLD_BASE_OFFSET
        self._offset_tile_collision = stream.read_uint() - WORLD_BASE_OFFSET
        self._offset_palette = stream.read_uint() - WORLD_BASE_OFFSET
        self._offset_u1 = stream.read_uint() - WORLD_BASE_OFFSET
        self._offset_u2 = stream.read_uint() - WORLD_BASE_OFFSET

        if self._offset_tile_gfx > stream.size or self._offset_tile_collision > stream.size or self._offset_palette > stream.size:
            raise Exception('"{}" is not a valid world file.'.format(filename))

        # Read level header offsets.
        level_count = stream.read_ushort()
        self._level_offsets = []
        for _ in range(0, level_count):
            self._level_offsets.append(stream.read_uint() - WORLD_BASE_OFFSET)

        # Read level headers.
        self._levels = []
        for level_index, offset in enumerate(self._level_offsets):
            stream.seek(offset)

            level = Level(self._world_index, level_index)
            level.name = '{}-{}: {}'.format(self._world_index + 1, level_index + 1, data[level_index]['name'])
            level.maximum_blockmap_size = data[level_index]['blockmap_size']
            level.load_header(stream)
            self._levels.append(level)

        # Read the world palette.
        stream.seek(self._offset_palette)
        self._palette = Palette.from_stream(stream, 16, 4)

        # Read tileset.
        self._tileset = TileSet.from_stream(stream, self._offset_tile_gfx, self._offset_tile_collision, self._palette)

        # Read level data.
        for level_index, level in enumerate(self._levels):
            if level_index > 0:
                game_dir = os.path.dirname(filename)
                level_file = 'L{}-{}'.format(self._world_index + 1, level_index + 1)
                level_file = os.path.join(game_dir, level_file)
                stream.insert(level_file, level.data_offset)

            if self._world_index == 2 and level_index == 1:
                offset = 19620
            else:
                offset = 0

            level.load(stream, offset)

    @property
    def levels(self):
        return self._levels

    @property
    def tileset(self):
        return self._tileset
