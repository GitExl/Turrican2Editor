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
#include "font.h"
#include "utils.h"
#include "render.h"


/**
 * Inline functions for mixing pixel data.
 */
static inline uint32_t renderPixelAlphaSimple(const uint32_t dest, const uint32_t src) {
  return (ALPHA(src) == 0xFF) ? src : dest;
}

static inline uint32_t renderPixelSolid(const uint32_t src) {
  return (src | 0xFF000000);
}

static inline uint32_t renderPixelAlpha50(const uint32_t dest, const uint32_t src) {
  if (ALPHA(src) == 0xFF) {
    return (((dest & 0x00FEFEFE) >> 1) + ((src & 0x00FEFEFE) >> 1)) | (0xFF << 24);
  }

  return dest;
}

static inline uint32_t renderPixelAlpha(const uint32_t dest, const uint32_t src) {
  if (ALPHA(src) == 0) {
    return dest;
  } else if (ALPHA(src) == 0xFF) {
    return src;
  }

  const uint8_t alpha = ALPHA(src);
  const uint32_t RB = (((src & 0x00FF00FF) * alpha) + ((dest & 0x00FF00FF) * (0xFF - alpha))) & 0xFF00FF00;
  const uint32_t G =  (((src & 0x0000FF00) * alpha) + ((dest & 0x0000FF00) * (0xFF - alpha))) & 0x00FF0000;

  return (0xFF << 24) | (RB | G) >> 8;
}

/**
 * Renders an outline from a surface's alpha mask.
 *
 * @param destSurface The Surface to render to.
 * @param srcSurface  The Surface to draw the outline of.
 * @param rx          The x coordinate to render to.
 * @param ry          The y coordinate to render to.
 * @param color       The color of the outline.
 */
EXPORT void renderOutline(const Surface* destSurface, const Surface* srcSurface, const int32_t rx, const int32_t ry, const uint32_t color) {
  int32_t x, y;
  int32_t cx, cy;

  for(y = 0; y < srcSurface->height; y++) {
    for(x = 0; x < srcSurface->width; x++) {
      if (ALPHA(srcSurface->rows[y][x]) != 0) {
        cx = x + rx;
        cy = y + ry;

        // Inside destination surface.
        if (cx - 1 >= 0 && cx - 1 < destSurface->width && cy >= 0 && cy < destSurface->height) {

          // Inside source surface and no source alpha, or outside source surface.
          if ((x - 1 >= 0 && ALPHA(srcSurface->rows[y][x - 1]) == 0) || x - 1 < 0) {
            destSurface->rows[cy][cx - 1] = renderPixelSolid(color);
          }
        }

        if (cx >= 0 && cx < destSurface->width && cy - 1 >= 0 && cy - 1 < destSurface->height) {
          if ((y - 1 >= 0 && ALPHA(srcSurface->rows[y - 1][x]) == 0) || y - 1 < 0) {
            destSurface->rows[cy - 1][cx] = renderPixelSolid(color);
          }
        }

        if (cx + 1 >= 0 && cx + 1 < destSurface->width && cy >= 0 && cy < destSurface->height) {
          if ((x + 1 < srcSurface->width && ALPHA(srcSurface->rows[y][x + 1]) == 0) || x + 1 >= srcSurface->width) {
            destSurface->rows[cy][cx + 1] = renderPixelSolid(color);
          }
        }

        if (cx >= 0 && cx < destSurface->width && cy + 1 >= 0 && cy + 1 < destSurface->height) {
          if ((y + 1 < srcSurface->height && ALPHA(srcSurface->rows[y + 1][x]) == 0) || y + 1 >= srcSurface->height) {
            destSurface->rows[cy + 1][cx] = renderPixelSolid(color);
          }
        }
      }
    }
  }
}

/**
 * Renders a line to a sorface.
 *
 * @param destSurface The Surface to render the line onto.
 * @param x1          The X coordinate of point 1.
 * @param y1          The Y coordinate of point 1.
 * @param x2          The X coordinate of point 2.
 * @param y2          The Y coordinate of point 2.
 * @param color       The color value to render the line with.
 */
EXPORT void renderLine(const Surface* destSurface, int32_t x1, int32_t y1, const int32_t x2, const int32_t y2, const uint32_t color) {
  const int32_t dx = abs(x2 - x1);
  const int32_t dy = abs(y2 - y1);

  int32_t x = x1;
  int32_t y = y1;
  int32_t xInc1 = 0, xInc2 = 0;
  int32_t yInc1 = 0, yInc2 = 0;
  int32_t den = 0, num = 0, numAdd = 0, numPixels = 0, curPixel = 0;

  if (x2 >= x1) {
    xInc1 = 1;
    xInc2 = 1;
  } else {
    xInc1 = -1;
    xInc2 = -1;
  }

  if (y2 >= y1) {
    yInc1 = 1;
    yInc2 = 1;
  } else {
    yInc1 = -1;
    yInc2 = -1;
  }

  // There is at least one x-value for every y-value.
  if (dx >= dy) {
    xInc1 = 0;
    yInc2 = 0;
    den = dx;
    num = dx >> 2;
    numAdd = dy;
    numPixels = dx;

  // There is at least one y-value for every x-value.
  } else {
    xInc2 = 0;
    yInc1 = 0;
    den = dy;
    num = dy >> 2;
    numAdd = dx;
    numPixels = dy;
  }

  for (curPixel = 0; curPixel <= numPixels; curPixel++) {
    if (x >= 0 && y >= 0 && x < destSurface->width && y < destSurface->height) {
      destSurface->rows[y][x] = renderPixelSolid(color);
    }

    // Increase numerator by the top of the fraction.
    num += numAdd;
    if (num >= den) {
      num -= den;
      x += xInc1;
      y += yInc1;
    }

    x += xInc2;
    y += yInc2;
  }
}

/**
 * Renders text to a Surface.
 *
 * @param destSurface The Surface to render the text onto,
 * @param srcFont     The Font to render the text with.
 * @param x           The X coordinate to render the text at.
 * @param y           The Y coordinate to render the text at. This renders from the top of a character, not from
 *                    it's baseline.
 * @param text        The text to render.
 * @param color       The color to render the text with. It's alpha component will be stripped and the Font's alpha
 *                    will be used instead.
 */
EXPORT void renderText(const Surface* destSurface, const Font* srcFont, const int32_t x, const int32_t y, const uint8_t* text, uint32_t color) {
  if (!destSurface || !srcFont || !text) {
    return;
  }
  if (y + srcFont->charHeight < 0 || y > destSurface->height) {
    return;
  }

  int32_t   rx, cx, cy;
  int32_t   dx, dy;
  uint32_t* dest;
  uint32_t  character = 0;

  // Strip alpha from the color, the Font surface's alpha will be used instead.
  color &= 0x00FFFFFF;

  do {

    // Rendering everything above space characters.
    if (*text > 32) {

      // Calculate X coordinate on font surface.
      rx = (*text - 33) * srcFont->charWidth;
      for (cy = 0; cy < srcFont->charHeight; cy++) {
        dy = (y + cy);

        if (dy < 0 || dy >= destSurface->height) {
          continue;
        }

        for (cx = 0; cx < srcFont->charWidth; cx++) {
          dx = x + cx + (character * srcFont->charWidth);

          if (dx < 0 || dx >= destSurface->width) {
            continue;
          }

          dest = destSurface->rows[dy] + dx;
          *dest = renderPixelAlpha(*dest, color | *(srcFont->surface->rows[cy] + cx + rx));
        }
      }
    }

    character++;
    text++;
  } while (*text != 0);
}

/**
 * Renders a box to a Surface.
 *
 * @param destSurface The Surface to render the box onto.
 * @param x           The X coordinate of the box.
 * @param y           The Y coordinate of the box.
 * @param width       The width of the box.
 * @param height      The height of the box.
 * @param color       The color of the box.
 * @param blendOp     The blend operation to render the box with.
 */
EXPORT void renderBox(const Surface* destSurface, int32_t x, int32_t y, int32_t width, int32_t height, const uint32_t color) {
  if (!destSurface) {
    return;
  }

  // Normalize coordinates.
  if (width < 0) {
    width = abs(width);
    x -= width;
  }
  if (height < 0) {
    height = abs(height);
    y -= height;
  }

  // Top and bottom.
  for (int32_t rx = x; rx < x + width + 1; rx++) {
    if (y >= 0 && y < destSurface->height && rx >= 0 && rx < destSurface->width) {
      destSurface->rows[y][rx] = renderPixelSolid(color);
    }

    if ((y + height) >= 0 && (y + height) < destSurface->height && rx >= 0 && rx < destSurface->width) {
      destSurface->rows[y + height][rx] = renderPixelSolid(color);
    }
  }

  // Left and right.
  for (int32_t ry = y + 1; ry < y + height; ry++) {
    if (ry >= 0 && ry < destSurface->height && x >= 0 && x < destSurface->width) {
      destSurface->rows[ry][x] = renderPixelSolid(color);
    }

    if (ry >= 0 && ry < destSurface->height && (x + width) >= 0 && (x + width) < destSurface->width) {
      destSurface->rows[ry][x + width] = renderPixelSolid(color);
    }
  }
}

/**
 * Does a simple blitting operation from one Surface onto another. Any alpha information is simply copied onto
 * the destination Surface.
 *
 * @param destSurface The Surface to blit onto.
 * @param srcSurface  The Surface to blit from.
 * @param x           The X coordinate to blit to.
 * @param y           The Y coordinate to blit to.
 */
EXPORT void renderBlit(const Surface* destSurface, const Surface* srcSurface, int32_t x, int32_t y) {
  if (!destSurface || !srcSurface) {
    return;
  }

  int32_t rW = srcSurface->width;
  int32_t rH = srcSurface->height;
  int32_t xO = 0;
  int32_t yO = 0;

  // Bounds checks.
  if (x < 0) {
    rW = rW + x;
    if (rW <= 0) {
      return;
    }
    xO = -x;
    x = 0;
  }
  if (y < 0) {
    rH = rH + y;
    if (rH <= 0) {
      return;
    }
    yO = -y;
    y = 0;
  }

  if (x + rW > destSurface->width) {
    rW = destSurface->width - x;
    if (rW <= 0) {
      return;
    }
  }
  if (y + rH > destSurface->height) {
    rH = destSurface->height - y;
    if (rH <= 0) {
      return;
    }
  }

  // Copy each row of pixels.
  uint32_t* dest = destSurface->rows[y] + x;
  uint32_t* src = srcSurface->rows[yO] + xO;
  const int32_t len = rW << 2;
  for (int32_t cy = 0; cy < rH; cy++) {
    memcpy(dest, src, len);
    dest += destSurface->width;
    src += srcSurface->width;
  }
}

/**
 * Renders a filled box onto a Surface.
 *
 * @param destSurface The Surface to render the box onto.
 * @param x           The X coordinate of the box.
 * @param y           The Y coordinate of the box.
 * @param width       The width of the box.
 * @param height      The height of the box.
 * @param color       The color of the box.
 * @param blendOp     The blend operation to render the box with.
 */
EXPORT void renderBoxFill(const Surface* destSurface, int32_t x, int32_t y, int32_t width, int32_t height, const uint32_t color, const BlendOp blendOp) {
  if (!destSurface) {
    return;
  }

  // Normalize coordinates.
  if (width < 0) {
    width = abs(width);
    x -= width;
  }
  if (height < 0) {
    height = abs(height);
    y -= height;
  }

  // Bounds check.
  if (x < 0) {
    width = width + x;
    if (width <= 0) {
      return;
    }
    x = 0;
  }
  if (y < 0) {
    height = height + y;
    if (height <= 0) {
      return;
    }
    y = 0;
  }

  if (x + width > destSurface->width) {
    width = destSurface->width - x;
    if (width <= 0) {
      return;
    }
  }
  if (y + height > destSurface->height) {
    height = destSurface->height - y;
    if (height <= 0) {
      return;
    }
  }

  int32_t cx, cy;
  uint32_t *dest;
  uint32_t* destRow = destSurface->rows[y] + x;

  for (cy = 0; cy < height; cy++) {
    dest = destRow;

    switch (blendOp) {
      case BLENDOP_SOLID:
        for (cx = 0; cx < width; cx++) {
          *dest = renderPixelSolid(color);
          dest++;
        }
        destRow += destSurface->width;
        break;

      case BLENDOP_ALPHA:
        for (cx = 0; cx < width; cx++) {
          *dest = renderPixelAlpha(*dest, color);
          dest++;
        }
        destRow += destSurface->width;
        break;

      case BLENDOP_ALPHA50:
        for (cx = 0; cx < width; cx++) {
          *dest = renderPixelAlpha50(*dest, color);
          dest++;
        }
        destRow += destSurface->width;
        break;

      default:
        break;
    }
  }
}

/**
 * Blits one Surface onto another, supporting blend operations.
 *
 * @param destSurface The Surface to blit onto.
 * @param srcSurface  The Surface to blit from.
 * @param x           The X coordinate to blit to.
 * @param y           The Y coordinate to blit to.
 * @param blendOp     The blend operation to blit with.
 */
EXPORT void renderBlitBlend(const Surface* destSurface, const Surface *srcSurface, int32_t x, int32_t y, const BlendOp blendOp) {
  if (!destSurface || !srcSurface) {
    return;
  }

  int32_t xO = 0;
  int32_t rW = srcSurface->width;
  if (x < 0) {
    rW = rW + x;
    if (rW <= 0) {
      return;
    }
    xO = -x;
    x = 0;
  }

  int32_t yO = 0;
  int32_t rH = srcSurface->height;
  if (y < 0) {
    rH = rH + y;
    if (rH <= 0) {
      return;
    }
    yO = -y;
    y = 0;
  }

  if (x + rW > destSurface->width) {
    rW = destSurface->width - x;
    if (rW <= 0) {
      return;
    }
  }
  if (y + rH > destSurface->height) {
    rH = destSurface->height - y;
    if (rH <= 0) {
      return;
    }
  }

  uint32_t* dest;
  uint32_t* src;
  int32_t cx, cy;
  for (cy = 0; cy < rH; cy++) {
    dest = destSurface->rows[y + cy] + x;
    src = srcSurface->rows[yO + cy] + xO;

    switch (blendOp) {
      case BLENDOP_SOLID:
        for (cx = 0; cx < rW; cx++) {
          *dest = renderPixelSolid(*src);
          src++;
          dest++;
        }
        break;

      case BLENDOP_ALPHA:
        for (cx = 0; cx < rW; cx++) {
          *dest = renderPixelAlpha(*dest, *src);
          src++;
          dest++;
        }
        break;

      case BLENDOP_ALPHA50:
        for (cx = 0; cx < rW; cx++) {
          *dest = renderPixelAlpha50(*dest, *src);
          src++;
          dest++;
        }
        break;

      case BLENDOP_ALPHA_SIMPLE:
        for (cx = 0; cx < rW; cx++) {
          *dest = renderPixelAlphaSimple(*dest, *src);
          src++;
          dest++;
        }
        break;

      default:
        break;
    }
  }
}

/**
 * Blits one Surface onto another, supporting blend operations and integer scaling.
 *
 * @param destSurface The Surface to blit onto.
 * @param srcSurface  The Surface to blit from.
 * @param x           The X coordinate to blit to.
 * @param y           The Y coordinate to blit to.
 * @param width       The target width of the surface.
 * @param height      The target height of the surface.
 * @param blendOp     The blend operation to blit with.
 */
EXPORT void renderBlitBlendScale(const Surface* destSurface, const Surface* srcSurface, const int32_t x, const int32_t y, const int32_t width, const int32_t height, const BlendOp blendOp) {
  if (!srcSurface || !destSurface || width < 1 || height < 1) {
    return;
  }

  const int32_t stepx = (srcSurface->width << 16) / width;
  const int32_t stepy = (srcSurface->height << 16) / height;

  int32_t cx, cy;
  int32_t cu, cv;
  uint32_t* dest;

  cv = 0;
  for (cy = y; cy < y + height; cy++) {
    if (cy >= 0 && cy < destSurface->height) {
      cu = 0;

      switch (blendOp) {
        case BLENDOP_SOLID:
          for (cx = x; cx < x + width; cx++) {
            if (cx >= 0 && cx < destSurface->width) {
              dest = destSurface->rows[cy] + cx;
              *dest = renderPixelSolid(srcSurface->rows[cv >> 16][cu >> 16]);
            }

            cu += stepx;
          }
          break;

        case BLENDOP_ALPHA:
          for (cx = x; cx < x + width; cx++) {
            if (cx >= 0 && cx < destSurface->width) {
              dest = destSurface->rows[cy] + cx;
              *dest = renderPixelAlpha(*dest, srcSurface->rows[cv >> 16][cu >> 16]);
            }

            cu += stepx;
          }
          break;

        case BLENDOP_ALPHA50:
          for (cx = x; cx < x + width; cx++) {
            if (cx >= 0 && cx < destSurface->width) {
              dest = destSurface->rows[cy] + cx;
              *dest = renderPixelAlpha50(*dest, srcSurface->rows[cv >> 16][cu >> 16]);
            }

            cu += stepx;
          }
          break;

        case BLENDOP_ALPHA_SIMPLE:
          for (cx = x; cx < x + width; cx++) {
            if (cx >= 0 && cx < destSurface->width) {
              dest = destSurface->rows[cy] + cx;
              *dest = renderPixelAlphaSimple(*dest, srcSurface->rows[cv >> 16][cu >> 16]);
            }

            cu += stepx;
          }
          break;

        default:
          break;
      }
    }

    cv += stepy;
  }
}
