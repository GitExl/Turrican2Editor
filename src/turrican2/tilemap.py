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
from typing import List

from renderlib.stream_read import StreamRead
from renderlib.stream_write import StreamWrite
from renderlib.surface import Surface

from turrican2.tileset import TileSet

from ui.camera import Camera


class Tilemap:

    TILE_SIZE: int = 32

    def __init__(self, tiles: List[int], width: int, height: int):
        self._tiles: List[int] = tiles
        self._width: int = width
        self._height: int = height

    @classmethod
    def from_stream(cls, stream: StreamRead, width: int, height: int):
        tiles = [0] * width * height

        for x in range(0, width):
            for y in range(0, height):
                tiles[x + y * width] = stream.read_ubyte()

        return cls(tiles, width, height)

    @classmethod
    def from_tilemap(cls, other, x1: int, y1: int, x2: int, y2: int):
        other_tiles = other.tiles

        width = x2 - x1
        height = y2 - y1
        tiles = [0] * width * height

        for y in range(y1, y2):
            for x in range(x1, x2):
                if x < 0 or x >= other.width:
                    continue
                if y < 0 or y >= other.height:
                    continue

                tiles[(x - x1) + (y - y1) * width] = other_tiles[x + y * other.width]

        return cls(tiles, width, height)

    def write_to(self, stream: StreamWrite):
        for x in range(0, self._width):
            for y in range(0, self._height):
                stream.write_ubyte(self._tiles[x + y * self._width])

    def render(self, surface: Surface, camera: Camera, tileset: TileSet, collision: bool = False):
        start_x: int = int(math.floor(camera.x / Tilemap.TILE_SIZE))
        start_y: int = int(math.floor(camera.y / Tilemap.TILE_SIZE))
        end_x: int = int(math.floor((camera.x + camera.width) / Tilemap.TILE_SIZE)) + 1
        end_y: int = int(math.floor((camera.y + camera.height) / Tilemap.TILE_SIZE)) + 1

        end_x: int = min(end_x, self._width)
        end_y: int = min(end_y, self._height)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                offset = x + y * self._width
                if offset >= len(self._tiles):
                    continue
                    
                index = self._tiles[offset]
                if index >= len(tileset.tiles):
                    continue

                tile = tileset.tiles[index]
                tile_x, tile_y = camera.world_to_camera(x * Tilemap.TILE_SIZE, y * Tilemap.TILE_SIZE)
                if collision:
                    surface.blit(tile.surface_collision, tile_x, tile_y)
                else:
                    surface.blit(tile.surface, tile_x, tile_y)

    def render_all(self, surface: Surface, tileset: TileSet, pos_x: int, pos_y: int, collision: bool = False):
        for y in range(0, self._height):
            for x in range(0, self._width):
                index = self._tiles[x + y * self._width]
                if index >= len(tileset.tiles):
                    continue

                tile = tileset.tiles[index]
                rx = int(pos_x + x * Tilemap.TILE_SIZE)
                ry = int(pos_y + y * Tilemap.TILE_SIZE)

                if collision:
                    surface.blit(tile.surface_collision, rx, ry)
                else:
                    surface.blit(tile.surface, rx, ry)

    def put_from(self, other, put_x: int, put_y: int):
        other_tiles = other.tiles

        for y in range(0, other.height):
            for x in range(0, other.width):
                if put_x + x < 0 or put_y + y < 0:
                    continue
                if put_x + x >= self._width or put_y + y >= self._height:
                    continue

                src = x + y * other.width
                dest = put_x + x + (put_y + y) * self._width
                self._tiles[dest] = other_tiles[src]

    def fill_with(self, other, x1: int, y1: int, x2: int, y2: int):
        other_tiles = other.tiles
        other_x = 0
        other_y = 0

        for y in range(y1, y2):
            for x in range(x1, x2):
                if not (x < 0 or y < 0 or x >= self._width or y >= self._height):
                    src = other_x + other_y * other.width
                    dest = x + y * self._width
                    self._tiles[dest] = other_tiles[src]

                other_x += 1
                if other_x >= other.width:
                    other_x = 0

            other_x = 0
            other_y += 1
            if other_y >= other.height:
                other_y = 0

    def clear(self):
        self._width = 0
        self._height = 0
        self._tiles = []

    @property
    def tiles(self) -> List[int]:
        return self._tiles

    @tiles.setter
    def tiles(self, tiles: List[int]):
        self._tiles = tiles

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height
