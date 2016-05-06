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

#ifndef H_STREAMREAD
#define H_STREAMREAD

typedef struct {
  uint8_t*   data;
  uint32_t   length;
  uint32_t   index;
  Endianness endianness;
} StreamRead;

StreamRead* streamReadCreate();

EXPORT uint32_t    streamReadGetSize          (const StreamRead* stream);
EXPORT bool        streamReadIsEnd            (const StreamRead* stream);
EXPORT uint32_t    streamReadGetIndex         (const StreamRead* stream);
EXPORT uint32_t    streamReadUInt             (StreamRead* stream);
EXPORT int32_t     streamReadInt              (StreamRead* stream);
EXPORT uint16_t    streamReadUShort           (StreamRead* stream);
EXPORT int16_t     streamReadShort            (StreamRead* stream);
EXPORT uint8_t     streamReadUByte            (StreamRead* stream);
EXPORT int8_t      streamReadByte             (StreamRead* stream);
EXPORT uint8_t     streamReadBytes            (StreamRead* stream, const uint32_t count, uint8_t* data);
EXPORT Endianness  streamReadGetEndianness    (const StreamRead* stream);
EXPORT void        streamReadSetEndianness    (StreamRead* stream, const Endianness endianness);
EXPORT void        streamReadDestroy          (StreamRead* stream);
EXPORT StreamRead* streamReadCreateFromMemory (const uint8_t* data, const uint32_t length);
EXPORT void        streamReadSeek             (StreamRead* stream, const uint32_t index);
EXPORT void        streamReadSkip             (StreamRead* stream, const uint32_t bytes);
EXPORT StreamRead* streamReadCreateFromFile   (const char* fileName);
EXPORT void        streamReadInsert           (StreamRead* stream, const char* fileName, const uint32_t offset);

#endif
