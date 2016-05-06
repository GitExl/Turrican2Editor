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
import os.path

from renderlib.stream_read import StreamRead, Endianness
from renderlib.palette import Palette
from renderlib.bitplane import Bitplane, BitplaneType, MaskMode


class Graphics(object):

    def __init__(self, directory):
        self.graphics = {}
        self.load_graphics('graphics.json', directory)

    def get_surfaces(self, name):
        return self.graphics.get(name, None)

    def load_graphics(self, json_filename, directory):
        with open(json_filename, 'r') as fp:
            data = json.load(fp)

        # Read palettes.
        palettes = {}
        for filename, file_data in data.items():
            filename = os.path.join(directory, filename)
            stream = StreamRead.from_file(filename, Endianness.BIG)

            for pal_name, pal_data in file_data['palettes'].items():
                stream.seek(pal_data['offset'])
                palettes[pal_name] = Palette.from_stream(stream, pal_data['length'], 4)

        # Read and generate graphics.
        for filename, file_data in data.items():
            filename = os.path.join(directory, filename)
            stream = StreamRead.from_file(filename, Endianness.BIG)

            for gfx in file_data['graphics']:
                width = gfx['width']
                height = gfx['height']
                planes = gfx['planes']
                count = gfx['count']
                palette = palettes[gfx['palette']]

                # Determine the bitplane mode to use.
                if gfx['mode'] == 'amiga_sprite':
                    mode = BitplaneType.AMIGA_SPRITE
                elif gfx['mode'] == 'chunky':
                    mode = BitplaneType.CHUNKY
                elif gfx['mode'] == 'planar':
                    mode = BitplaneType.PLANAR
                else:
                    raise Exception('Unknown bitplane mode "{}".'.format(gfx['mode']))

                # Read all bitplanes in order.
                surfaces = []
                stream.seek(gfx['offset'])
                for _ in range(0, count):
                    bitplane = Bitplane.from_stream(stream, mode, width, height, planes)

                    # Create a surface, and use a masking mode if needed.
                    if gfx['mask'] == 'color_zero':
                        surface = bitplane.create_surface(None, palette, 0, 0, MaskMode.INDEX)
                    elif gfx['mask'] == 'none':
                        surface = bitplane.create_surface(None, palette, 0, 0, MaskMode.NONE)
                    elif gfx['mask'] == 'bitplane':
                        if gfx['mode'] == 'planar':
                            mask = bitplane.from_stream(stream, BitplaneType.PLANAR, width, height, planes)
                        else:
                            mask = bitplane.from_stream(stream, BitplaneType.CHUNKY, width, height, 1)
                        surface = bitplane.create_surface(mask, palette, 0, 0, MaskMode.BITPLANE)
                    else:
                        raise Exception('Unknown mask mode "{}".'.format(gfx['mask']))

                    if gfx['flip_y']:
                        surface = surface.flipped_y()

                    surfaces.append(surface)

                if gfx['name'] in self.graphics:
                    self.graphics[gfx['name']].extend(surfaces)
                else:
                    self.graphics[gfx['name']] = surfaces

