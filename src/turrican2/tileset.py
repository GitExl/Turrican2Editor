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

from renderlib.bitplane import Bitplane, MaskMode, BitplaneType
from renderlib.surface import Surface, BlendOp


class CollisionType(object):
    SOLID = 1
    DESTRUCTABLE = 127
    SECRET = 128
    HURT = 211


class Tile(object):

    def __init__(self):
        self.surface = None
        self.surface_collision = None
        self.collision = None

    def render_collision(self):
        self.surface_collision = self.surface.clone()

        for index in range(0, 16):
            if not self.collision[index]:
                continue

            value = self.collision[index]
            if value == CollisionType.SOLID:
                color = 0xFFFFFFFF
            elif value == CollisionType.DESTRUCTABLE:
                color = 0xFF00FF00
            elif value == CollisionType.HURT:
                color = 0xFFFF0000
            elif value == CollisionType.SECRET:
                color = 0xFFFF00FF
            else:
                raise Exception('Unknown tile collision value {}.'.format(value))

            x = (index % 4) * 8
            y = int(index / 4) * 8
            self.surface_collision.box_fill(x, y, 8, 8, color, BlendOp.ALPHA50)


class TileSet(object):

    def __init__(self, tiles):
        self._tiles = tiles

    @classmethod
    def from_stream(cls, stream, offset_gfx, offset_collision, palette):

        stream.seek(offset_gfx)
        tile_count = int(stream.read_uint() / 4)

        stream.seek(offset_gfx)
        tile_offsets = []
        for _ in range(0, tile_count):
            offset = offset_gfx + stream.read_uint()
            tile_offsets.append(offset)

        # Read tile graphics.
        tiles = []
        for offset in tile_offsets:
            stream.seek(offset)
            bitplane = Bitplane.from_stream(stream, BitplaneType.PLANAR, 32, 32, 4)
            surface = bitplane.create_surface(None, palette, 0, 0, MaskMode.NONE)

            tile = Tile()
            tile.surface = surface
            tiles.append(tile)

        # Read collision data.
        stream.seek(offset_collision)
        for tile in tiles:
            tile.collision = [0] * 16
            for index in range(0, 16):
                tile.collision[index] = stream.read_ubyte()
            tile.render_collision()

        return cls(tiles)

    @property
    def tiles(self):
        return self._tiles
