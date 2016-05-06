/*
  Copyright (c) 2016, Dennis Meuwissen
  All rights reserved.

  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions are met:

  1. Redistributions of source code must retain the above copyright notice, this
     list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright notice,
     this list of conditions and the following disclaimer in the documentation
     and/or other materials provided with the distribution.

  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#include "renderlib.h"
#include "utils.h"
#include "streamread.h"
#include "palette.h"


Palette* paletteCreate(const uint8_t length) {
  Palette* pal = calloc(1, sizeof(Palette));
  if (!pal) {
    return NULL;
  }

  pal->length = length;
  pal->entries = calloc(length, sizeof(uint32_t));

  return pal;
}

EXPORT void paletteDestroy(Palette* pal) {
  if (!pal) {
    return;
  }

  free(pal->entries);
  free(pal);
}

EXPORT Palette* paletteReadFromStream(StreamRead* stream, const uint8_t length, const uint8_t bits_per_channel, const bool read_alpha) {
  Palette* pal = paletteCreate(length);
  if (!pal) {
    return NULL;
  }

  uint32_t value;
  uint8_t a, r, g, b;
  uint8_t index;

  if (bits_per_channel == 8) {
    for (index = 0; index < length; index++) {
      value = streamReadInt(stream);

      a = read_alpha ? (value >> 24) & 0xFF : 0;
      r = (value >> 16) & 0xFF;
      g = (value >> 8) & 0xFF;
      b = value & 0xFF;

      pal->entries[index] = BGRA(r, g, b, a);
    }

  } else if (bits_per_channel == 4) {
    for (index = 0; index < length; index++) {
      value = streamReadShort(stream);

      a = read_alpha ? ((value >> 12) & 0xF) * 17 : 0;
      r = ((value >> 8) & 0xF) * 17;
      g = ((value >> 4) & 0xF) * 17;
      b = (value & 0xF) * 17;

      pal->entries[index] = BGRA(r, g, b, a);
    }

  } else if (bits_per_channel == 2) {
    for (index = 0; index < length; index++) {
      value = streamReadByte(stream);

      a = read_alpha ? ((value >> 6) & 0x3) * 85 : 0;
      r = ((value >> 4) & 0x3) * 85;
      g = ((value >> 2) & 0x3) * 85;
      b = (value & 0x3) * 85;

      pal->entries[index] = BGRA(r, g, b, a);
    }

  } else {
    return NULL;

  }

  return pal;
}
