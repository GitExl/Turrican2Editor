# Copyright (c) 2016, Dennis Meuwissen
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from ctypes import *

from renderlib.dll import dll


__all__ = ['StreamRead', 'Endianness']


streamReadGetSize = dll.streamReadGetSize
streamReadGetSize.argtypes = [c_void_p]
streamReadGetSize.restype = c_uint32

streamReadIsEnd = dll.streamReadIsEnd
streamReadIsEnd.argtypes = [c_void_p]
streamReadIsEnd.restype = c_bool

streamReadGetIndex = dll.streamReadGetIndex
streamReadGetIndex.argtypes = [c_void_p]
streamReadGetIndex.restype = c_uint32

streamReadUInt = dll.streamReadUInt
streamReadUInt.argtypes = [c_void_p]
streamReadUInt.restype = c_uint32

streamReadUShort = dll.streamReadUShort
streamReadUShort.argtypes = [c_void_p]
streamReadUShort.restype = c_uint16

streamReadUByte = dll.streamReadUByte
streamReadUByte.argtypes = [c_void_p]
streamReadUByte.restype = c_uint8

streamReadInt = dll.streamReadInt
streamReadInt.argtypes = [c_void_p]
streamReadInt.restype = c_int32

streamReadShort = dll.streamReadShort
streamReadShort.argtypes = [c_void_p]
streamReadShort.restype = c_int16

streamReadByte = dll.streamReadByte
streamReadByte.argtypes = [c_void_p]
streamReadByte.restype = c_int8

streamReadBytes = dll.streamReadBytes
streamReadBytes.argtypes = [c_void_p, c_uint32, c_void_p]
streamReadBytes.restype = c_bool

streamReadGetEndianness = dll.streamReadGetEndianness
streamReadGetEndianness.argtypes = [c_void_p]
streamReadGetEndianness.restype = c_uint32

streamReadSetEndianness = dll.streamReadSetEndianness
streamReadSetEndianness.argtypes = [c_void_p, c_uint8]
streamReadSetEndianness.restype = None

streamReadDestroy = dll.streamReadDestroy
streamReadDestroy.argtypes = [c_void_p]
streamReadDestroy.restype = None

streamReadCreateFromMemory = dll.streamReadCreateFromMemory
streamReadCreateFromMemory.argtypes = [c_void_p, c_uint32]
streamReadCreateFromMemory.restype = c_void_p

streamReadSeek = dll.streamReadSeek
streamReadSeek.argtypes = [c_void_p, c_uint32]
streamReadSeek.restype = None

streamReadSkip = dll.streamReadSkip
streamReadSkip.argtypes = [c_void_p, c_uint32]
streamReadSkip.restype = None

streamReadCreateFromFile = dll.streamReadCreateFromFile
streamReadCreateFromFile.argtypes = [c_char_p]
streamReadCreateFromFile.restype = c_void_p

streamReadInsert = dll.streamReadInsert
streamReadInsert.argtypes = [c_void_p, c_char_p, c_uint32]
streamReadInsert.restype = None


class Endianness(object):
    LITTLE = 0
    BIG = 1


class StreamRead(object):
    """
    Reads data from a memory stream. Also handles byte endianness.
    """

    def __init__(self, ptr):
        self._stream = ptr

    def __del__(self):
        streamReadDestroy(self._stream)

    @classmethod
    def from_file(cls, filename, endianness=Endianness.LITTLE):
        """
        Creates a new stream from a file.
        :param filename: the filename to read from.
        :param endianness: the endianness of the stream reader.
        :return: a new stream reader.
        """
        ptr = streamReadCreateFromFile(filename.encode())
        if not ptr:
            raise Exception('Could not create a StreamRead object from file "{}".'.format(filename))

        streamReadSetEndianness(ptr, endianness)

        return cls(ptr)

    def read_uint(self):
        """
        :return: a uint value from the stream.
        """
        return streamReadUInt(self._stream)

    def read_ushort(self):
        """
        :return: a ushort value from the stream.
        """
        return streamReadUShort(self._stream)

    def read_ubyte(self):
        """
        :return: a ubyte value from the stream.
        """
        return streamReadUByte(self._stream)

    def read_int(self):
        """
        :return: a int value from the stream.
        """
        return streamReadInt(self._stream)

    def read_short(self):
        """
        :return: a short value from the stream.
        """
        return streamReadShort(self._stream)

    def read_byte(self):
        """
        :return: a byte value from the stream.
        """
        return streamReadByte(self._stream)

    def read_bytes(self, count):
        """
        Reads a number of bytes from this stream.
        :param count: the number of bytes to read.
        :return: a string buffer of bytes.
        """
        byte_buffer = create_string_buffer(count)
        streamReadBytes(self._stream, count, byte_buffer)
        return byte_buffer

    def get_endianness(self):
        """
        :return: the endianness of this stream.
        """
        return streamReadGetEndianness(self._stream)

    def set_endianness(self, endianness):
        """
        Sets the endianness of this stream.
        :param endianness: an Endianness value.
        """
        streamReadSetEndianness(self._stream, endianness)

    def seek(self, offset):
        """
        Seeks to a position in this stream.
        :param offset: the absolute offset to seek to.
        """
        streamReadSeek(self._stream, offset)

    def skip(self, count):
        """
        Skips a number of bytes in this stream.
        :param count: the number of bytes to skip.
        """
        streamReadSkip(self._stream, count)

    def insert(self, filename, offset):
        """
        Inserts the data from a file at a specific offset in this stream.
        The original file is not modified, the insertion only occurs in memory.
        :param filename: the filename of the data to insert.
        :param offset: the offset to insert the data at.
        """
        streamReadInsert(self._stream, filename.encode(), offset)

    @property
    def pointer(self):
        return self._stream

    @property
    def size(self):
        """
        :return: the size of this stream in bytes.
        """
        return streamReadGetSize(self._stream)

    @property
    def is_end(self):
        """
        :return: True if the end of this stream has been reached.
        """
        return streamReadIsEnd(self._stream)

    @property
    def index(self):
        """
        :return: the current reading index in this stream.
        """
        return streamReadGetIndex(self._stream)
