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

#include "surface.h"

typedef struct {
  int x1;
  int y1;
  int x2;
  int y2;
} Rectangle;

// RGB component splitting
#define RED(rgb)   (unsigned char) rgb
#define GREEN(rgb) (unsigned char)(rgb >> 8)
#define BLUE(rgb)  (unsigned char)(rgb >> 16)
#define ALPHA(rgb) (unsigned char)(rgb >> 24)

// RGB creation
#define RGB(r, g, b)     (RGBA)r | (g << 8) | (b << 16)
#define RGBA(r, g, b, a) (RGBA)r | (g << 8) | (b << 16) | (a << 24)
#define BGRA(r, g, b, a) (RGBA)b | (g << 8) | (r << 16) | (a << 24)

// Byte swapping
#define SWAP2(value) (((value) & 0xFF) << 8) | (value >> 8)
#define SWAP4(value) (((value >> 24) & 0xFF) | ((value >> 8) & 0xFF00) | ((value << 8) & 0xFF0000) | ((value << 24) & 0xFF000000))

RGBA EXPORT createBGRA (const unsigned char r, const unsigned char g, const unsigned char b, const unsigned char a);
RGBA EXPORT createRGBA (const unsigned char r, const unsigned char g, const unsigned char b, const unsigned char a);
RGBA EXPORT swapRGBA   (const RGBA color);

#endif
