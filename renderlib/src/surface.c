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
#include "png.h"
#include "utils.h"

bool surfaceAllocate(Surface* surface) {
  surface->length = surface->width * surface->height * sizeof(uint32_t);

  if (!surface->data) {
    surface->data = calloc(1, surface->length);
  } else {
    surface->data = realloc(surface->data, surface->length);
  }
  if (!surface->data) {
    return false;
  }

  if (!surface->rows) {
    surface->rows = calloc(1, surface->height * sizeof(uint32_t));
  } else {
    surface->rows = realloc(surface->rows, surface->height * sizeof(uint32_t));
  }
  if (!surface->rows) {
    return false;
  }

  // Assign row pointers
  for (int32_t row = 0; row < surface->height; row++) {
    surface->rows[row] = (surface->data + row * surface->width);
  }

  return true;
}

bool surfaceResize(Surface* surface, const uint32_t width, const uint32_t height) {
  surface->width = width;
  surface->height = height;

  return surfaceAllocate(surface);
}

// Copy a surface to a regular DIB, doubling each pixel
void surfaceCopyToBitmapDouble(const Surface* srcSurface, uint32_t* ptrBitmapBits, const uint32_t destWidth, const uint32_t destHeight) {
  if (!srcSurface || !ptrBitmapBits) {
    return;
  }

  uint32_t cx, cy;
  uint32_t* src;
  uint32_t* dest = ptrBitmapBits;

  cy = destHeight >> 1;
  while (cy--) {
    src = srcSurface->rows[cy];
    cx = destWidth >> 1;
    while (cx--) {
      *dest++ = *src;
      *dest++ = *src;
      src++;
    }

    src = srcSurface->rows[cy];
    cx = destWidth >> 1;
    while (cx--) {
      *dest++ = *src;
      *dest++ = *src;
      src++;
    }
  }
}

// Copy a surface to a regular DIB
void surfaceCopyToBitmap(const Surface *srcSurface, uint32_t *ptrBitmapBits) {
  if (!srcSurface || !ptrBitmapBits) {
    return;
  }

  const int32_t len = srcSurface->width << 2;
  uint32_t* src = srcSurface->rows[srcSurface->height - 1];
  uint32_t* dest = ptrBitmapBits;

  for (int32_t y = 0; y < srcSurface->height; y++) {
    memcpy(dest, src, len);
    src -= srcSurface->width;
    dest += srcSurface->width;
  }
}

// Copy a surface to an SDL surface, scaling each pixel
void surfaceCopyToBitmapScaled(const Surface* srcSurface, uint32_t *ptrBitmapBits, const uint32_t destWidth, const uint32_t destHeight, const uint32_t scale) {
  if (!srcSurface || !ptrBitmapBits) {
    return;
  }

  uint32_t cx, cy;
  float cu, cv;
  uint32_t* dest;

  const float factor = 1.0 / scale;
  uint32_t* destRow = ptrBitmapBits + (destHeight * destWidth) - destWidth;

  cv = 0;
  cy = destHeight - 1;
  while (cy--) {
    cu = 0;
    dest = destRow;

    cx = destWidth - 1;
    while (cx--) {
      *dest++ = srcSurface->rows[(uint32_t)cv][(uint32_t)cu];
      cu += factor;
    }

    cv += factor;
    destRow -= destWidth;
  }
}

// Flip surface vertically
EXPORT Surface* surfaceFlipY(const Surface* srcSurface) {
  if (!srcSurface) {
    return NULL;
  }

  Surface* destSurface = surfaceCreate(srcSurface->width, srcSurface->height);
  if (!destSurface) {
    return NULL;
  }

  uint32_t* dest = destSurface->data;
  uint32_t* src = srcSurface->rows[srcSurface->height - 1];
  const uint32_t len = srcSurface->width << 2;
  for (int32_t y = 0; y < srcSurface->height; y++) {
    memcpy(dest, src, len);
    dest += destSurface->width;
    src -= srcSurface->width;
  }

  return destSurface;
}

// Return a surface's properties
EXPORT uint32_t surfaceGetWidth(const Surface* surface) {
  return surface->width;
}

EXPORT uint32_t surfaceGetHeight(const Surface* surface) {
  return surface->height;
}

// Write a surface to a PNG file
EXPORT bool surfaceWriteToPNG(const Surface* surface, const char* fileName, const uint8_t compressLevel) {
  if (!surface) {
    return false;
  }
  if (compressLevel < 1 || compressLevel > 9) {
    return false;
  }

  PNGContext* png = pngCreate();
  if (!png) {
    return false;
  }

  png->width = surface->width;
  png->height = surface->height;
  png->colorType = PNG_COLOR_TYPE_RGB_ALPHA;
  png->bitDepth = 8;

  // Convert image data to RGBA
  uint32_t* imageData = calloc(1, png->width * png->height * sizeof(uint32_t));
  if (!imageData) {
    pngClose(png);
    return false;
  }

  int32_t x, y;
  uint32_t src;
  for (y = 0; y < surface->height; y++) {
    for (x = 0; x < surface->width; x++) {
      src = *(surface->rows[y] + x);
      src = BGRA(RED(src), GREEN(src), BLUE(src), ALPHA(src));
      imageData[x + y * png->width] = src;
    }
  }

  pngSave(png, (uint8_t*)imageData, NULL, 0, compressLevel);

  FILE* fp = fopen(fileName, "wb");
  if (!fp) {
    free(imageData);
    pngClose(png);
    return false;
  }

  if (fwrite(png->data, 1, png->dataSize, fp) == 0) {
    free(imageData);
    fclose(fp);
    pngClose(png);
    return false;
  }

  free(imageData);
  fclose(fp);
  pngClose(png);

  return true;
}

// Load a surface from a PNG file
EXPORT Surface* surfaceReadFromPNG(const char* fileName) {
  FILE* fp = fopen(fileName, "rb");
  fseek(fp, 0, SEEK_END);
  const uint32_t length = ftell(fp);
  fseek(fp, 0, SEEK_SET);

  void* data = calloc(1, length);
  if (fread(data, 1, length, fp) == 0) {
    free(data);
    fclose(fp);
    return NULL;
  }

  // Read PNG
  PNGContext* png = pngOpen(data, length);
  fclose(fp);
  if (!png) {
    return NULL;
  }

  // Only 8 bits per channel is supported
  if (png->bitDepth != 8) {
    pngClose(png);
    return NULL;
  }

  // Create new surface
  Surface* surface = surfaceCreate(png->width, png->height);
  if (!surface) {
    pngClose(png);
    return NULL;
  }

  // Greyscale becomes an alpha channel
  if (png->bitDepth == 8 && png->colorType == PNG_COLOR_TYPE_GRAY) {
    uint8_t* imageData = calloc(1, png->width * png->height);
    if (!imageData) {
      pngClose(png);
      return NULL;
    }
    pngRead(png, imageData, NULL);

    int32_t x, y;
    for (y = 0; y < surface->height; y++) {
      for (x = 0; x < surface->width; x++) {
        surface->rows[y][x] = *(uint8_t*)(imageData + x + y * surface->width) << 24;
      }
    }

    free(imageData);

  // RGB, add alpha
  } else if (png->bitDepth == 8 && png->colorType == PNG_COLOR_TYPE_RGB) {
    uint8_t* imageData = calloc(1, png->width * png->height * 3);
    if (!imageData) {
      pngClose(png);
      return NULL;
    }
    pngRead(png, imageData, NULL);

    uint32_t col;
    int32_t x, y;
    for (y = 0; y < surface->height; y++) {
      for (x = 0; x < surface->width; x++) {
        col = *(uint32_t*)(imageData + (x + y * surface->width) * 3);
        surface->rows[y][x] = createRGBA(RED(col), GREEN(col), BLUE(col), 0xFF);
      }
    }

    free(imageData);

  // RGBA
  } else if (png->bitDepth == 8 && png->colorType == PNG_COLOR_TYPE_RGB_ALPHA) {
    pngRead(png, (uint8_t*)surface->data, NULL);

  // Unsupported format
  } else {
    pngClose(png);
    surfaceDestroy(surface);
    return NULL;
  }

  pngClose(png);
  free(data);
  return surface;
}

// Allocate a new, empty surface
EXPORT Surface* surfaceCreate(const uint32_t width, const uint32_t height) {
  Surface* surface = calloc(1, sizeof(Surface));
  if (!surface) {
    return NULL;
  }

  surface->width = width;
  surface->height = height;

  if (!surfaceAllocate(surface)) {
    surfaceDestroy(surface);
    return NULL;
  }

  return surface;
}

// Destroy a surface
EXPORT void surfaceDestroy(Surface* surface) {
  if (!surface) {
    return;
  }

  free(surface->rows);
  free(surface->data);
  free(surface);
}

// Extract a portion of a surface onto another
EXPORT void surfaceExtract(const Surface* srcSurface, const Surface* destSurface, const int32_t x, const int32_t y) {
  if (!srcSurface || !destSurface) {
    return;
  }

  const int32_t len = destSurface->width << 2;
  uint32_t* src = srcSurface->rows[y] + x;
  uint32_t* dest = destSurface->data;

  for (int32_t row = 0; row < destSurface->height; row++) {
    memcpy(dest, src, len);
    src += srcSurface->width;
    dest += destSurface->width;
  }
}

// Fill this surface with a single color
EXPORT void surfaceFill(const Surface* destSurface, const uint32_t color) {
  if (!destSurface) {
    return;
  }

  for (int32_t pixel = 0; pixel < destSurface->width * destSurface->height; pixel++) {
    *(destSurface->data + pixel) = color;
  }
}

// Clear a surface
EXPORT void surfaceClear(const Surface* surface) {
  if (!surface) {
    return;
  }
  memset(surface->data, 0, surface->length);
}

EXPORT Surface* surfaceClone(const Surface* surface) {
  Surface* newSurface = surfaceCreate(surface->width, surface->height);
  if (!newSurface) {
    return NULL;
  }

  memcpy(newSurface->data, surface->data, surface->length);

  return newSurface;
}

EXPORT Rectangle surfaceUsedRect(const Surface* surface) {
  Rectangle rect = {surface->width, surface->height, 0, 0};

  for (int32_t y = 0; y < surface->height; y++) {
    for (int32_t x = 0; x < surface->width; x++) {
      uint32_t pixel = surface->data[x + y * surface->width];
      if (ALPHA(pixel)) {
        rect.x1 = x < rect.x1 ? x : rect.x1;
        break;
      }
    }

    for (int32_t x = surface->width - 1; x >= 0; x--) {
      uint32_t pixel = surface->data[x + y * surface->width];
      if (ALPHA(pixel)) {
        rect.x2 = x > rect.x2 ? x : rect.x2;
        break;
      }
    }
  }

  for (int32_t x = 0; x < surface->width; x++) {
    for (int32_t y = 0; y < surface->height; y++) {
      uint32_t pixel = surface->data[x + y * surface->width];
      if (ALPHA(pixel)) {
        rect.y1 = y < rect.y1 ? y : rect.y1;
        break;
      }
    }

    for (int32_t y = surface->height - 1; y >= 0; y--) {
      uint32_t pixel = surface->data[x + y * surface->width];
      if (ALPHA(pixel)) {
        rect.y2 = y > rect.y2 ? y : rect.y2;
        break;
      }
    }
  }

  return rect;
}
