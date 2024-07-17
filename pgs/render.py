from collections.abc import Buffer
from enum import Enum

from PIL import Image

from pgs.bytestream import ByteStream

class NotImplementedYetError(Exception):
  pass

class CompositionObject:
  def __init__(self, stream: ByteStream):
    self.objectId = stream.readU16()
    self.windowId = stream.readU8()
    self.objectCroppedFlag = stream.readU8() != 0x00
    self.objectHorizontalPosition = stream.readU16()
    self.objectVerticalPosition = stream.readU16()
    if self.objectCroppedFlag:
      self.objectCroppingHorizontalPosition = stream.readU16()
      self.objectCroppingVerticalPosition = stream.readU16()
      self.objectCroppingWidth = stream.readU16()
      self.objectCroppingHeight = stream.readU16()
    else:
      self.objectCroppingHorizontalPosition = None
      self.objectCroppingVerticalPosition = None
      self.objectCroppingWidth = None
      self.objectCroppingHeight = None

class CompsitionState(Enum):
  Normal = 0x00
  AcquisitionPoint = 0x40
  EpochStart = 0x80

class PresentationCompositionSegment:
  def __init__(self, stream: ByteStream):
    self.width = stream.readU16()
    self.height = stream.readU16()
    self.frameRate = stream.readU8()
    self.compositionNumber = stream.readU16()
    self.compositionState = stream.readU8()
    self.paletteUpdateFlag = stream.readU8() == 0x80
    self.paletteId = stream.readU8()
    self.numberOfCompositionObject = stream.readU8()
    self.compositionObjects = [CompositionObject(stream) for _ in range(self.numberOfCompositionObject)]

class WindowDefinition:
  def __init__(self, stream: ByteStream):
    self.windowId = stream.readU8()
    self.windowHorizontalPosition = stream.readU16()
    self.windowVerticalPosition = stream.readU16()
    self.windowWidth = stream.readU16()
    self.windowHeight = stream.readU16()

  def __str__(self):
    return f'{{ windowId: {self.windowId}, size: ({self.windowWidth}, {self.windowHeight}), position: ({self.windowHorizontalPosition}, {self.windowVerticalPosition}) }}'

class WindowDefinitionSegment:
  def __init__(self, stream: ByteStream):
    self.numberOfWindow = stream.readU8()
    self.windows = [WindowDefinition(stream) for _ in range(self.numberOfWindow)]

  def __str__(self):
    return f'WindowDefinitionSegment: [{",".join(list(map(str, self.windows)))}]'

class PaletteEntry:
  def __init__(self, stream: ByteStream):
    self.paletteEntryID = stream.readU8()
    self.luminance = stream.readU8()
    self.colorDifferenceRed = stream.readU8()
    self.colorDifferenceBlue = stream.readU8()
    self.transparency = stream.readU8()

  def __str__(self):
    return f'{{ paletteEntryID: {self.paletteEntryID}, YCbCr: ({self.luminance}, {self.colorDifferenceBlue}, {self.colorDifferenceRed}), alpha: {self.transparency} }}'

class PaletteDefinitionSegment:
  def __init__(self, stream: ByteStream):
    self.paletteID = stream.readU8()
    self.paletteVersionNumber = stream.readU8()
    self.paletteEntries: list[PaletteEntry] = []
    while stream: self.paletteEntries.append(PaletteEntry(stream))

  def __str__(self):
    return f'PaletteDefinitionSegment: palletId: {self.paletteID}, VersionNumber: {self.paletteVersionNumber}, [{",".join(list(map(str, self.paletteEntries)))}]'

class ObjectData:
  def __init__(self, stream: ByteStream):
    self.pixels: list[list[int]] = [[]]
    while stream:
      firstByte = stream.readU8()
      if firstByte != 0:
        self.pixels[-1].append(firstByte)
        continue
      secondByte = stream.readU8()
      if secondByte == 0:
        self.pixels.append([])
      twoBit = (secondByte & 0xC0) >> 6
      match twoBit:
        case 0b00:
          length = secondByte & 0x3F
          color = 0
          self.pixels[-1].extend([color] * length)
        case 0b01:
          length = ((secondByte & 0x3F) << 8) | (stream.readU8())
          color = 0
          self.pixels[-1].extend([color] * length)
        case 0b10:
          length = secondByte & 0x3F
          color = stream.readU8()
          self.pixels[-1].extend([color] * length)
        case 0b11:
          length = ((secondByte & 0x3F) << 8) | (stream.readU8())
          color = stream.readU8()
          self.pixels[-1].extend([color] * length)

  def __str__(self):
    return '\n'.join([','.join([f'{c:03d}' for c in row]) for row in self.pixels])

class ObjectDefinitionSegment:
  def __init__(self, stream: ByteStream):
    self.objectId = stream.readU16()
    self.objectVersionNumber = stream.readU8()
    self.lastInSequenceFlag = stream.readU8()
    self.objectDataLength = stream.readU24()
    self.width = stream.readU16()
    self.height = stream.readU16()
    self.objectData = ObjectData(stream)

class PGSRenderer:
  def __init__(self):
    self.PCS: PresentationCompositionSegment | None = None
    self.WDS: WindowDefinitionSegment | None = None
    self.PDS: PaletteDefinitionSegment | None = None
    self.ODS: ObjectDefinitionSegment | None = None

  def feed(self, data: Buffer):
    self.stream = ByteStream(memoryview(data))
    self._parse()

  def _parse(self):
    while self.stream:
      segmentType = self.stream.readU8()
      segmentSize = self.stream.readU16()
      print(hex(segmentType), segmentSize, len(self.stream))
      try:
        match (segmentType):
          case 0x14: # PDS
            self.PDS = PaletteDefinitionSegment(ByteStream(self.stream.read(segmentSize)))
          case 0x15: # ODS
            self.ODS = ObjectDefinitionSegment(ByteStream(self.stream.read(segmentSize)))
          case 0x16: # PCS
            self.PCS = PresentationCompositionSegment(ByteStream(self.stream.read(segmentSize)))
          case 0x17: # WDS
            self.WDS = WindowDefinitionSegment(ByteStream(self.stream.read(segmentSize)))
          case 0x80: # END
            self.stream.read(segmentSize)
            if self.PCS is None or self.WDS is None or self.PDS is None or self.ODS is None: continue

            palette = { palette.paletteEntryID: palette for palette in self.PDS.paletteEntries }
            image = Image.new('YCbCr', (self.ODS.width, self.ODS.height))
            for y in range(0, self.ODS.height):
              for x in range(0, self.ODS.width):
                print(y, x, self.ODS.height, self.ODS.width)
                color = self.ODS.objectData.pixels[y][x]
                value = (palette[color].luminance, palette[color].colorDifferenceBlue, palette[color].colorDifferenceRed) if color in palette else (0, 0, 0)
                image.putpixel((x, y), value)
            image = image.convert('RGBA')
            mask = Image.new('L', (self.ODS.width, self.ODS.height))
            for y in range(0, self.ODS.height):
              for x in range(0, self.ODS.width):
                color = self.ODS.objectData.pixels[y][x]
                alpha = palette[color].transparency if color in palette else 0
                mask.putpixel((x, y), alpha)
            image.putalpha(mask)
            image.save('test.png')

          case _:
            self.stream.read(segmentSize)
      except EOFError:
        pass