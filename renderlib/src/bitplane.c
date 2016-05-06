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
#include "surface.h"
#include "streamread.h"
#include "palette.h"
#include "bitplane.h"


/**
 * Creates a new Bitplane.
 *
 * @param  width  The width of the new Bitplane.
 * @param  height The height of the new Bitplane.
 * @param  planes The number of planes of the new Bitplane.
 *
 * @return        A new Bitplane or NULL if one could not be created.
 */
Bitplane* bitplaneCreate(const uint32_t width, const uint32_t height, const uint8_t planes) {
  if (planes > 7) {
    return NULL;
  }

  Bitplane* bp = calloc(1, sizeof(Bitplane));
  if (!bp) {
    return NULL;
  }

  bp->width = width;
  bp->height = height;
  bp->planes = planes;
  bp->length = width * height * sizeof(uint8_t);

  bp->data = calloc(1, bp->length);
  if (!bp->data) {
    return NULL;
  }

  return bp;
}

/**
 * Reads "Amiga sprite" bitmap data into a Bitplane.
 *
 * An Amiga sprite consists of 2 chunky sprites that the Amiga sprite hardware combines into a single sprite.
 *
 * @param  stream The StreamRead to read from.
 * @param  width  The width of the image data.
 * @param  height The height of the image data.
 *
 * @return        A new Bitplane or NULL if one could not be created.
 */
Bitplane* bitplaneCreateAmigaSprite(StreamRead* stream, const uint32_t height) {
  Bitplane* bp = bitplaneCreate(32, height, 4);

  uint32_t ix, plane, y, x;
  int8_t shift = 7;
  uint8_t value = streamReadByte(stream);

  for (ix = 0; ix < 32; ix += 16) {
    for (plane = 0; plane < 4; plane += 2) {
      for (y = 0; y < height; y++) {
        for (x = 0; x < 32; x++) {

          if (shift < 0) {
            shift = 7;
            value = streamReadByte(stream);
          }

          if ((value >> shift) & 0x1) {
            if (x < 16) {
              bp->data[y * 32 + x + ix] |= (1 << plane);
            } else {
              bp->data[y * 32 + x + ix - 16] |= (1 << (plane + 1));
            }
          }

          shift--;
        }
      }
    }
  }

  return bp;
}

/**
 * Reads "planar" bitmap data into a Bitplane.
 *
 * @param  stream The StreamRead to read from.
 * @param  width  The width of the image data.
 * @param  height The height of the image data.
 * @param  planes The number of bitplanes in the image data.
 *
 * @return        A new Bitplane or NULL if one could not be created.
 */
Bitplane* bitplaneCreatePlanar(StreamRead* stream, const uint32_t width, const uint32_t height, const uint8_t planes) {
  if (planes > 8) {
    return NULL;
  }

  Bitplane* bp = bitplaneCreate(width, height, planes);

  uint32_t x, y, plane;
  int8_t shift = 7;
  uint8_t value = streamReadByte(stream);

  for (y = 0; y < height; y++) {
    for (plane = 0; plane < planes; plane++) {
      for (x = 0; x < width; x++) {
        if (shift < 0) {
          shift = 7;
          value = streamReadByte(stream);
        }

        if ((value >> shift) & 0x1) {
          bp->data[y * width + x] |= (1 << plane);
        }

        shift--;
      }
    }
  }

  return bp;
}

/**
 * Reads "chunky" bitmap data into a Bitplane.
 *
 * @param  stream The StreamRead to read from.
 * @param  width  The width of the image data.
 * @param  height The height of the image data.
 * @param  planes The number of bitplanes in the image data.
 *
 * @return        A new Bitplane or NULL if one could not be created.
 */
Bitplane* bitplaneCreateChunky(StreamRead* stream, const uint32_t width, const uint32_t height, const uint8_t planes) {
  if (planes > 7) {
    return NULL;
  }

  Bitplane* bp = bitplaneCreate(width, height, planes);

  uint32_t x, y, plane;
  int8_t shift = 7;
  uint8_t value = streamReadByte(stream);

  for (plane = 0; plane < planes; plane++) {
    for (y = 0; y < height; y++) {
      for (x = 0; x < width; x++) {
        if (shift < 0) {
          shift = 7;
          value = streamReadByte(stream);
        }

        if ((value >> shift) & 0x1) {
          bp->data[y * width + x] |= (1 << plane);
        }

        shift--;
      }
    }
  }

  return bp;
}

/**
 * Creates a new Bitplane from image data.
 *
 * @param  type   A BITPLANE_TYPE_* constant indicating what type of data it is.
 * @param  stream The stream to read the image data from.
 * @param  width  The width of the image data.
 * @param  height The height of the image data.
 * @param  planes The number of bitplanes in the image data, if relevant.
 *
 * @return        A new Bitplane or NULL if one could not be created.
 */
EXPORT Bitplane* bitplaneCreateFromStream(StreamRead* stream, BitplaneType type, const uint32_t width, const uint32_t height,
                                          const uint8_t planes) {
  if (!stream) {
    return NULL;
  }

  switch (type) {
    case BITPLANE_TYPE_PLANAR:       return bitplaneCreatePlanar(stream, width, height, planes);
    case BITPLANE_TYPE_CHUNKY:       return bitplaneCreateChunky(stream, width, height, planes);
    case BITPLANE_TYPE_AMIGA_SPRITE: return bitplaneCreateAmigaSprite(stream, height);
  }

  return NULL;
}

/**
 * Destroys and frees a Bitplane.
 *
 * @param  bp The Bitplane to destroy.
 */
EXPORT void bitplaneDestroy(Bitplane* bp) {
  if (!bp) {
    return;
  }

  free(bp->data);
  free(bp);
}

/**
 * Converts a Bitplane to a surface.
 *
 * @param  bp        The Bitplane to convert.
 * @param  mask      A Bitplane to use as a mask, or NULL if no mask is used.
 * @param  palette   Pointer to an RGBA palette to convert the Bitplane with.
 * @param  maskColor The color that will be transparent.
 * @param  shift     The number of bits to shift Bitplane pixels with before converting.
 * @param  mode      A BITPLANE_MASK_* value that determines whether the mask Bitplane is used or the maskColor is
 *                   used for masking.
 *
 * @return           A new Surface containing the converted Bitplane or NULL if it could not be converted.
 */
EXPORT Surface* bitplaneToSurface(const Bitplane* bp, const Bitplane* mask, const Palette* palette,
                                  const uint32_t maskColor, const int32_t shift, const MaskMode mode) {
  if (!bp) {
    return NULL;
  }

  Surface* surface = surfaceCreate(bp->width, bp->height);

  // Convert all Bitplane pixels to BGRA.
  uint32_t pixel;
  for (pixel = 0; pixel < bp->length; pixel++) {
    surface->data[pixel] = palette->entries[bp->data[pixel] + shift] | 0xFF000000;
  }

  // Transparency by mask image if present.
  if (mode == MASK_MODE_BITPLANE && mask) {

    // The mask Bitplane size must match the source Bitplane size.
    if (bp->width != mask->width || bp->height != mask->height) {
      return NULL;
    }

    // Zero out alpha of masked out pixels.
    for (pixel = 0; pixel < bp->length; pixel++) {
      if (mask->data[pixel]) {
        continue;
      }
      surface->data[pixel] &= 0x00FFFFFF;
    }

  // Transparency by color index.
  } else if (mode == MASK_MODE_INDEX) {
    for (pixel = 0; pixel < bp->length; pixel++) {
      if (bp->data[pixel] != maskColor) {
        continue;
      }
      surface->data[pixel] &= 0x00FFFFFF;
    }
  }

  return surface;
}
