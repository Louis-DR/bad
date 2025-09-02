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



@dataclass
class Style:
  pass

@dataclass
class ElementStyle(Style):
  pass

@dataclass
class LocatedElementStyle(ElementStyle):
  margin: float = 5

@dataclass
class BoundedElementStyle(LocatedElementStyle):
  pass

@dataclass
class ContainerElementStyle(BoundedElementStyle):
  pass

@dataclass
class LayoutStyle(BoundedElementStyle):
  padding: float = 5
  gap:     float = 5



class Element:
  """Base class for all schematic elements"""
  def __init__(self,
               id     : str  | None = None,
               parent : Self | None = None):
    self.id     = id
    self.parent = parent
  def update(self): pass
  def draw(self) -> str: return ""



class LocatedElement(Element):
  """Base class for element with a position"""
  def __init__(self,
               id       : str     | None = None,
               parent   : Element | None = None,
               position : Vector2        = None):
    Element.__init__(self, id, parent)
    self.position = position or Vector2(0,0)

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
               position : Vector2        = None,
               size     : Vector2        = None):
    LocatedElement.__init__(self, id, parent, position)
    self.size = size or Vector2(0,0)

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



class Layout(BoundedElement):
  """Base class for layouts"""
  def __init__(self,
               id       : str     | None = None,
               parent   : Element | None = None,
               position : Vector2        = None,
               size     : Vector2        = None,
               style    : LayoutStyle    = LayoutStyle()):
    ContainerElement.__init__(self, id, parent, position, size)
    self.style = style or LayoutStyle()
    self.children = []

  def add(self, element:Element):
    self.children.append(element)

  def update(self):
    for child in self.children:
      child.update()

  def draw(self):
    svg = f'<g id="{self.id}">'
    for child in self.children:
      svg += '\n'
      svg += child.draw()
    svg += '\n'
    svg += '</g>'
    return svg



class ContainerElement(BoundedElement):
  """Base class for bounded element that can have a layout to contain other elements"""
  def __init__(self,
               id       : str     | None = None,
               parent   : Element | None = None,
               position : Vector2        = None,
               size     : Vector2        = None):
    BoundedElement.__init__(self, id, parent, position, size)
    self.layout = None

  def set_layout(self, layout:Layout):
    self.layout = layout

  def update(self):
    if self.layout is not None:
      self.layout.update()
      self.size = self.layout.size

  def draw(self):
    if self.layout is not None:
      return '\n' + self.layout.draw()
    else:
      return ''



@dataclass
class BoxStyle(ContainerElementStyle):
  background_color: str   = "white"
  stroke_width:     float = 1
  stroke_color:     str   = "black"
  corner_radius:    float = 0

class Box(ContainerElement):
  """Rectangle element with styling and anchors"""
  def __init__(self,
               id       : str     | None = None,
               parent   : Element | None = None,
               position : Vector2        = None,
               size     : Vector2        = None,
               style    : BoxStyle       = None):
    ContainerElement.__init__(self, id, parent, position, size)
    self.style  = style or BoxStyle()

  def draw(self):
    absolute_position = self.absolute_position()
    svg  = f'<rect id="{self.id}" x="{absolute_position.x}" y="{absolute_position.y}" width="{self.width}" height="{self.height}" rx="{self.style.corner_radius}" ry="{self.style.corner_radius}" fill="white" stroke="black"/>'
    svg += ContainerElement.draw(self)
    return svg



from PIL import Image, ImageDraw, ImageFont
font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
pil_text_width_rectifier = 1.1
def split_text_to_width(text:str, width:float, font_size:float=10):
  """Split text into lines that fit within the specified width"""
  font         = ImageFont.truetype(font_path, font_size)
  dummy_image  = Image.new('RGB', (1,1))
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
    test_width  = draw_context.textlength(text=test_line, font=font)
    test_width *= pil_text_width_rectifier
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
  font            = ImageFont.truetype(font_path, font_size)
  ascent, descent = font.getmetrics()
  line_height     = ascent + descent
  font_metrics    = FontMetrics(ascent, descent, line_height)
  return font_metrics





@dataclass
class TextStyle(BoundedElementStyle):
  font_family: str = "Arial"
  font_style:  str = "regular"
  font_size:   int = 10
  font_color:  str = "black"

class Text(BoundedElement):
  """Text region within a rectangle"""
  def __init__(self,
               id       : str     | None = None,
               parent   : Element | None = None,
               text     : str            = "",
               position : Vector2        = None,
               size     : Vector2        = None,
               style    : TextStyle      = None):
    BoundedElement.__init__(self, id, parent, position, size)
    self.style = style or TextStyle()
    self.text  = text
    self.lines = []

  def update(self):
    """Update text lines and recalculate size if needed"""
    self.lines   = split_text_to_width(self.text, self.width, self.style.font_size)
    font_metrics = get_font_metrics(self.style.font_size)
    self.height  = (len(self.lines) + 1) * font_metrics.line_height

  def draw(self):
    """Generate SVG for the text element"""
    self.update()
    font_metrics = get_font_metrics(self.style.font_size)
    svg = '<g>'
    if self.lines:
      line_position = self.absolute_position()
      line_position.y += font_metrics.ascent
      for line in self.lines:
        svg += '\n'
        svg += f'<text x="{line_position.x}" y="{line_position.y}" font-family="{self.style.font_family}" font-size="{self.style.font_size}" fill="{self.style.font_color}">{line}</text>\n'
        line_position.y += font_metrics.line_height
    svg += '\n'
    svg += '</g>'
    return svg





class VerticalLayout(Layout):
  """Layout to display elements vertically"""
  def __init__(self,
               id       : str     | None = None,
               parent   : Element | None = None,
               position : Vector2        = None,
               size     : Vector2        = None):
    Layout.__init__(self, id, parent, position, size)

  def update(self):
    Layout.update(self)
    max_child_width = self.width
    child_y         = 0
    current_gap     = self.style.padding
    for child in self.children:
      current_gap = max(current_gap, child.style.margin)
      child_y += current_gap
      child.position = Vector2(self.style.padding, child_y)
      child_y += child.height
      current_gap = max(self.style.gap, child.style.margin)
      max_child_width = max(max_child_width, child.width)
    current_gap = max(current_gap, self.style.padding)
    child_y += current_gap
    self.size.x = max_child_width + 2 * self.style.padding
    self.size.y = child_y



class HorizontalLayout(Layout):
  """Layout to display elements horizontally"""
  def __init__(self,
               id       : str     | None = None,
               parent   : Element | None = None,
               position : Vector2        = None,
               size     : Vector2        = None):
    Layout.__init__(self, id, parent, position, size)

  def update(self):
    Layout.update(self)
    max_child_height = self.height
    child_x         = 0
    current_gap     = self.style.padding
    for child in self.children:
      current_gap = max(current_gap, child.style.margin)
      child_x += current_gap
      child.position = Vector2(child_x, self.style.padding)
      child_x += child.width
      current_gap = max(self.style.gap, child.style.margin)
      max_child_height = max(max_child_height, child.height)
    current_gap = max(current_gap, self.style.padding)
    child_x += current_gap
    self.size.x = child_x
    self.size.y = max_child_height + 2 * self.style.padding



class Diagram:
  def __init__(self):
    self.size   = None
    self.layout = None

  def update(self):
    self.layout.update()
    self.size = self.layout.size

  def render(self):
    svg_string  = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
    svg_string += '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'
    svg_string += f'<svg width="{self.size.x}" height="{self.size.y}" viewBox="0 0 {self.size.x} {self.size.y}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n'
    svg_string += self.layout.draw() + '\n'
    svg_string += '</svg>'
    return svg_string

