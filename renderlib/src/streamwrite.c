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
#include "streamwrite.h"

/**
 * Skips a number of bytes in a StreamWrite.
 *
 * @param stream The StreamWrite to skip in.
 * @param count  The number of bytes to skip.
 */
void streamWriteSkip(StreamWrite* stream, const uint32_t count) {
  stream->index += count;

  // Increase the stream's data size if needed.
  if (stream->index >= stream->length) {
    stream->length = stream->index + 1;
    if (stream->length >= stream->bufferLength) {
      streamWriteExpand(stream);
    }
  }
}

/**
 * Expands a StreamWrite's buffer size to fit new data.
 *
 * The buffer is reallocated to twice it's current size.
 *
 * @param stream The StreamWrite to expand the buffer size of.
 */
void streamWriteExpand(StreamWrite* stream) {
  uint32_t newLength = stream->bufferLength * 2;
  uint8_t* newPointer = realloc(stream->data, newLength);
  if (!newPointer) {
    return;
  }

  stream->data = newPointer;
  stream->bufferLength = newLength;

  // Zero the newly allocated part.
  memset(stream->data + stream->bufferLength, 0, newLength - stream->bufferLength);
}

/**
 * Gets the endianness of a StreamWrite.
 *
 * @param  stream The StreamWrite to get the endianness from.
 *
 * @return        An Endianness constant.
 */
EXPORT Endianness streamWriteGetEndianness(const StreamWrite* stream) {
	return stream->endianness;
}

/**
 * Sets the endianness of a StreamWrite.
 *
 * @param  stream     The StreamWrite to set the endianness on.
 * @param  endianness A Endianness constant that is the new endianness of the StreamWrite.
 */
EXPORT void streamWriteSetEndianness(StreamWrite* stream, const Endianness endianness) {
	stream->endianness = endianness;
}

/**
 * Writes a 32 bit integer to a StreamWrite.
 *
 * @param stream The StreamWrite to write to.
 * @param value  The value to write.
 */
EXPORT void streamWriteUInt(StreamWrite* stream, uint32_t value) {
  if (!stream) {
    return;
  }

  if (stream->index + 4 >= stream->bufferLength) {
    streamWriteExpand(stream);
  }

	if (stream->endianness != ENDIANNESS_NATIVE) {
    value = SWAP4(value);
  }
  *(uint32_t*)(stream->data + stream->index) = value;
  streamWriteSkip(stream, 4);
}

EXPORT void streamWriteInt(StreamWrite* stream, int32_t value) {
  streamWriteUInt(stream, (uint32_t)value);
}

/**
 * Writes a 16 bit integer to a StreamWrite.
 *
 * @param stream The StreamWrite to write to.
 * @param value  The value to write.
 */
EXPORT void streamWriteUShort(StreamWrite* stream, uint16_t value) {
  if (!stream) {
    return;
  }

  if (stream->index + 2 >= stream->bufferLength) {
    streamWriteExpand(stream);
  }

  if (stream->endianness != ENDIANNESS_NATIVE) {
    value = SWAP2(value);
  }
	*(uint32_t*)(stream->data + stream->index) = value;
  streamWriteSkip(stream, 2);
}

EXPORT void streamWriteShort(StreamWrite* stream, int16_t value) {
  streamWriteUShort(stream, (uint16_t)value);
}

/**
 * Writes a byte to a StreamWrite.
 *
 * @param stream The StreamWrite to write to.
 * @param value  The value to write.
 */
EXPORT void streamWriteUByte(StreamWrite* stream, const uint8_t value) {
  if (!stream) {
    return;
  }

  if (stream->index >= stream->bufferLength) {
    streamWriteExpand(stream);
  }

  *(uint8_t*)(stream->data + stream->index) = value;
  streamWriteSkip(stream, 1);
}

EXPORT void streamWriteByte(StreamWrite* stream, int8_t value) {
  streamWriteUByte(stream, (uint8_t)value);
}

/**
 * Writes a number of bytes to a StreamWrite.
 *
 * @param stream The StreamWrite to write to.
 * @param data   The data to write.
 * @param length The length of the data to write.
 */
EXPORT void streamWriteBytes(StreamWrite* stream, const uint8_t* data, const uint32_t length) {
  if (!stream) {
    return;
  }

  if (stream->index + length >= stream->bufferLength) {
    streamWriteExpand(stream);
  }

  memcpy(stream->data + stream->index, data, length);
  streamWriteSkip(stream, length);
}

/**
 * Seeks to a byte index in a StreamWrite.
 *
 * @param stream The StreamWrite to seek in.
 * @param index  The new byte index to seek to.
 */
EXPORT void streamWriteSeek(StreamWrite* stream, const uint32_t index) {
  if (!stream) {
    return;
  }
  if (index >= stream->length) {
    return;
  }

  stream->index = index;
}

/**
 * Returns the current size of a StreamWrite.
 *
 * @param  stream The StreamWrite to return the size of.
 *
 * @return        The size of the StreamWrite or 0 if stream is NULL.
 */
EXPORT uint32_t streamWriteGetSize(const StreamWrite* stream) {
  if (!stream) {
    return 0;
  }
  return stream->length;
}

/**
 * Returns the current byte index of a StreamWrite.
 *
 * @param  stream The StreamWrite to return the index of.
 *
 * @return        The current byte index or 0 if stream is NULL.
 */
EXPORT uint32_t streamWriteGetIndex(const StreamWrite* stream) {
  if (!stream) {
  	return 0;
  }
  return stream->index;
}

/**
 * Writes a StreamWrite to a file.
 *
 * @param  stream   The StreamWrite to write.
 * @param  fileName The name of the file to write to.
 *
 * @return          true if the write was successful, false if not.
 */
EXPORT bool streamWriteToFile(const StreamWrite* stream, const char* fileName) {
  if (!stream) {
    return false;
  }

  FILE* fp = fopen(fileName, "wb");
  if (!fp) {
    return false;
  }

	if (fwrite(stream->data, 1, stream->length, fp) == 0) {
		fclose(fp);
		return false;
	}

	fclose(fp);
  return true;
}

/**
 * Creates a new StreamWrite.
 *
 * @return A new empty StreamWrite or NULL if it could not be created.
 */
EXPORT StreamWrite* streamWriteCreate() {
  StreamWrite* stream = calloc(1, sizeof(StreamWrite));
  if (!stream) {
    return NULL;
  }

	stream->endianness = ENDIANNESS_NATIVE;

  return stream;
}

/**
 * Destroys a StreamWrite.
 *
 * @param stream The StreamWrite to destroy.
 */
EXPORT void streamWriteDestroy(StreamWrite* stream) {
	if (!stream) {
		return;
  }

	free(stream->data);
	free(stream);
}

/**
 * Creates a new StreamWrite from a file's contents.
 *
 * @param  fileName The filename to read the contents from.
 *
 * @return          A new StreamWrite with the contents of the file, set to index 0.
 */
EXPORT StreamWrite* streamWriteCreateFromFile(const char* fileName) {
  StreamWrite* stream = streamWriteCreate();
  if (!stream) {
    return NULL;
  }

  FILE* fp = fopen(fileName, "rb");
  if (!fp) {
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
    streamWriteDestroy(stream);
    return NULL;
  }

  // Read the file into the stream's buffer.
  if (fread(stream->data, 1, stream->length, fp) == 0) {
    fclose(fp);
    streamWriteDestroy(stream);
    return NULL;
  }

  fclose(fp);

  stream->endianness = ENDIANNESS_NATIVE;
  stream->bufferLength = stream->length;

  return stream;
}
