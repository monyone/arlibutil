from collections.abc import Buffer

class ByteStream:
  def __init__(self, data: Buffer):
    self.data = memoryview(data)
    self.current = 0

  def __len__(self):
    return max(0, len(self.data) - self.current)

  def __bool__(self):
    return len(self) > 0

  def read(self, size: int):
    if self.current + size > len(self.data):
      raise EOFError
    view = self.data[self.current: self.current + size]
    self.current = min(len(self.data), self.current + size)
    return view

  def readU8(self):
    if self.current + 1 > len(self.data):
      raise EOFError
    view = int.from_bytes(self.data[self.current: self.current + 1], byteorder='big')
    self.current = min(len(self.data), self.current + 1)
    return view

  def readU16(self):
    if self.current + 2 > len(self.data):
      raise EOFError
    view = int.from_bytes(self.data[self.current: self.current + 2], byteorder='big')
    self.current = min(len(self.data), self.current + 2)
    return view

  def readU24(self):
    if self.current + 3 > len(self.data):
      raise EOFError
    view = int.from_bytes(self.data[self.current: self.current + 3], byteorder='big')
    self.current = min(len(self.data), self.current + 3)
    return view

  def readU32(self):
    if self.current + 4 > len(self.data):
      raise EOFError
    view = int.from_bytes(self.data[self.current: self.current + 4], byteorder='big')
    self.current = min(len(self.data), self.current + 4)
    return view

  def readU64(self):
    if self.current + 8 > len(self.data):
      raise EOFError
    view = int.from_bytes(self.data[self.current: self.current + 8], byteorder='big')
    self.current = min(len(self.data), self.current + 8)
    return view

  def readS8(self):
    if self.current + 1 > len(self.data):
      raise EOFError
    view = int.from_bytes(self.data[self.current: self.current + 1], byteorder='big', signed=True)
    self.current = min(len(self.data), self.current + 1)
    return view

  def readS16(self):
    if self.current + 2 > len(self.data):
      raise EOFError
    view = int.from_bytes(self.data[self.current: self.current + 2], byteorder='big', signed=True)
    self.current = min(len(self.data), self.current + 2)
    return view

  def readS24(self):
    if self.current + 3 > len(self.data):
      raise EOFError
    view = int.from_bytes(self.data[self.current: self.current + 3], byteorder='big', signed=True)
    self.current = min(len(self.data), self.current + 3)
    return view

  def readS32(self):
    if self.current + 4 > len(self.data):
      raise EOFError
    view = int.from_bytes(self.data[self.current: self.current + 4], byteorder='big', signed=True)
    self.current = min(len(self.data), self.current + 4)
    return view

  def readS64(self):
    if self.current + 8 > len(self.data):
      raise EOFError
    view = int.from_bytes(self.data[self.current: self.current + 8], byteorder='big', signed=True)
    self.current = min(len(self.data), self.current + 8)
    return view

  def readAll(self):
    view = self.data[self.current: len(self.data)]
    self.current = len(self.data)
    return view
