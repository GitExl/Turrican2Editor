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

import json
from typing import Dict, List, Optional, Tuple

from renderlib.stream_read import StreamRead
from renderlib.stream_write import StreamWrite
from turrican2.tilemap import Tilemap
from ui.camera import Camera


class Entity:

    def __init__(self, entity_type: int, entity_subtype: int):
        self.type: int = entity_type
        self.subtype: int = entity_subtype
        self.x: int = 0
        self.y: int = 0
        self.selected: bool = False


class EntityTemplate:

    def __init__(self, name: str, type: int, subtype: int, data: Dict):
        self.name: str = name

        self.type: int = type
        self.subtype: int = subtype

        self.gfx: str = data.get('gfx', 'fontsmall')
        self.gfx_index: int = data.get('gfx_index', 0)

        offset = data.get('offset', [0, 0])
        self.offset_x: int = offset[0]
        self.offset_y: int = offset[1]


class Block:

    def __init__(self):
        self.entities: List[Tuple[int, int, int]] = []
        self.offset: int = 0

    def write(self, stream: StreamWrite):
        for entity in self.entities:
            stream.write_ubyte(entity[0])
            stream.write_ubyte(entity[1])
            stream.write_ubyte(entity[2])
        stream.write_ubyte(0xFF)


class Level:

    ORIGIN_SIZE: int = 8

    BASE_OFFSET: int = 0x20700

    def __init__(self, world_index: int, level_index: int):
        self._world_index: int = world_index
        self._level_index: int = level_index
        self.name: str = 'Unnamed'

        self.undo: List = []
        self.undo_index: int = -1

        self._offset_level_data: int = 0
        self._offset_code_1: int = 0
        self._offset_code_2: int = 0
        self._offset_code_3: int = 0
        self._offset_pointers_behaviour: int = 0
        self._offset_blockmap_row_pointers: int = 0
        self._offset_blockmap_pointers: int = 0

        self._u1: int = 0
        self._u2: int = 0

        self._tilemap: Optional[Tilemap] = None
        self._entities: List[Entity] = []
        self._entity_templates: Dict[Tuple[int, int], EntityTemplate] = {}

        self._tilemap_width: int = 0
        self._tilemap_height: int = 0

        self.camera_tile_x: int = 0
        self.camera_tile_y: int = 0

        self.player_x: int = 0
        self.player_y: int = 0

        self._blockmap_width: int = 0
        self._blockmap_height: int = 0

        self.maximum_blockmap_size: int = 0

        self.camera: Optional[Camera] = None
        self.modified: bool = False

        self.load_entity_templates('entities/shared.json')
        self.load_entity_templates('entities/world{}-shared.json'.format(world_index + 1))
        self.load_entity_templates('entities/world{}-level{}.json'.format(world_index + 1, level_index + 1))

    def load_entity_templates(self, filename: str):
        with open(filename, 'r') as fp:
            data = json.load(fp)

        for type_key, data in data.items():
            type_key = int(type_key)
            type_data = data['type']

            for subtype_key, subtype_data in data['subtypes'].items():
                subtype_key = int(subtype_key)

                merged_data = type_data.copy()
                merged_data.update(subtype_data)

                type_name = type_data.get('name', 'Unnamed')
                subtype_name = subtype_data.get('name', None)

                if type_name and subtype_name:
                    name = '{} - {}'.format(type_name, subtype_name)
                elif subtype_name:
                    name = subtype_name
                else:
                    name = type_name

                key = (type_key, subtype_key)
                self._entity_templates[key] = EntityTemplate(name, type_key, subtype_key, merged_data)

    def save_header(self, stream):
        stream.write_uint(self._offset_level_data + Level.BASE_OFFSET)

        stream.write_ushort(self._tilemap_width)
        stream.write_ushort(self._tilemap_height)

        stream.write_short(self.camera_tile_x - 1)
        stream.write_short(self.camera_tile_y - 1)

        stream.write_short(self.player_x + 32)
        stream.write_short(self.player_y + 32)

        stream.write_ushort(self._blockmap_width - 1)
        stream.write_ushort(self._blockmap_height - 1)

        stream.write_uint(self._offset_code_1 + Level.BASE_OFFSET)
        stream.write_uint(self._offset_code_2 + Level.BASE_OFFSET)

        stream.write_ubyte(self._u1)
        stream.write_ubyte(0)
        stream.write_ubyte(0)
        stream.write_ubyte(0)

        stream.write_uint(self._offset_pointers_behaviour + Level.BASE_OFFSET)
        stream.write_uint(self._offset_blockmap_row_pointers + Level.BASE_OFFSET)
        stream.write_uint(self._offset_blockmap_pointers + Level.BASE_OFFSET)

        stream.write_ushort(self._u2)

        stream.write_uint(self._offset_code_3 + Level.BASE_OFFSET)

    def save(self, stream, offset=None):
        if offset is None:
            offset = self._offset_level_data

        stream.seek(offset)
        self._tilemap.write_to(stream)

    def load_header(self, stream):
        self._offset_level_data = stream.read_uint() - Level.BASE_OFFSET

        self._tilemap_width = stream.read_ushort()
        self._tilemap_height = stream.read_ushort()

        self.camera_tile_x = stream.read_short() + 1
        self.camera_tile_y = stream.read_short() + 1

        self.player_x = stream.read_short() - 32
        self.player_y = stream.read_short() - 32

        self._blockmap_width = stream.read_ushort() + 1
        self._blockmap_height = stream.read_ushort() + 1

        self._offset_code_1 = stream.read_uint() - Level.BASE_OFFSET
        self._offset_code_2 = stream.read_uint() - Level.BASE_OFFSET

        self._u1 = stream.read_ubyte()
        stream.skip(3)

        self._offset_pointers_behaviour = stream.read_uint() - Level.BASE_OFFSET

        self._offset_blockmap_row_pointers = stream.read_uint() - Level.BASE_OFFSET
        self._offset_blockmap_pointers = stream.read_uint() - Level.BASE_OFFSET

        # Music track index? Modify and test.
        self._u2 = stream.read_ushort()

        self._offset_code_3 = stream.read_uint() - Level.BASE_OFFSET

    def load(self, stream: StreamRead, offset: int=0):
        stream.seek(self._offset_level_data + offset)
        self._tilemap = Tilemap.from_stream(stream, self._tilemap_width, self._tilemap_height)

        self.read_entities(stream, self._offset_blockmap_pointers)

    def write_entities(self, stream: StreamWrite):

        # Generate blockmap blocks and adjust width\height of the blockmap in the process.
        blocks = self.generate_blocks()
        self._offset_blockmap_pointers = self._offset_blockmap_row_pointers + self._blockmap_height * 2

        # Write row pointers.
        stream.seek(self._offset_blockmap_row_pointers)
        for row in range(0, self._blockmap_height):
            stream.write_ushort(row * (self._blockmap_width * 4))

        # Write blocks.
        stream.seek(self._offset_blockmap_pointers + len(blocks) * 4)
        zero_block = None
        for block in blocks:
            if not len(block.entities):
                if not zero_block:
                    zero_block = block
                    block.offset = stream.index
                    block.write(stream)
                else:
                    block.offset = zero_block.offset
            else:
                block.offset = stream.index
                block.write(stream)

        # Write block offsets.
        stream.seek(self._offset_blockmap_pointers)
        for index, block in enumerate(blocks):
            stream.write_uint(Level.BASE_OFFSET + block.offset)

    def generate_blocks(self) -> List[Block]:
        self._blockmap_width, self._blockmap_height, block_width, block_height = self.get_blockmap_dimensions()

        length: int = self._blockmap_width * self._blockmap_height
        blocks: List[Block] = []

        for _ in range(0, length):
            blocks.append(Block())

        for entity in self._entities:
            block_x = int(((entity.x + 3) * 8) / block_width)
            block_y = int((entity.y * 8) / block_height)

            if block_x < 0:
                block_x = 0
            elif block_x >= self._blockmap_width:
                block_x = self._blockmap_width - 1
            if block_y < 0:
                block_y = 0
            elif block_y >= self._blockmap_height:
                block_y = self._blockmap_height - 1

            block_index = block_x + block_y * self._blockmap_width
            if block_index < 0 or block_index >= len(blocks):
                continue

            data = (entity.type & 0xF) | ((entity.subtype & 0xF) << 4)
            x = (entity.x + 3) - block_x * 32
            y = entity.y - block_y * 32
            blocks[block_index].entities.append((data, x, y))

        # Prune empty last row.
        empty = True
        for x in range(0, self._blockmap_width):
            block_index = x + (self._blockmap_height - 1) * self._blockmap_width
            if len(blocks[block_index].entities) > 0:
                empty = False
                break

        if empty:
            blocks = blocks[0:-self._blockmap_width]
            self._blockmap_height -= 1

        # Prune empty last column
        empty = True
        for y in range(0, self._blockmap_height):
            block_index = (self._blockmap_width - 1) + y * self._blockmap_width
            if len(blocks[block_index].entities) > 0:
                empty = False
                break

        if empty:
            self._blockmap_width -= 1
            new_blocks = []
            for y in range(0, self._blockmap_height):
                start_index = y * self._blockmap_width
                new_blocks.extend(blocks[start_index:start_index + self._blockmap_width])
            blocks = new_blocks

        return blocks

    def read_entities(self, stream: StreamRead, offset_blockmap_pointers: int):
        row_offsets: List[int] = [0] * self._blockmap_height
        stream.seek(self._offset_blockmap_row_pointers)
        for row_index in range(0, self._blockmap_height):
            row_offsets[row_index] = stream.read_ushort()

        block_y = 0
        for row_offset in row_offsets:

            # Read row offsets to blockmap block data.
            block_offsets = [0] * self._blockmap_width
            stream.seek(offset_blockmap_pointers + row_offset)
            for offset_index in range(0, self._blockmap_width):
                block_offsets[offset_index] = stream.read_uint() - Level.BASE_OFFSET

            # Each block contains a list of entities that are inside it.
            block_x = 0
            for offset in block_offsets:
                stream.seek(offset)

                while True:
                    value = stream.read_ubyte()
                    if value == 0xFF:
                        break

                    entity_type = value & 0xF
                    entity_data = (value >> 4) & 0xF

                    entity = Entity(entity_type, entity_data)
                    entity.x = stream.read_ubyte() + block_x * 32 - 3
                    entity.y = stream.read_ubyte() + block_y * 32

                    entity.block_x = block_x
                    entity.block_y = block_y

                    self._entities.append(entity)

                block_x += 1

            block_y += 1

    def add_entity(self, template: EntityTemplate, x: int, y: int):
        entity = Entity(template.type, template.subtype)
        entity.x = x
        entity.y = y
        self._entities.append(entity)

    def remove_entity(self, entity: Entity):
        self._entities.remove(entity)

    def get_entity_template(self, entity_type: int, entity_subtype: int) -> EntityTemplate:
        template = self._entity_templates.get((entity_type, entity_subtype), None)
        if not template:
            raise Exception('Unknown entity template {}, {}.'.format(entity_type, entity_subtype))

        return template

    def get_entity_templates(self) -> Dict[Tuple[int, int], EntityTemplate]:
        return self._entity_templates

    def get_entities_inside(self, x1: int, y1: int, x2: int, y2: int) -> List[Entity]:
        selected = []

        for entity in self._entities:
            if entity.x < x1 or entity.x >= x2 or entity.y < y1 or entity.y >= y2:
                continue
            selected.append(entity)

        return selected

    def get_entity_at(self, x: int, y: int) -> Optional[Entity]:
        for entity in self._entities:
            if entity.x == x and entity.y == y:
                return entity

        return None

    def get_blockmap_dimensions(self) -> Tuple[int, int, float, float]:
        if self._tilemap.width <= 16:
            block_width = 512.0
        else:
            block_width = 256.0

        if self._tilemap.height <= 16:
            block_height = 512.0
        else:
            block_height = 256.0

        # TODO: calculating these sizes doesn't work out for all levels, since some entities are positioned
        #  outside the block they are in, causing the original levels' blockmaps to be truncated in width or height.
        #  blockmap_width = int(math.ceil((self._tilemap_width * Tilemap.TILE_SIZE + 48) / block_width))
        #  blockmap_height = int(math.ceil((self._tilemap_height * Tilemap.TILE_SIZE) / block_height))
        blockmap_width = self._blockmap_width
        blockmap_height = self._blockmap_height

        return blockmap_width, blockmap_height, block_width, block_height

    def calculate_blockmap_size(self) -> int:
        blockmap_width, blockmap_height, block_width, block_height = self.get_blockmap_dimensions()

        length = blockmap_width * blockmap_height
        block_sizes = [0] * length

        for entity in self._entities:
            block_x = int(((entity.x + 3) * 8) / block_width)
            block_y = int((entity.y * 8) / block_height)

            if block_x < 0:
                block_x = 0
            elif block_x >= blockmap_width:
                block_x = blockmap_width - 1
            if block_y < 0:
                block_y = 0
            elif block_y >= blockmap_height:
                block_y = blockmap_height - 1

            block_index = block_x + block_y * blockmap_width

            if block_index < 0 or block_index >= len(block_sizes):
                continue

            block_sizes[block_index] += 3

        # Prune empty last row.
        empty = True
        for x in range(0, blockmap_width):
            block_index = x + (blockmap_height - 1) * blockmap_width
            if block_sizes[block_index] > 0:
                empty = False
                break

        if empty:
            block_sizes = block_sizes[0:-blockmap_width]
            blockmap_height -= 1

        # Prune empty last column
        empty = True
        for y in range(0, blockmap_height):
            block_index = (blockmap_width - 1) + y * blockmap_width
            if block_sizes[block_index] > 0:
                empty = False
                break

        if empty:
            blockmap_width -= 1
            new_sizes = []
            for y in range(0, blockmap_height):
                start_index = y * blockmap_width
                new_sizes.extend(block_sizes[start_index:start_index + blockmap_width])
            block_sizes = new_sizes

        # Entity lists + terminators.
        size = 0
        had_zero = False
        for block_size in block_sizes:
            if block_size == 0:
                if not had_zero:
                    size += 1
                    had_zero = True
            else:
                size += block_size + 1

        # Block pointers.
        size += len(block_sizes) * 4

        # Row pointers.
        size += blockmap_height * 2

        return size

    def get_entity_bytes_left(self) -> int:
        size = self.calculate_blockmap_size()
        max_size = self.maximum_blockmap_size
        return max_size - size

    def can_save(self) -> bool:
        bytes_left = self.get_entity_bytes_left()
        if bytes_left < 0:
            return False

        return True

    @property
    def tilemap(self) -> Tilemap:
        return self._tilemap

    @property
    def entities(self) -> List[Entity]:
        return self._entities

    @entities.setter
    def entities(self, entities: List[Entity]):
        self._entities = entities

    @property
    def data_offset(self) -> int:
        return self._offset_level_data
