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
#include "presenter.h"

/**
 * Creates a new Presenter.
 *
 * @param  hwnd  A window handle (HWND) that should be the Presenter's target window.
 * @param  scale The scale at which to render.
 *
 * @return       A new Presenter.
 */
EXPORT Presenter* presenterCreate(const HWND hwnd, const unsigned int scale) {
  if (!hwnd || scale < 1) {
    printf("presenterCreate: invalid parameters.\n");
    return NULL;
  }

  Presenter* presenter = calloc(1, sizeof(Presenter));
  if (!presenter) {
    printf("presenterCreate: could not allocate memory.\n");
    return NULL;
  }

  presenter->hwnd = hwnd;
  presenter->scale = scale;

  // Get the target window's device context.
  presenter->htargetdc = GetDC(hwnd);
  if (!presenter->htargetdc) {
    printf("presenterCreate: could not get window device context.\n");
    presenterDestroy(presenter);
    return NULL;
  }

  // Create a device context for the target bitmap.
  presenter->hbitmapdc = CreateCompatibleDC(presenter->htargetdc);
  if (!presenter->hbitmapdc) {
    printf("presenterCreate: could not create a compatible bitmap device context.\n");
    presenterDestroy(presenter);
    return NULL;
  }

  // Create the Presenter's pixel data and device context.
  presenterResize(presenter);

  // Test if the Presenter was resized without errors.
  if (!presenter->hbitmapdc || !presenter->hbitmap || GetCurrentObject(presenter->hbitmapdc, OBJ_BITMAP) != presenter->hbitmap || !presenter->surface) {
    printf("presenterCreate: presenterResize failed.\n");
    presenterDestroy(presenter);
    return NULL;
  }

  return presenter;
}

/**
 * Destroys a Presenter.
 *
 * @param presenter The Presenter to destroy.
 */
EXPORT void presenterDestroy(Presenter* presenter) {
  if (!presenter) {
    return;
  }

  if (presenter->hbitmapdc) {
    SelectObject(presenter->hbitmapdc, 0);
    DeleteDC(presenter->hbitmapdc);
  }

  if (presenter->htargetdc) {
    ReleaseDC(presenter->hwnd, presenter->htargetdc);
  }

  if (presenter->hbitmap) {
    DeleteObject(presenter->hbitmap);
  }

  if (presenter->surface) {
    surfaceDestroy(presenter->surface);
  }

  free(presenter);
}

/**
 * Resizes a Presenter's display area.
 *
 * This function should be called when the target window's szie ahs changed. It will allocate a new Surface and bitmap
 * to render to, based on the current size of the target window. Use presenterSetScale to change the scale.
 *
 * @param presenter The Presenter to resize.
 */
EXPORT void presenterResize(Presenter* presenter) {

  // Delete the old bitmap.
  if (presenter->hbitmapdc) {
    SelectObject(presenter->hbitmapdc, 0);
  }
  if (presenter->hbitmap) {
    DeleteObject(presenter->hbitmap);
  }

  // Get the dimensions of the target window.
  RECT rect;
  GetWindowRect(presenter->hwnd, &rect);
  presenter->width = rect.right - rect.left;
  presenter->height = rect.bottom - rect.top;

  presenter->width += presenter->scale - (presenter->width % presenter->scale);
  presenter->height += presenter->scale - (presenter->height % presenter->scale);

  // Create a new DIB section bitmap and select it into the bitmap device context.
  BITMAPINFO bitmap;
  bitmap.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
  bitmap.bmiHeader.biWidth = presenter->width;
  bitmap.bmiHeader.biHeight = presenter->height;
  bitmap.bmiHeader.biPlanes = 1;
  bitmap.bmiHeader.biBitCount = 32;
  bitmap.bmiHeader.biCompression = 0;
  bitmap.bmiHeader.biSizeImage = presenter->width * presenter->height * 4;
  bitmap.bmiHeader.biXPelsPerMeter = 1;
  bitmap.bmiHeader.biYPelsPerMeter = 1;
  bitmap.bmiHeader.biClrUsed = 0;
  bitmap.bmiHeader.biClrImportant = 0;
  presenter->hbitmap = CreateDIBSection(presenter->hbitmapdc, &bitmap, 0, (void*)(&presenter->data), 0, 0);
  if (!presenter->hbitmap) {
    printf("presenterResize: could not create bitmap.\n");
    return;
  }
  if (!SelectObject(presenter->hbitmapdc, presenter->hbitmap)) {
    printf("presenterResize: could not select bitmap.\n");
    return;
  }

  const unsigned int width = ceil(presenter->width / (double)presenter->scale);
  const unsigned int height = ceil(presenter->height / (double)presenter->scale);

  // Resize an existing target surface.
  if (presenter->surface) {
    if (!surfaceResize(presenter->surface, width, height)) {
      printf("presenterResize: could not resize surface.\n");
      return;
    }

  // Create a new matching target Surface.
  } else {
    presenter->surface = surfaceCreate(width, height);
    if (!presenter->surface) {
      printf("presenterResize: could not create surface.\n");
      return;
    }
  }
}

/**
 * Sets a new scale for a Presenter.
 *
 * The Presenter will be resized as a result.
 *
 * @param presenter The Presenter to set the scale for.
 * @param scale     The new scale. Must be > 0.
 */
EXPORT void presenterSetScale(Presenter* presenter, const unsigned int scale) {
  if (scale < 1) {
    printf("presenterSetScale: invalid scale.\n");
    return;
  }

  presenter->scale = scale;
  presenterResize(presenter);
}

/**
 * Returns the current scale of a presenter.
 *
 * @param presenter The Presenter to get the scale from.
 */
EXPORT unsigned int presenterGetScale(Presenter* presenter) {
  return presenter->scale;
}

/**
 * Returns the target Surface of a Presenter.
 *
 * @param  presenter The Presenter to return the target Surface of.
 *
 * @return           A Presenter's target Surface.
 */
EXPORT Surface* presenterGetSurface(Presenter* presenter) {
  return presenter->surface;
}

/**
 * Render a Presenter's target Surface to it's window.
 *
 * @param presenter The Presenter to render the target Surface of.
 */
EXPORT void presenterPresent(Presenter* presenter) {

  // Use a specific surface scaler function for performance.
  if (presenter->scale == 1) {
    surfaceCopyToBitmap(presenter->surface, presenter->data);
  } else if (presenter->scale == 2) {
    surfaceCopyToBitmapDouble(presenter->surface, presenter->data, presenter->width, presenter->height);
  } else {
    surfaceCopyToBitmapScaled(presenter->surface, presenter->data, presenter->width, presenter->height, presenter->scale);
  }

  BitBlt(presenter->htargetdc, 0, 0, presenter->width, presenter->height, presenter->hbitmapdc, 0, 0, SRCCOPY);
}
