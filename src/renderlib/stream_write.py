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
from renderlib.utils import Endianness


__all__ = ['StreamWrite']


streamWriteGetSize = dll.streamWriteGetSize
streamWriteGetSize.argtypes = [c_void_p]
streamWriteGetSize.restype = c_uint32

streamWriteGetIndex = dll.streamWriteGetIndex
streamWriteGetIndex.argtypes = [c_void_p]
streamWriteGetIndex.restype = c_uint32

streamWriteUInt = dll.streamWriteUInt
streamWriteUInt.argtypes = [c_void_p, c_uint32]
streamWriteUInt.restype = None

streamWriteUShort = dll.streamWriteUShort
streamWriteUShort.argtypes = [c_void_p, c_uint16]
streamWriteUShort.restype = None

streamWriteUByte = dll.streamWriteUByte
streamWriteUByte.argtypes = [c_void_p, c_uint8]
streamWriteUByte.restype = None

streamWriteInt = dll.streamWriteInt
streamWriteInt.argtypes = [c_void_p, c_int32]
streamWriteInt.restype = None

streamWriteShort = dll.streamWriteShort
streamWriteShort.argtypes = [c_void_p, c_int16]
streamWriteShort.restype = None

streamWriteByte = dll.streamWriteByte
streamWriteByte.argtypes = [c_void_p, c_int8]
streamWriteByte.restype = None

streamWriteBytes = dll.streamWriteBytes
streamWriteBytes.argtypes = [c_void_p, c_void_p, c_uint32]
streamWriteBytes.restype = c_bool

streamWriteGetEndianness = dll.streamWriteGetEndianness
streamWriteGetEndianness.argtypes = [c_void_p]
streamWriteGetEndianness.restype = c_uint32

streamWriteSetEndianness = dll.streamWriteSetEndianness
streamWriteSetEndianness.argtypes = [c_void_p, c_uint8]
streamWriteSetEndianness.restype = None

streamWriteDestroy = dll.streamWriteDestroy
streamWriteDestroy.argtypes = [c_void_p]
streamWriteDestroy.restype = None

streamWriteSeek = dll.streamWriteSeek
streamWriteSeek.argtypes = [c_void_p, c_uint32]
streamWriteSeek.restype = None

streamWriteToFile = dll.streamWriteToFile
streamWriteToFile.argtypes = [c_void_p, c_char_p]
streamWriteToFile.restype = c_bool

streamWriteCreateFromFile = dll.streamWriteCreateFromFile
streamWriteCreateFromFile.argtypes = [c_char_p]
streamWriteCreateFromFile.restype = c_void_p

streamWriteCreate = dll.streamWriteCreate
streamWriteCreate.argtypes = None
streamWriteCreate.restype = c_void_p


class StreamWrite:

    def __init__(self, ptr: int):
        self._stream: int = ptr

    def __del__(self):
        streamWriteDestroy(self._stream)

    @classmethod
    def empty(cls, endianness: Endianness = Endianness.LITTLE):
        ptr = streamWriteCreate()
        if not ptr:
            raise Exception('Could not create a StreamWrite object.')

        streamWriteSetEndianness(ptr, endianness)

        return cls(ptr)

    @classmethod
    def from_file(cls, filename: str, endianness: Endianness = Endianness.LITTLE):
        ptr = streamWriteCreateFromFile(filename.encode())
        if not ptr:
            raise Exception('Could not create a StreamWrite object from file "{}".'.format(filename))

        streamWriteSetEndianness(ptr, endianness)

        return cls(ptr)

    def write_to_file(self, filename: str):
        if not streamWriteToFile(self._stream, filename.encode()):
            raise Exception('Could not write StreamWrite object to file "{}".'.format(filename))

    def write_uint(self, data: int):
        streamWriteUInt(self._stream, data)

    def write_ushort(self, data: int):
        streamWriteUShort(self._stream, data)

    def write_ubyte(self, data: int):
        streamWriteUByte(self._stream, data)

    def write_int(self, data: int):
        streamWriteInt(self._stream, data)

    def write_short(self, data: int):
        streamWriteShort(self._stream, data)

    def write_byte(self, data: int):
        streamWriteByte(self._stream, data)

    def write_bytes(self, data: bytes):
        count = len(data)
        byte_buffer = create_string_buffer(count)
        streamWriteBytes(self._stream, byte_buffer, count)

    def get_endianness(self) -> Endianness:
        return streamWriteGetEndianness(self._stream)

    def set_endianness(self, endianness: Endianness):
        streamWriteSetEndianness(self._stream, endianness)

    def seek(self, offset: int):
        streamWriteSeek(self._stream, offset)

    @property
    def pointer(self) -> int:
        return self._stream

    @property
    def size(self) -> int:
        return streamWriteGetSize(self._stream)

    @property
    def index(self) -> int:
        return streamWriteGetIndex(self._stream)
