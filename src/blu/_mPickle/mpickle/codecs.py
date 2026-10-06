# -----------------------------------------------------------------------------
# MIT License
#
# Copyright (c) 2025 Mattia Antonini (Fondazione Bruno Kessler) m.antonini@fbk.eu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------
#
# codecs.py - Pure-Python implementation of a few codecs functions.
#


def encode(input_string, encoding):
    def ascii_encoder(input_string):
        return bytes([ord(char) for char in input_string if ord(char) < 128])

    def latin1_encoder(input_string):
        return bytes([ord(char) for char in input_string if ord(char) < 256])

    def utf8_encoder(input_string):
        result = bytearray()
        for char in input_string:
            code_point = ord(char)
            if code_point < 0x80:
                result.append(code_point)
            elif code_point < 0x800:
                result.append(0xC0 | (code_point >> 6))
                result.append(0x80 | (code_point & 0x3F))
            elif code_point < 0x10000:
                result.append(0xE0 | (code_point >> 12))
                result.append(0x80 | ((code_point >> 6) & 0x3F))
                result.append(0x80 | (code_point & 0x3F))
            elif code_point < 0x110000:
                result.append(0xF0 | (code_point >> 18))
                result.append(0x80 | ((code_point >> 12) & 0x3F))
                result.append(0x80 | ((code_point >> 6) & 0x3F))
                result.append(0x80 | (code_point & 0x3F))
            else:
                raise UnicodeEncodeError(
                    "utf-8", char, -1, -1, "Invalid Unicode code point"
                )
        return bytes(result)

    if encoding == "ascii":
        return ascii_encoder(input_string)
    elif encoding == "latin1":
        return latin1_encoder(input_string)
    elif encoding == "utf-8":
        return utf8_encoder(input_string)
    else:
        raise ValueError(f"Unsupported encoding: {encoding}")


def escape_decode(input_bytes):
    # A dictionary to map escape sequences to their actual byte values
    escape_sequences = {
        b"\\n": b"\n",
        b"\\t": b"\t",
        b"\\r": b"\r",
        b"\\\\": b"\\",
        b"\\'": b"'",
        b'\\"': b'"',
        b"\\b": b"\b",
        b"\\f": b"\f",
        b"\\v": b"\v",
        b"\\a": b"\a",
        b"\\0": b"\0",
    }

    decoded_bytes = bytearray()
    i = 0
    while i < len(input_bytes):
        # If current byte is a backslash, it might be an escape sequence
        if input_bytes[i : i + 1] == b"\\":
            # Look ahead to see if it's an escape sequence
            for seq, byte_val in escape_sequences.items():
                if input_bytes[i : i + len(seq)] == seq:
                    decoded_bytes.extend(byte_val)
                    i += len(seq)
                    break
            else:
                # Not a recognized escape sequence, just add the backslash
                decoded_bytes.extend(b"\\")
                i += 1
        else:
            # Normal byte, just append it
            decoded_bytes.extend(input_bytes[i : i + 1])
            i += 1

    return bytes(decoded_bytes), len(decoded_bytes)
