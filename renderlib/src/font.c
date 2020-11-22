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

/**
 * Returns the character width of a font.
 *
 * @param  font The font to return the character width of.
 *
 * @return      The character width in pixels.
 */
EXPORT unsigned int fontGetCharWidth(const Font* font) {
  return font->charWidth;
}

/**
 * Returns the character height of a font.
 *
 * @param  font The font to return the character height of.
 *
 * @return      The character height in pixels.
 */
EXPORT unsigned int fontGetCharHeight(const Font* font) {
  return font->charHeight;
}

/**
 * Loads a font from an image file.
 *
 * The image is expected to contain 128 characters of a fixed width lined up horizontally.
 *
 * @param  fileName The name of the image file to load the font from.
 *
 * @return          A new Font or NULL if it could not be loaded.
 */
EXPORT Font* fontLoad(const char* fileName) {
  Surface* surface = surfaceReadFromPNG(fileName);
  if (!surface) {
    return NULL;
  }

  Font* font = calloc(1, sizeof(Font));
  if (!font) {
    return NULL;
  }

  font->surface = surface;
  font->charWidth = font->surface->width / 128;
  font->charHeight = font->surface->height;

  return font;
}

/**
 * Destroys and frees a Font.
 *
 * @param  font The Font to destroy.
 */
EXPORT void fontDestroy(Font* font) {
  if (!font) {
    return;
  }

  surfaceDestroy(font->surface);
  free(font);
}
