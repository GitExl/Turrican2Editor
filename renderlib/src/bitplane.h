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

#ifndef H_BITPLANE
#define H_BITPLANE

typedef struct {
  uint32_t width;
  uint32_t height;
  uint8_t planes;
  uint8_t* data;
  uint32_t length;
} Bitplane;

typedef enum {
  BITPLANE_TYPE_CHUNKY = 0,
  BITPLANE_TYPE_PLANAR = 1,
  BITPLANE_TYPE_AMIGA_SPRITE = 2
} BitplaneType;

typedef enum {
  MASK_MODE_NONE = 0,
  MASK_MODE_INDEX = 1,
  MASK_MODE_BITPLANE = 2
} MaskMode;

Bitplane* bitplaneCreate (const uint32_t width, const uint32_t height, const uint8_t planes);

EXPORT Bitplane* bitplaneCreateFromStream (StreamRead* stream, BitplaneType type, const uint32_t width, const uint32_t height, const uint8_t planes);
EXPORT void      bitplaneDestroy          (Bitplane* bp);
EXPORT Surface*  bitplaneToSurface        (const Bitplane* bp, const Bitplane* mask, const Palette* palette, const uint32_t maskColor, const int32_t shift, const MaskMode mode);

#endif
