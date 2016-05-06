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

#ifndef H_RENDER
#define H_RENDER

typedef enum {
  BLENDOP_SOLID        = 0,
  BLENDOP_ALPHA50      = 1,
  BLENDOP_ALPHA        = 2,
  BLENDOP_ALPHA_SIMPLE = 3
} BlendOp;

EXPORT void renderOutline        (const Surface* destSurface, const Surface* srcSurface, const int32_t rx, const int32_t ry, const uint32_t color);
EXPORT void renderLine           (const Surface* destSurface, int32_t x1, int32_t y1, const int32_t x2, const int32_t y2, const uint32_t color);
EXPORT void renderText           (const Surface* destSurface, const Font* srcFont, const int32_t x, const int32_t y, const uint8_t* text, uint32_t color);
EXPORT void renderBox            (const Surface* destSurface, int32_t x, int32_t y, int32_t width, int32_t height, const uint32_t color);
EXPORT void renderBlit           (const Surface* destSurface, const Surface* srcSurface, int32_t x, int32_t y);
EXPORT void renderBoxFill        (const Surface* destSurface, int32_t x, int32_t y, int32_t width, int32_t height, const uint32_t color, const BlendOp blendOp);
EXPORT void renderBlitBlend      (const Surface* destSurface, const Surface *srcSurface, int32_t x, int32_t y, const BlendOp blendOp);
EXPORT void renderBlitBlendScale (const Surface* destSurface, const Surface* srcSurface, const int32_t x, const int32_t y, const int32_t width, const int32_t height, const BlendOp blendOp);

#endif
