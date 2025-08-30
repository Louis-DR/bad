# BAD Diagram

This tool generated Box-and-Arrow Diagrams from a CLI or XML description.

The schematics follow a structure of items, anchors, links, and layouts. Items are 2D visual elements like text, image, box containers, etc. Anchors are point positions. Items have anchors, for instance on their corners. Links are 1D visual elements represented as lines between anchors. Layout are non-visual elements that affect how items and links are placed and sized. Layouts and items can have content and nest recursively.

The schematic is rendered recursively. For layouts and containers with items, a placement algorithm is used. For links, a routing algorithm is used. Place-and-route optimisation is performed to improve the schematic by modifying the elements size, position, and configuration to reduce unwanted behaviors.

## Items

Items are 2D visual elements with a size and position. The position is mostly calculated from the layout and other items. The size is mostly calculated recursively from the size of the items and layouts inside the item. Items that can contain other items or layouts have an internal padding and external margin, like in HTML.

The basic item is the `box`. It is a rectangle with a background and a border. The attributes `background-color`, `border-color` and `border-width` are used to style the box. It can contain other objects like items, layouts, etc. It has internal padding and external margin defined by the respective attributes `padding` and `margin`. It has 9 basic anchors : `top-left`, `top-center`, `top-right`, `left`, `center`, `right`, `bottom-left`, `bottom-center`, and `bottom-right`.

The syntax for a box with with size is `<box id="foobar" width="50" height="30"></box>`.

## Anchor

Anchors are point elements with only a position. They are used as start and end points for links. Visually, they can be represented as a small circle. They can be implicit, meaning they are part of items without being declared, or explicitly declared without being dependent of another elements. Explicitly declared standalone anchors have attributes `x` and `y` for their position.

The syntax for a standalone anchor is `<anchor id="foobar" x="10" y="20"/>`.

## Link

Links are basically lines between anchors. A link is defined with a start anchor and an end anchor. There are multiple styles of links, let's start with `straight`, and `orthogonal`. The basic style is the straight line between the two anchors. The orthogonal style only uses vertical and horizontal segments, and the line avoids other items by turning. It also respects the margins and padding of the items. They can link anchors from different hierarchies, meaning anchors from nested items of different depths.

The syntax for a link between the anchors of two boxes with IDs `foo` and `bar` is `<link from="foo.right" to="bar.left"/>`.

## Layout

Layouts are non-visual containers that dictate how items are laid out. Layouts contain items and other layouts. The default layout is the vertical layout.

The `vertical` and `horizontal` layout are the most basic. They arrange the items in a vertical or horizontal line. The attribute `align` defines how the items are aligned when their sizes differ. It can take the values `start`, `center`, `end`, or `stretch`.

The syntax for a horizontal layout with three items is
```
<horizontal align="center">
	<box id="box1" width="50" height="30"></box>
	<box id="box2" width="80" height="20"></box>
	<box id="box3" width="30" height="50"></box>
</horizontal>
```

The `columns` and `rows` layouts are more advanced. They arrange items respectively first vertically and horizontally, and when overflowing or after a break `<break/>` tag they jump to the next column or row. Columns and rows themselves are arranged respectively horizontally and vertically. The attribute `align` works the same as for the vertical and horizontal layouts within each column or row. The attribute `justify` defines the alignent between columns or rows when their sizes differ. It can take the values `start`, `center`, `end`, or `space`.

The syntax for a columns layout with three items on the first column and two on he second is
```
<columns align="center" justify="start">
	<box id="box1" width="50" height="30"></box>
	<box id="box2" width="80" height="20"></box>
	<box id="box3" width="30" height="50"></box>
	<break/>
	<box id="box4" width="30" height="30"></box>
	<box id="box5" width="50" height="50"></box>
</horizontal>
```
