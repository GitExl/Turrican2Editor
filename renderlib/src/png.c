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
#include "png.h"
#include "utils.h"


// Add a new chunk to the chunk list
EXPORT uint32_t pngAddChunk(PNGContext* png, const char* name, const uint32_t size, const uint8_t* data) {
  if (!png) {
    return 0;
  }

  // Add new chunk in list
  PNGChunk* newChunk = calloc(1, sizeof(PNGChunk));
  newChunk->next = png->chunks;
  png->chunks = newChunk;

  // Copy name
  newChunk->name = calloc(1, 5);
  memcpy(newChunk->name, name, 5);

  // Copy size and data
  newChunk->size = size;
  newChunk->data = malloc(size);
  memcpy(newChunk->data, data, size);

  return 1;
}


// Unknown chunk callback, store chunks in context chunk list
int32_t pngUserReadChunk(const png_structp pngPtr, const png_unknown_chunkp chunk) {
  PNGContext* png = png_get_io_ptr(pngPtr);
  if (!png) {
    return 1;
  }

  pngAddChunk(png, (char*)chunk->name, chunk->size, chunk->data);

  return 0;
}


// User data read callback
void pngUserReadData(const png_structp pngPtr, const png_bytep data, const png_size_t length) {
  PNGContext* png = png_get_io_ptr(pngPtr);
  if (!png) {
    return;
  }

  // Check if the read is within bounds
  uint32_t readLength = length;
  if (png->dataOffset + readLength > png->dataSize) {
    readLength = png->dataSize - png->dataOffset;
    if (readLength <= 0) {
      return;
    }
  }

  // Copy requested data into buffer
  memcpy(data, png->data + png->dataOffset, readLength);

  // Increase data pointer
  png->dataOffset += readLength;
}


// User data write callback
void pngUserWriteData(const png_structp pngPtr, const png_bytep data, const png_size_t length) {
  PNGContext* png = png_get_io_ptr(pngPtr);
  if (!png) {
    return;
  }

  png->dataSize += length;
  png->data = realloc(png->data, png->dataSize);
  memcpy(png->data + png->dataOffset, data, length);
  png->dataOffset += length;

  return;
}


// Create a png for saving
EXPORT PNGContext* pngCreate() {
  // Allocate context
  PNGContext* png = calloc(1, sizeof(PNGContext));
  png->pngPtr = png_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
  if (!png->pngPtr) {
    pngClose(png);
    return NULL;
  }

  png->infoPtr = png_create_info_struct(png->pngPtr);
  if (!png->infoPtr) {
    pngClose(png);
    return NULL;
  }

  // Custom write function
  png_set_write_fn(png->pngPtr, NULL, pngUserWriteData, NULL);
  png_init_io(png->pngPtr, (png_FILE_p)png);

  // Custom error handler
  png_set_error_fn(png->pngPtr, NULL, NULL, NULL);

  // This context is for writing
  png->write = 1;

  return png;
}


// Save an image to a png
EXPORT uint32_t pngSave(PNGContext* png, const uint8_t* src, uint8_t* pal, const uint32_t numPal, const uint8_t compressLevel) {
  if (!png) {
    return 0;
  }
  if (!png->write) {
    return 0;
  }
  if (compressLevel < 1 || compressLevel > 9) {
    return 0;
  }

  // Error handling return
  if (setjmp(png_jmpbuf(png->pngPtr))) {
    pngClose(png);
    return 0;
  }

  // png filtering and ZLIB compression
  png_set_filter(png->pngPtr, 0, PNG_ALL_FILTERS);
  png_set_compression_level(png->pngPtr, compressLevel);

  // Set image info
  png_set_IHDR(png->pngPtr, png->infoPtr, png->width, png->height, png->bitDepth, png->colorType,
               PNG_INTERLACE_NONE, PNG_COMPRESSION_TYPE_DEFAULT, PNG_FILTER_TYPE_DEFAULT);

  // Set palette
  if (png->colorType == PNG_COLOR_TYPE_PALETTE && pal) {
    png_set_PLTE(png->pngPtr, png->infoPtr, (void*)pal, numPal);
  }

  // Set transparency info
  if (png->colorType == PNG_COLOR_TYPE_PALETTE || png->colorType == PNG_COLOR_TYPE_GRAY ||
      png->colorType == PNG_COLOR_TYPE_RGB) {
    png_color_16p transValues = calloc(1, sizeof(png_color_16));

    if (png->colorType == PNG_COLOR_TYPE_PALETTE) {
      transValues->index = (uint8_t)png->transColor;
    } else if (png->colorType == PNG_COLOR_TYPE_GRAY) {
      transValues->gray = (uint16_t)png->transColor;
    } else if (png->colorType == PNG_COLOR_TYPE_RGB) {
      transValues->red = RED(png->transColor);
      transValues->green = GREEN(png->transColor);
      transValues->blue = BLUE(png->transColor);
    }

    png_set_tRNS(png->pngPtr, png->infoPtr, png->trans, 256, transValues);
    free(transValues);
  }

  // Pack < 8 bits per pixel
  png_set_packing(png->pngPtr);

  // write header
  png_write_info(png->pngPtr, png->infoPtr);

  // Allocate memory for the row pointers
  png_bytep* rows = (png_bytep*)calloc(png->height, sizeof(png_bytep));

  // Point the row pointers into the destination
  uint32_t stride = png_get_rowbytes(png->pngPtr, png->infoPtr);
  for (uint32_t y = 0; y < png->height; y++) {
    rows[y] = (png_byte*)(src + (y * stride));
  }

  // write image
  png_write_image(png->pngPtr, rows);
  png_write_end(png->pngPtr, NULL);

  free(rows);

  return 1;
}


// Open a png file and read its basic information
EXPORT PNGContext* pngOpen(uint8_t* src, const uint32_t srcLen) {
  if (!src || srcLen == 0) {
    return NULL;
  }

  // Test for png signature
  if (png_sig_cmp((png_bytep)src, 0, 8)) {
    return NULL;
  }

  // Allocate png context and init libpng read structure
  PNGContext* png = calloc(1, sizeof(PNGContext));
  png->pngPtr = png_create_read_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
  if (!png->pngPtr) {
    pngClose(png);
    return NULL;
  }

  // Set custom read function
  png_set_read_fn(png->pngPtr, NULL, pngUserReadData);
  png_init_io(png->pngPtr, (png_FILE_p)png);

  // Set custom error handler
  png_set_error_fn(png->pngPtr, NULL, NULL, NULL);

  // Set unknown chunk callback
  png_set_read_user_chunk_fn(png->pngPtr, NULL, pngUserReadChunk);

  // Set error handling return
  if (setjmp(png_jmpbuf(png->pngPtr))) {
    pngClose(png);
    return NULL;
  }

  // Allocate info
  png->infoPtr = png_create_info_struct(png->pngPtr);
  if (!png->infoPtr) {
    pngClose(png);
    return NULL;
  }

  // Set the new context's data info
  png->data = src;
  png->dataOffset = 0;
  png->dataSize = srcLen;

  // Read png info
  png_read_info(png->pngPtr, png->infoPtr);

  // Update context with information from libpng
  png->width = png_get_image_width(png->pngPtr, png->infoPtr);
  png->height = png_get_image_height(png->pngPtr, png->infoPtr);
  png->bitDepth = png_get_bit_depth(png->pngPtr, png->infoPtr);
  png->colorType = png_get_color_type(png->pngPtr, png->infoPtr);

  // Strip 16 bits per channel images down to 8 bits per channel
  png_set_strip_16(png->pngPtr);
  if (png->bitDepth == 16) {
    png->bitDepth = 8;
  }

  // Expand 1, 2 or 4 bits pixels to 8 bits
  png_set_packing(png->pngPtr);

  // Expand grayscale < 8 bpp to 8 bpp
  if (png->colorType == PNG_COLOR_TYPE_GRAY && png->bitDepth < 8) {
    png_set_expand_gray_1_2_4_to_8(png->pngPtr);
  }

  // Convert RGB to BGR
  if (png->colorType == PNG_COLOR_TYPE_RGB || png->colorType == PNG_COLOR_TYPE_RGB_ALPHA) {
    png_set_bgr(png->pngPtr);
  }

  png_read_update_info(png->pngPtr, png->infoPtr);

  return png;
}


// Read a png file's image and chunk data
EXPORT uint32_t pngRead(PNGContext* png, uint8_t* dest, uint8_t* destPal) {
  if (!png || !dest) {
    return 0;
  }
  if (png->write) {
    return 0;
  }

  // Allocate memory for the image's row pointers
  png_bytep* rows = (png_bytep*)calloc(png->height, sizeof(png_bytep));

  // Point the row pointers to their destinations
  uint32_t stride = png_get_rowbytes(png->pngPtr, png->infoPtr);
  for (uint32_t y = 0; y < png->height; y++) {
    rows[y] = (png_byte*)(dest + (y * stride));
  }

  // Set error handling return
  if (setjmp(png_jmpbuf(png->pngPtr))) {
    pngClose(png);
    return 0;
  }

  // Read and decompress image data
  png_read_image(png->pngPtr, rows);

  // Read palette if any
  png_color* pal;
  int32_t numPalette = 0;
  if (png_get_valid(png->pngPtr, png->infoPtr, PNG_INFO_PLTE) && destPal) {
    png_get_PLTE(png->pngPtr, png->infoPtr, &pal, &numPalette);
    memcpy(destPal, pal, numPalette * 3);
  }

  // Read transparency information
  png_color_16p transValues;
  int32_t numTrans = 0;
  if (png_get_valid(png->pngPtr, png->infoPtr, PNG_INFO_tRNS)) {

    // List of tranparent palette indices
    png_get_tRNS(png->pngPtr, png->infoPtr, (png_bytep*)&png->trans, &numTrans, &transValues);

    // Transparent colors
    if (png->colorType == PNG_COLOR_TYPE_PALETTE) {
      png->transColor = (uint32_t)transValues->index;
    } else if (png->colorType == PNG_COLOR_TYPE_GRAY || png->colorType == PNG_COLOR_TYPE_GRAY_ALPHA) {
      png->transColor = (uint32_t)transValues->gray;
    } else if (png->colorType == PNG_COLOR_TYPE_RGB || png->colorType == PNG_COLOR_TYPE_RGB_ALPHA) {
      png->transColor = RGB(transValues->red, transValues->green, transValues->blue);
    }
  }

  png_read_end(png->pngPtr, NULL);
  free(rows);

  return 1;
}


// Close a png context
EXPORT void pngClose(PNGContext* png) {
  if (!png) {
    return;
  }

  if (png->write) {
    png_destroy_write_struct(&png->pngPtr, &png->infoPtr);
    free(png->data);

    if (png->trans) {
      free(png->trans);
    }
  } else {
    png_destroy_read_struct(&png->pngPtr, &png->infoPtr, NULL);
  }

  // Free up chunks
  PNGChunk* chunk = png->chunks;
  while (chunk) {
    PNGChunk* prevChunk = chunk;
    chunk = chunk->next;
    free(prevChunk->name);
    free(prevChunk->data);
    free(prevChunk);
  }

  free(png);
}
