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

#ifndef H_SURFACE
#define H_SURFACE

typedef uint32_t RGBA;

typedef struct {
  int width;
  int height;
  unsigned int length;
  RGBA* data;
  RGBA** rows;
} Surface;

bool surfaceAllocate           (Surface* surface);
bool surfaceResize             (Surface* surface, const unsigned int width, const unsigned int height);
void surfaceCopyToBitmapDouble (const Surface* srcSurface, uint32_t* ptrBitmapBits, const unsigned int destWidth, const unsigned int destHeight);
void surfaceCopyToBitmap       (const Surface *srcSurface, uint32_t* ptrBitmapBits);
void surfaceCopyToBitmapScaled (const Surface* srcSurface, uint32_t* ptrBitmapBits, const unsigned int destWidth, const unsigned int destHeight, unsigned int scale);

EXPORT Surface* surfaceFlipY              (const Surface* srcSurface);
EXPORT uint32_t surfaceGetWidth           (const Surface* surface);
EXPORT uint32_t surfaceGetHeight          (const Surface* surface);
EXPORT bool     surfaceWriteToPNG         (const Surface* surface, const char* fileName, const unsigned int compressLevel);
EXPORT Surface* surfaceReadFromPNG        (const char* fileName);
EXPORT Surface* surfaceCreate             (const unsigned int width, const unsigned int height);
EXPORT void     surfaceDestroy            (Surface* surface);
EXPORT void     surfaceExtract            (const Surface* srcSurface, const Surface* destSurface, const int x, const int y);
EXPORT void     surfaceFill               (const Surface* destSurface, const RGBA color);
EXPORT void     surfaceClear              (const Surface* surface);
EXPORT Surface* surfaceClone              (const Surface* surface);

#endif
