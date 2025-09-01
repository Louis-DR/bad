# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ Project:     bad - Box-and-Arrow Diagram tool                             ║
# ║ Author:      Louis Duret-Robert - louisduret@gmail.com                    ║
# ║ Website:     louis-dr.github.io                                           ║
# ║ License:     MIT License                                                  ║
# ║ File:        bad.py                                                       ║
# ╚═══════════════════════════════════════════════════════════════════════════╝



from dataclasses import dataclass
from typing import Self



@dataclass
class Vector2:
  x: float
  y: float

  def __add__(self, other):
    return Vector2(self.x + other.x, self.y + other.y)

  def __sub__(self, other):
    return Vector2(self.x - other.x, self.y - other.y)

  def __mul__(self, other):
    if isinstance(other, Vector2):
      return Vector2(self.x * other.x, self.y * other.y)
    else:
      return Vector2(self.x * other, self.y * other)

  def __truediv__(self, other):
    if isinstance(other, Vector2):
      return Vector2(self.x / other.x, self.y / other.y)
    else:
      return Vector2(self.x / other, self.y / other)

  def __repr__(self):
    return f"[{self.x},{self.y}]"



class Element:
  """Base class for all schematic elements"""
  def __init__(self,
               id     : str  | None = None,
               parent : Self | None = None):
    self.id     = id
    self.parent = parent
  def draw(self) -> str:
    return ""



class LocatedElement(Element):
  """Base class for element with a position"""
  def __init__(self,
               id       : str     | None = None,
               parent   : Element | None = None,
               position : Vector2        = Vector2(0,0)):
    Element.__init__(self, id, parent)
    self.position = position

  @property
  def x(self): return self.position.x

  @property
  def y(self): return self.position.y

  def absolute_position(self) -> Vector2:
    """Get absolute position in global coordinates"""
    if self.parent: return self.position + self.parent.absolute_position()
    else:           return self.position



class BoundedElement(LocatedElement):
  """Base class for element with a position and a size"""
  def __init__(self,
               id       : str     | None = None,
               parent   : Element | None = None,
               position : Vector2        = Vector2(0,0),
               size     : Vector2        = Vector2(0,0)):
    LocatedElement.__init__(self, id, parent, position)
    self.size = size

  @property
  def width(self): return self.size.x

  @property
  def height(self): return self.size.y

  @property
  def x2(self): return self.x + self.width

  @property
  def y2(self): return self.y + self.height

  @property
  def center(self): return self.position + self.size / 2



class ContainerElement(BoundedElement):
  """Base class for bounded element with children"""
  def __init__(self,
               id       : str     | None = None,
               parent   : Element | None = None,
               position : Vector2        = Vector2(0,0),
               size     : Vector2        = Vector2(0,0)):
    BoundedElement.__init__(self, id, parent, position, size)
    self.children = []



@dataclass
class ElementStyle:
  pass



@dataclass
class BoxStyle(ElementStyle):
  background_color: str   = "white"
  stroke_width:     float = 1
  stroke_color:     str   = "black"
  corner_radius:    float = 0
  padding:          float = 10

class Box(BoundedElement):
  """Rectangle element with styling and anchors"""
  def __init__(self,
               id       : str     | None = None,
               parent   : Element | None = None,
               position : Vector2        = Vector2(0,0),
               size     : Vector2        = Vector2(0,0),
               style    : BoxStyle       = BoxStyle()):
    BoundedElement.__init__(self, id, parent, position, size)
    self.style = style

  def draw(self):
    return f'<rect x="{self.x}" y="{self.y}" width="{self.width}" height="{self.height}" rx="{self.style.corner_radius}" ry="{self.style.corner_radius}" fill="white" stroke="black"/>'



from PIL import Image, ImageDraw, ImageFont
font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
def split_text_to_width(text:str, width:float, font_size:float=10):
  """Split text into lines that fit within the specified width"""
  font         = ImageFont.truetype(font_path, font_size)
  dummy_image  = Image.new('RGB', (1, 1))
  draw_context = ImageDraw.Draw(dummy_image)
  words        = text.split(' ')
  lines        = []
  current_line = ""
  # Iterate over words
  for word in words:
    # Test line with word added
    if current_line:
      test_line = current_line + " " + word
    else:
      test_line = word
    # Measure width of test line
    test_width = draw_context.textlength(text=test_line, font=font)
    # If width is within bounds, continue to next word
    if test_width <= width:
      current_line = test_line
    # Else create a new line
    else:
      if current_line:
        lines.append(current_line)
      current_line = word
  # Push the last line
  if current_line:
    lines.append(current_line)
  return lines

@dataclass
class FontMetrics:
  ascent:      float
  descent:     float
  line_height: float

def get_font_metrics(font_size:float=10) -> FontMetrics:
  font = ImageFont.truetype(font_path, font_size)
  ascent, descent = font.getmetrics()
  line_height = ascent + descent
  font_metrics = FontMetrics(ascent, descent, line_height)
  return font_metrics


