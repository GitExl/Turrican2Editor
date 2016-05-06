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

#ifndef H_STREAMWRITE
#define H_STREAMWRITE

typedef struct {
  uint8_t*   data;
  uint32_t   length;
  uint32_t   bufferLength;
  uint32_t   index;
  Endianness endianness;
} StreamWrite;

void streamWriteExpand (StreamWrite* stream);
void streamWriteSkip   (StreamWrite* stream, const uint32_t count);

EXPORT Endianness   streamWriteGetEndianness  (const StreamWrite* stream);
EXPORT void         streamWriteSetEndianness  (StreamWrite* stream, const Endianness endianness);
EXPORT void         streamWriteUInt           (StreamWrite* stream, uint32_t value);
EXPORT void         streamWriteInt            (StreamWrite* stream, int32_t value);
EXPORT void         streamWriteUShort         (StreamWrite* stream, uint16_t value);
EXPORT void         streamWriteShort          (StreamWrite* stream, int16_t value);
EXPORT void         streamWriteUByte          (StreamWrite* stream, const uint8_t value);
EXPORT void         streamWriteByte           (StreamWrite* stream, const int8_t value);
EXPORT void         streamWriteBytes          (StreamWrite* stream, const uint8_t* data, const uint32_t length);
EXPORT void         streamWriteSeek           (StreamWrite* stream, const uint32_t address);
EXPORT uint32_t     streamWriteGetSize        (const StreamWrite* stream);
EXPORT uint32_t     streamWriteGetIndex       (const StreamWrite* stream);
EXPORT bool         streamWriteToFile         (const StreamWrite* stream, const char* fileName);
EXPORT StreamWrite* streamWriteCreate         ();
EXPORT void         streamWriteDestroy        (StreamWrite* stream);
EXPORT StreamWrite* streamWriteCreateFromFile (const char* fileName);

#endif
