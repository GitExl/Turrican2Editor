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

#ifndef H_UTILS
#define H_UTILS

typedef struct {
  int32_t x1;
  int32_t y1;
  int32_t x2;
  int32_t y2;
} Rectangle;

// RGB component splitting
#define RED(rgb)   (uint8_t) rgb
#define GREEN(rgb) (uint8_t)(rgb >> 8)
#define BLUE(rgb)  (uint8_t)(rgb >> 16)
#define ALPHA(rgb) (uint8_t)(rgb >> 24)

// RGB creation
#define RGB(r, g, b)     (uint32_t)r | (g << 8) | (b << 16)
#define RGBA(r, g, b, a) (uint32_t)r | (g << 8) | (b << 16) | (a << 24)
#define BGRA(r, g, b, a) (uint32_t)b | (g << 8) | (r << 16) | (a << 24)

// Byte swapping
#define SWAP2(value) (((value) & 0xFF) << 8) | (value >> 8)
#define SWAP4(value) (((value >> 24) & 0xFF) | ((value >> 8) & 0xFF00) | ((value << 8) & 0xFF0000) | ((value << 24) & 0xFF000000))

uint32_t EXPORT createBGRA (const uint8_t r, const uint8_t g, const uint8_t b, const uint8_t a);
uint32_t EXPORT createRGBA (const uint8_t r, const uint8_t g, const uint8_t b, const uint8_t a);
uint32_t EXPORT swapRGBA   (const uint32_t color);

#endif
