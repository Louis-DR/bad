# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ Project:     bad - Box-and-Arrow Diagram tool                             ║
# ║ Author:      Louis Duret-Robert - louisduret@gmail.com                    ║
# ║ Website:     louis-dr.github.io                                           ║
# ║ License:     MIT License                                                  ║
# ║ File:        bad.py                                                       ║
# ╚═══════════════════════════════════════════════════════════════════════════╝



from dataclasses import dataclass
from enum import Enum
from typing import Self



@dataclass
class Vector2:
  x: float = 0
  y: float = 0

  def __add__(self, other):
    if isinstance(other, Vector2):
      return Vector2(self.x + other.x, self.y + other.y)
    else:
      return Vector2(self.x + other, self.y + other)

  def __sub__(self, other):
    if isinstance(other, Vector2):
      return Vector2(self.x - other.x, self.y - other.y)
    else:
      return Vector2(self.x - other, self.y - other)

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

  def max(vector_1:Self, vector_2:Self) -> Self:
    return Vector2(max(vector_1.x, vector_2.x), max(vector_1.y, vector_2.y))



@dataclass
class Position(Vector2):
  automatic: bool = True



def indent(text:str, spaces:int=2):
  indentation = spaces * ' '
  return indentation + text.replace('\n', '\n'+indentation)



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

class LayoutAlignment(Enum):
  START   = 0
  CENTER  = 1
  END     = 2

@dataclass
class LayoutStyle(BoundedElementStyle):
  margin:    float           = 0
  padding:   float           = 5
  gap:       float           = 5
  alignment: LayoutAlignment = LayoutAlignment.START



class Element:
  """Base class for all schematic elements"""
  def __init__(self,
               id : str | None = None):
    self.id     = id
    self.parent = None
  def set_parent(self, parent:Self):
    self.parent = parent
  def update(self): pass
  def draw(self) -> str: return ""



class LocatedElement(Element):
  """Base class for element with a position"""
  def __init__(self,
               id       : str | None = None,
               position : Position   = None):
    Element.__init__(self, id)
    self.position = position or Position()

  @property
  def x(self): return self.position.x

  @property
  def y(self): return self.position.y

  def absolute_position(self) -> Vector2:
    """Get absolute position in global coordinates"""
    if self.parent: return self.position + self.parent.absolute_position()
    else:           return self.position



class AnchorDirection(Enum):
  NONE       = 0
  VERTICAL   = 1
  HORIZONTAL = 2

class Anchor(LocatedElement):
  def __init__(self,
               id        : str | None      = None,
               position  : Position        = None,
               direction : AnchorDirection = None):
    LocatedElement.__init__(self, id, position)
    self.direction = direction or AnchorDirection.NONE

class RelativeAnchor(Anchor):
  def __init__(self,
               id        : str | None      = None,
               direction : AnchorDirection = None,
               reference : Vector2         = None,
               offset    : Vector2         = None):
    Anchor.__init__(self, id, direction=direction)
    self.reference = reference or Vector2()
    self.offset    = offset    or Vector2()



class BoundedElement(LocatedElement):
  """Base class for element with a position and a size"""
  def __init__(self,
               id       : str | None = None,
               position : Vector2    = None,
               size     : Vector2    = None):
    LocatedElement.__init__(self, id, position)
    self.size    = size or Vector2()
    self.anchors = {}

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

  def add_anchor(self, name:str, anchor:Anchor):
    anchor.set_parent(self)
    self.anchors[name] = anchor

  def update(self):
    LocatedElement.update(self)
    for anchor in self.anchors.values():
      anchor.update()
      if isinstance(anchor, RelativeAnchor):
        anchor.position = anchor.reference * self.size + anchor.offset



class Layout(BoundedElement):
  """Base class for layouts"""
  def __init__(self,
               id       : str | None  = None,
               position : Position    = None,
               size     : Vector2     = None,
               style    : LayoutStyle = None):
    ContainerElement.__init__(self, id, position, size)
    self.style = style or LayoutStyle()
    self.children = []

  def add(self, element:Element):
    element.set_parent(self)
    self.children.append(element)

  def update(self):
    for child in self.children:
      child.update()

  def draw(self):
    svg = f'<g id="{self.id}">'
    for child in self.children:
      svg += '\n'
      svg += indent(child.draw())
    svg += '\n'
    svg += '</g>'
    return svg



class ContainerElement(BoundedElement):
  """Base class for bounded element that can have a single child element or a layout to contain other elements"""
  def __init__(self,
               id       : str | None = None,
               position : Position   = None,
               size     : Vector2    = None):
    BoundedElement.__init__(self, id, position, size)
    self.layout = None
    self.child  = None

  def set_layout(self, layout:Layout):
    layout.set_parent(self)
    self.layout = layout

  def set_child(self, element:Element):
    element.set_parent(self)
    self.child = element

  def update(self):
    BoundedElement.update(self)
    if self.layout is not None:
      self.layout.update()
      self.size = Vector2.max(self.size, self.layout.size) + 2 * self.layout.style.margin
    if self.child is not None:
      self.child.update()
      self.size = Vector2.max(self.size, self.child.size) + 2 * self.child.style.margin

  def draw(self):
    svg = ''
    if self.layout is not None:
      svg += '\n' + indent(self.layout.draw())
    if self.child is not None:
      svg += '\n' + indent(self.child.draw())
    return svg



@dataclass
class BoxStyle(ContainerElementStyle):
  background_color: str   = "white"
  stroke_width:     float = 1
  stroke_color:     str   = "black"
  corner_radius:    float = 0

class Box(ContainerElement):
  """Rectangle element with styling and anchors"""
  def __init__(self,
               id       : str | None = None,
               position : Position   = None,
               size     : Vector2    = None,
               style    : BoxStyle   = None):
    ContainerElement.__init__(self, id, position, size)
    self.style = style or BoxStyle()
    self.add_anchor("top_left",      RelativeAnchor(direction=AnchorDirection.NONE,       reference=Vector2(0.0,0.0)))
    self.add_anchor("top_center",    RelativeAnchor(direction=AnchorDirection.VERTICAL,   reference=Vector2(0.5,0.0)))
    self.add_anchor("top_right",     RelativeAnchor(direction=AnchorDirection.NONE,       reference=Vector2(1.0,0.0)))
    self.add_anchor("center_left",   RelativeAnchor(direction=AnchorDirection.HORIZONTAL, reference=Vector2(0.0,0.5)))
    self.add_anchor("center_right",  RelativeAnchor(direction=AnchorDirection.HORIZONTAL, reference=Vector2(1.0,0.5)))
    self.add_anchor("bottom_left",   RelativeAnchor(direction=AnchorDirection.NONE,       reference=Vector2(0.0,1.0)))
    self.add_anchor("bottom_center", RelativeAnchor(direction=AnchorDirection.VERTICAL,   reference=Vector2(0.5,1.0)))
    self.add_anchor("bottom_right",  RelativeAnchor(direction=AnchorDirection.NONE,       reference=Vector2(1.0,1.0)))

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
               id       : str | None = None,
               text     : str        = "",
               position : Position   = None,
               size     : Vector2    = None,
               style    : TextStyle  = None):
    BoundedElement.__init__(self, id, position, size)
    self.style = style or TextStyle()
    self.text  = text
    self.lines = []

  def update(self):
    """Update text lines and recalculate size if needed"""
    self.lines   = split_text_to_width(self.text, self.width, self.style.font_size)
    font_metrics = get_font_metrics(self.style.font_size)
    self.size.y  = (len(self.lines) + 1) * font_metrics.line_height

  def draw(self):
    """Generate SVG for the text element"""
    self.update()
    font_metrics = get_font_metrics(self.style.font_size)
    svg = '<g>'
    if self.lines:
      line_position    = self.absolute_position()
      line_position   += self.style.margin
      line_position.y += font_metrics.ascent
      for line in self.lines:
        svg += '\n'
        svg += f'  <text x="{line_position.x}" y="{line_position.y}" font-family="{self.style.font_family}" font-size="{self.style.font_size}" fill="{self.style.font_color}">{line}</text>'
        line_position.y += font_metrics.line_height
    svg += '\n'
    svg += '</g>'
    return svg





class VerticalLayout(Layout):
  """Layout to display elements vertically"""
  def __init__(self,
               id       : str | None  = None,
               position : Position    = None,
               size     : Vector2     = None,
               style    : LayoutStyle = None):
    Layout.__init__(self, id, position, size, style)

  def update(self):
    Layout.update(self)

    # Compute horizontally
    max_x_bound = self.width
    for child in self.children:
      if child.position.automatic:
        child_x_margin = max(child.style.margin, self.style.padding)
        max_x_bound    = max(max_x_bound, child.width + 2 * child_x_margin)
    self.size.x = max_x_bound

    # Compute vertically
    current_gap = self.style.padding
    child_y     = 0
    for child in self.children:
      if child.position.automatic:
        current_gap      = max(current_gap, child.style.margin)
        child_y         += current_gap
        child.position.y = child_y
        child_y         += child.height
        current_gap      = max(self.style.gap, child.style.margin)
    current_gap = max(current_gap, self.style.padding)
    child_y += current_gap

    # Align horizontally
    for child in self.children:
      if child.position.automatic:
        child_x_margin = max(child.style.margin, self.style.padding)
        match self.style.alignment:
          case LayoutAlignment.START:
            child.position.x = child_x_margin
          case LayoutAlignment.CENTER:
            child.position.x = (self.width - child.width) / 2
          case LayoutAlignment.END:
            child.position.x = self.width - child_x_margin - child.width

    # Update size
    self.size.x = max_x_bound
    self.size.y = child_y



class HorizontalLayout(Layout):
  """Layout to display elements horizontally"""
  def __init__(self,
               id       : str | None  = None,
               position : Position    = None,
               size     : Vector2     = None,
               style    : LayoutStyle = None):
    Layout.__init__(self, id, position, size, style)

  def update(self):
    Layout.update(self)

    # Compute vertically
    max_y_bound = self.height
    for child in self.children:
      if child.position.automatic:
        child_y_margin = max(child.style.margin, self.style.padding)
        max_y_bound    = max(max_y_bound, child.height + 2 * child_y_margin)
    self.size.y = max_y_bound

    # Compute horizontally
    current_gap = self.style.padding
    child_x     = 0
    for child in self.children:
      if child.position.automatic:
        current_gap      = max(current_gap, child.style.margin)
        child_x         += current_gap
        child.position.x = child_x
        child_x         += child.width
        current_gap      = max(self.style.gap, child.style.margin)
    current_gap = max(current_gap, self.style.padding)
    child_x += current_gap

    # Align vertically
    for child in self.children:
      if child.position.automatic:
        child_y_margin = max(child.style.margin, self.style.padding)
        match self.style.alignment:
          case LayoutAlignment.START:
            child.position.y = child_y_margin
          case LayoutAlignment.CENTER:
            child.position.y = (self.height - child.height) / 2
          case LayoutAlignment.END:
            child.position.y = self.height - child_y_margin - child.height

    # Update size
    self.size.x = child_x
    self.size.y = max_y_bound



@dataclass
class LinkStyle(Style):
  margin:       float = 5
  stroke_width: float = 1
  stroke_color: str   = "red"

class Link(Element):
  def __init__(self,
               id    : str | None = None,
               start : Anchor     = None,
               end   : Anchor     = None,
               style : LinkStyle  = None):
    Element.__init__(self, id)
    self.start    = start
    self.end      = end
    self.style    = style or LinkStyle()
    self.points   = []
    self.position = Vector2()

  def update(self):
    if self.start is None or self.end is None:
      return
    start_absolute_position = self.start.absolute_position()
    end_absolute_position   = self.end.absolute_position()
    self.points = []
    self.points.append(start_absolute_position)
    if self.start.direction == self.end.direction:
      if self.start.direction == AnchorDirection.HORIZONTAL:
        if start_absolute_position.y == end_absolute_position.y:
          pass
        else:
          mid_point_x = (start_absolute_position.x + end_absolute_position.x) / 2
          self.points.append(Vector2(mid_point_x, start_absolute_position.y))
          self.points.append(Vector2(mid_point_x, end_absolute_position.y))
      else:
        if start_absolute_position.x == end_absolute_position.x:
          pass
        else:
          mid_point_y = (start_absolute_position.y + end_absolute_position.y) / 2
          self.points.append(Vector2(start_absolute_position.y, mid_point_y))
          self.points.append(Vector2(end_absolute_position.y,   mid_point_y))
    else:
      if self.start.direction == AnchorDirection.HORIZONTAL:
        self.points.append(Vector2(end_absolute_position.x, start_absolute_position.y))
      else:
        self.points.append(Vector2(start_absolute_position.x, end_absolute_position.y))
    self.points.append(end_absolute_position)

  def draw(self):
    svg = '<polyline points="'
    for point in self.points:
      point_absolute_position = point + self.position
      svg += f'{point_absolute_position.x},{point_absolute_position.y} '
    svg  = svg.rstrip()
    svg += f'" style="stroke-width:{self.style.stroke_width}; stroke:{self.style.stroke_color}; fill:none;"/>'
    return svg



class Diagram:
  def __init__(self):
    self.size   = None
    self.layout = None
    self.links  = []

  def set_layout(self, layout:Layout):
    self.layout = layout

  def add_link(self, link:Link):
    self.links.append(link)

  def update(self):
    self.layout.update()
    self.size = self.layout.size
    for link in self.links:
      link.update()

  def render(self):
    svg_string  = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
    svg_string += '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'
    svg_string += f'<svg width="{self.size.x}" height="{self.size.y}" viewBox="0 0 {self.size.x} {self.size.y}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n'
    svg_string += self.layout.draw() + '\n'
    for link in self.links:
      svg_string += link.draw() + '\n'
    svg_string += '</svg>'
    return svg_string

