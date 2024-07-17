#!/usr/bin/env python3

import math

class PES:
  HEADER_SIZE = 6

  def __init__(self, payload = b''):
    self.payload = bytearray(payload)

  def __iadd__(self, payload):
    self.payload += payload
    return self

  def __getitem__(self, item):
    return self.payload[item]

  def __setitem__(self, key, value):
    self.payload[key] = value

  def __len__(self):
    return len(self.payload)

  def packet_start_code_prefix(self):
    return (self.payload[0] << 16) | (self.payload[1] << 8) | self.payload[2]

  def stream_id(self):
    return self.payload[3]

  def has_optional_pes_header(self) -> bool:
    if self.stream_id() in [0b10111100, 0b10111111, 0b11110000, 0b11110001, 0b11110010, 0b11111000, 0b11111111]:
      return False
    elif self.stream_id() in [0b10111110]:
      return False
    else:
      return True

  def has_pts(self) -> bool:
    if self.has_optional_pes_header():
      return (self.payload[PES.HEADER_SIZE + 1] & 0x80) != 0
    else:
      return False

  def has_dts(self) -> bool:
    if self.has_optional_pes_header():
      return (self.payload[PES.HEADER_SIZE + 1] & 0x40) != 0
    else:
      return False

  def PES_packet_length(self):
    return (self.payload[4] << 8) | self.payload[5]

  def pes_header_length(self) -> int | None:
    if self.has_optional_pes_header():
      return (self.payload[PES.HEADER_SIZE + 2])
    else:
      return None

  def pts(self) -> int | None:
    if not self.has_pts(): return None

    pts = 0
    pts <<= 3; pts |= ((self.payload[PES.HEADER_SIZE + 3 + 0] & 0x0E) >> 1)
    pts <<= 8; pts |= ((self.payload[PES.HEADER_SIZE + 3 + 1] & 0xFF) >> 0)
    pts <<= 7; pts |= ((self.payload[PES.HEADER_SIZE + 3 + 2] & 0xFE) >> 1)
    pts <<= 8; pts |= ((self.payload[PES.HEADER_SIZE + 3 + 3] & 0xFF) >> 0)
    pts <<= 7; pts |= ((self.payload[PES.HEADER_SIZE + 3 + 4] & 0xFE) >> 1)
    return pts

  def dts(self) -> int | None:
    if not self.has_dts(): return None

    dts = 0
    if self.has_pts():
      dts <<= 3; dts |= ((self.payload[PES.HEADER_SIZE + 8 + 0] & 0x0E) >> 1)
      dts <<= 8; dts |= ((self.payload[PES.HEADER_SIZE + 8 + 1] & 0xFF) >> 0)
      dts <<= 7; dts |= ((self.payload[PES.HEADER_SIZE + 8 + 2] & 0xFE) >> 1)
      dts <<= 8; dts |= ((self.payload[PES.HEADER_SIZE + 8 + 3] & 0xFF) >> 0)
      dts <<= 7; dts |= ((self.payload[PES.HEADER_SIZE + 8 + 4] & 0xFE) >> 1)
    else:
      dts <<= 3; dts |= ((self.payload[PES.HEADER_SIZE + 3 + 0] & 0x0E) >> 1)
      dts <<= 8; dts |= ((self.payload[PES.HEADER_SIZE + 3 + 1] & 0xFF) >> 0)
      dts <<= 7; dts |= ((self.payload[PES.HEADER_SIZE + 3 + 2] & 0xFE) >> 1)
      dts <<= 8; dts |= ((self.payload[PES.HEADER_SIZE + 3 + 3] & 0xFF) >> 0)
      dts <<= 7; dts |= ((self.payload[PES.HEADER_SIZE + 3 + 4] & 0xFE) >> 1)

    return dts

  def PES_packet_data(self) -> memoryview:
    if self.has_optional_pes_header():
      return self.payload[PES.HEADER_SIZE + 3 + self.payload[PES.HEADER_SIZE + 2]:]
    else:
      return self.payload[PES.HEADER_SIZE:]

  def remains(self):
    if self.PES_packet_length() == 0:
      return math.inf
    else:
      return max(0, (PES.HEADER_SIZE + self.PES_packet_length()) - len(self.payload))

  def fulfilled(self):
    if self.PES_packet_length() == 0:
      return False
    else:
      return len(self.payload) >= PES.HEADER_SIZE + self.PES_packet_length()
