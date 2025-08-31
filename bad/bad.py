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
               id     : str | int | None = None,
               parent : Self      | None = None):
    self.id     = id
    self.parent = parent
  def draw(self) -> str:
    return ""



class LocatedElement(Element):
  """Base class for schematic with a position"""
  def __init__(self,
               id       : str | int | None = None,
               parent   : Element   | None = None,
               position : Vector2          = Vector2(0,0)):
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
  """Base class for schematic with a position and a size"""
  def __init__(self,
               id       : str | int | None = None,
               parent   : Element   | None = None,
               position : Vector2          = Vector2(0,0),
               size     : Vector2          = Vector2(0,0)):
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
