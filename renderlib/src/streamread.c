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
#include "utils.h"
#include "streamread.h"

/**
 * Creates a new, empty StreamRead.
 *
 * StreamRead->data is still NULL when created.
 *
 * @return        A new StreamRead or NULL if one could not be created.
 */
StreamRead* streamReadCreate() {
  StreamRead* stream = calloc(1, sizeof(StreamRead));
  if (!stream) {
    return NULL;
  }

  stream->endianness = ENDIANNESS_NATIVE;

  return stream;
}

/**
 * Returns the size of a StreamRead.
 *
 * @param  stream The StreamRead to return the size of.
 *
 * @return        The size of the StreamRead in bytes or 0 if stream is NULL.
 */
EXPORT uint32_t streamReadGetSize(const StreamRead* stream) {
  if (!stream) {
    return 0;
  }

  return stream->length;
}

/**
 * Returns if a StreamRead has reached it's end.
 *
 * @param  stream The StreamRead to examine.
 *
 * @return        1 if the end was reached, 0 if it was not or if stream is NULL.
 */
EXPORT bool streamReadIsEnd(const StreamRead* stream) {
  if (!stream) {
    return false;
  }

  return (stream->index >= stream->length);
}

/**
 * Returns the current byte index a StreamRead is at.
 *
 * @param  stream The StreamRead to return the current index of.
 *
 * @return        The byte index the StreamRead is currently at or 0 if stream is NULL.
 */
EXPORT uint32_t streamReadGetIndex(const StreamRead* stream) {
  if (!stream) {
    return 0;
  }

  return stream->index;
}

/**
 * Reads a 32 bit integer from a StreamRead.
 *
 * @param  stream The StreamRead to read from.
 *
 * @return        The value that was read or 0 if the stream is NULL or the read would be out of bounds.
 */
EXPORT uint32_t streamReadUInt(StreamRead* stream) {
  if (stream->index + 4 >= stream->length) {
    return 0;
  }

  const uint32_t value = *(uint32_t*)(stream->data + stream->index);
  streamReadSkip(stream, 4);

  if (stream->endianness != ENDIANNESS_NATIVE) {
    return SWAP4(value);
  } else {
    return value;
  }
}

EXPORT int32_t streamReadInt(StreamRead* stream) {
  return (int32_t)streamReadUInt(stream);
}

/**
 * Reads a 16 bit integer from a StreamRead.
 *
 * @param  stream The StreamRead to read from.
 *
 * @return        The value that was read or 0 if the stream is NULL or the read would be out of bounds.
 */
EXPORT uint16_t streamReadUShort(StreamRead* stream) {
  if (stream->index + 2 >= stream->length) {
    return 0;
  }

  const uint16_t value = *(uint16_t*)(stream->data + stream->index);
  streamReadSkip(stream, 2);

  if (stream->endianness != ENDIANNESS_NATIVE) {
    return SWAP2(value);
  } else {
    return value;
  }
}

EXPORT int16_t streamReadShort(StreamRead* stream) {
  return (int16_t)streamReadUShort(stream);
}

/**
 * Reads a byte from a StreamRead.
 *
 * @param  stream The StreamRead to read from.
 *
 * @return        The value that was read or 0 if the stream is NULL or the read would be out of bounds.
 */
EXPORT uint8_t streamReadUByte(StreamRead* stream) {
  if (stream->index + 1 >= stream->length) {
    return 0;
  }

  const uint8_t value = *(stream->data + stream->index);
  streamReadSkip(stream, 1);

  return value;
}

EXPORT int8_t streamReadByte(StreamRead* stream) {
  return (int8_t)streamReadUByte(stream);
}

/**
 * Reads a number of bytes from a StreamRead.
 *
 * @param  stream The StreamRead to read from.
 * @param  count  The number of bytes to read.
 * @param  data   A pointer to where the bytes should be read into.
 *
 * @return        The value that was read or 0 if the stream is NULL or the read would be out of bounds.
 */
EXPORT uint8_t streamReadBytes(StreamRead* stream, const uint32_t count, uint8_t* data) {
  if (stream->index + count >= stream->length) {
    return 0;
  }

  memcpy(data, stream->data + stream->index, count);
  streamReadSkip(stream, count);

  return 1;
}

/**
 * Gets the endianness of a StreamRead.
 *
 * @param  stream The StreamRead to get the endianness from.
 *
 * @return        An Endianness constant.
 */
EXPORT Endianness streamReadGetEndianness(const StreamRead* stream) {
  return stream->endianness;
}

/**
 * Sets the endianness of a StreamRead.
 *
 * @param  stream     The StreamRead to set the endianness on.
 * @param  endianness A Endianness constant that is the new endianness of the StreamRead.
 */
EXPORT void streamReadSetEndianness(StreamRead* stream, const Endianness endianness) {
  stream->endianness = endianness;
}

/**
 * Destroys a StreamRead.
 *
 * @param stream The StreamRead to destroy.
 */
EXPORT void streamReadDestroy(StreamRead* stream) {
  if (!stream) {
    return;
  }

  free(stream->data);
  free(stream);
}

/**
 * Creates a new StreamRead with a buffer taken from memory.
 *
 * The memory is copied into the StreamRead's own buffer.
 *
 * @param  data   The data to read.
 * @param  length The length of the data to read.
 *
 * @return        A new StreamRead or NULL if one could not be created.
 */
EXPORT StreamRead* streamReadCreateFromMemory(const uint8_t* data, const uint32_t length) {
  StreamRead* stream = streamReadCreate();
  if (!stream) {
    return NULL;
  }

  // Copy data into our own buffer.
  stream->length = length;
  stream->data = calloc(1, length);
  if (!stream->data) {
    streamReadDestroy(stream);
    return NULL;
  }
  memcpy(stream->data, data, length);

  return stream;
}

/**
 * Seeks a StreamRead to an index.
 *
 * If the seek index is beyond the stream's end, the new index will be the last byte in the stream.
 *
 * @param stream The StreamRead to seek.
 * @param index  The byte index to seek to.
 */
EXPORT void streamReadSeek(StreamRead* stream, const uint32_t index) {
  stream->index = index;
  if (stream->index >= stream->length) {
    stream->index = stream->length - 1;
  }
}

/**
 * Skips a number of bytes in a StreamRead.
 *
 * @param stream The StreamRead to skip in.
 * @param bytes  The number of bytes to skip.
 */
EXPORT void streamReadSkip(StreamRead* stream, const uint32_t bytes) {
  stream->index += bytes;
  if (stream->index >= stream->length) {
    stream->index = stream->length - 1;
  }
}

/**
 * Creates a new StreamRead from a file.
 *
 * @param  fileName The name of the file to create a StreamRead of.
 *
 * @return          A new StreamRead with the file's contents or NULL if the file could not be opened or read, or the
 *                  StreamRead could not be created.
 */
EXPORT StreamRead* streamReadCreateFromFile(const char* fileName) {
  FILE* fp;
  fopen_s(&fp, fileName, "rb");
  if (!fp) {
    return NULL;
  }

  StreamRead* stream = streamReadCreate();
  if (!stream) {
    fclose(fp);
    return NULL;
  }

  // Get the length of the file.
  fseek(fp, 0, SEEK_END);
  stream->length = ftell(fp);
  fseek(fp, 0, SEEK_SET);

  // Allocate data for the stream.
  stream->data = calloc(1, stream->length);
  if (!stream->data) {
    fclose(fp);
    streamReadDestroy(stream);
    return NULL;
  }

  // Read the file into the stream's buffer.
  if (fread(stream->data, 1, stream->length, fp) == 0) {
    fclose(fp);
    streamReadDestroy(stream);
    return NULL;
  }

  fclose(fp);
  return stream;
}

/**
 * Inserts a file's data at a point in the stream.
 *
 * @param stream   The stream to isnert data into.
 * @param fileName The name of the file to insert the data from.
 * @param offset   The offset at which to insert the data.
 */
EXPORT void streamReadInsert(StreamRead* stream, const char* fileName, const uint32_t offset) {
  if (!stream) {
    return;
  }

  FILE* fp;
  fopen_s(&fp, fileName, "rb");
  if (!fp) {
    return;
  }

  // Get the length of the file.
  fseek(fp, 0, SEEK_END);
  uint32_t length = ftell(fp);
  fseek(fp, 0, SEEK_SET);

  if (offset + length >= stream->length) {
    uint8_t* dataPtr = realloc(stream->data, offset + length);
    if (!dataPtr) {
      fclose(fp);
      return;
    }
    stream->data = dataPtr;
    stream->length = offset + length;
  }

  fread(stream->data + offset, 1, length, fp);
  fclose(fp);
}
