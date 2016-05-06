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

#ifndef H_PNG
#define H_PNG

#include <png.h>

typedef struct {
  char*    name;
  uint32_t size;
  uint8_t* data;
  void*    next;
} PNGChunk;

typedef struct {
  // libpng pointers
  png_structp pngPtr;
  png_infop infoPtr;

  // Opened for writing
  uint8_t write;

  // Basic info
  uint32_t width;
  uint32_t height;
  uint32_t bitDepth;
  uint32_t colorType;

  // Array of transparent colors
  uint8_t* trans;
  uint32_t transColor;

  // Data containing the PNG file
  uint8_t* data;
  uint32_t dataOffset;
  uint32_t dataSize;

  // Linked list of chunks
  PNGChunk* chunks;
} PNGContext;

EXPORT void        pngClose    (PNGContext* ctx);
EXPORT PNGContext* pngOpen(uint8_t* src, const uint32_t srcLen);
EXPORT PNGContext* pngCreate();
EXPORT uint32_t    pngAddChunk(PNGContext* png, const char* name, const uint32_t size, const uint8_t* data);
EXPORT uint32_t    pngRead(PNGContext* ctx, uint8_t* dest, uint8_t* destPal);
EXPORT uint32_t    pngSave(PNGContext* png, const uint8_t* src, uint8_t* pal, const uint32_t numPal, const uint8_t compressLevel);

#endif
