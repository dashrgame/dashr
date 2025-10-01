import pygame
from typing import List, Tuple, Optional
from enum import Enum

from client.src.ui.core import UIComponent, Panel, UIConstants
from client.src.asset.font.font import Font


class LayoutDirection(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class Alignment(Enum):
    START = "start"  # Left/Top
    CENTER = "center"
    END = "end"  # Right/Bottom
    STRETCH = "stretch"  # Fill available space


class LinearLayout(Panel):
    """Layout that arranges children in a line (horizontal or vertical)"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        direction: LayoutDirection = LayoutDirection.VERTICAL,
        spacing: int = UIConstants.DEFAULT_MARGIN,
        padding: int = UIConstants.DEFAULT_PADDING,
        alignment: Alignment = Alignment.START,
        **kwargs
    ):
        super().__init__(x, y, width, height, **kwargs)
        self.direction = direction
        self.spacing = spacing
        self.padding = padding
        self.alignment = alignment

    def add_child(self, child: UIComponent, weight: float = 0.0):
        """Add a child with optional weight for flexible sizing"""
        super().add_child(child)
        # Store weight as a custom attribute
        setattr(child, "_layout_weight", weight)
        self._update_layout()

    def remove_child(self, child: UIComponent):
        """Remove a child and update layout"""
        super().remove_child(child)
        self._update_layout()

    def set_spacing(self, spacing: int):
        """Set spacing between children"""
        self.spacing = spacing
        self._update_layout()

    def set_padding(self, padding: int):
        """Set padding around children"""
        self.padding = padding
        self._update_layout()

    def set_alignment(self, alignment: Alignment):
        """Set alignment of children"""
        self.alignment = alignment
        self._update_layout()

    def _update_layout(self):
        """Update the layout of all children"""
        if not self.children:
            return

        available_width = self.width - 2 * self.padding
        available_height = self.height - 2 * self.padding

        if self.direction == LayoutDirection.HORIZONTAL:
            self._layout_horizontal(available_width, available_height)
        else:
            self._layout_vertical(available_width, available_height)

    def _layout_horizontal(self, available_width: int, available_height: int):
        """Layout children horizontally"""
        total_spacing = (
            self.spacing * (len(self.children) - 1) if len(self.children) > 1 else 0
        )

        # Calculate fixed and flexible widths
        fixed_width = 0
        total_weight = 0.0

        for child in self.children:
            weight = getattr(child, "_layout_weight", 0.0)
            if weight <= 0:
                fixed_width += child.width
            else:
                total_weight += weight

        # Calculate remaining width for flexible children
        remaining_width = available_width - fixed_width - total_spacing

        # Position children
        current_x = self.padding

        for i, child in enumerate(self.children):
            weight = getattr(child, "_layout_weight", 0.0)

            # Calculate child width
            if weight > 0 and total_weight > 0:
                child_width = int(remaining_width * weight / total_weight)
            else:
                child_width = child.width

            # Calculate child height based on alignment
            if self.alignment == Alignment.STRETCH:
                child_height = available_height
                child_y = self.padding
            elif self.alignment == Alignment.CENTER:
                child_height = child.height
                child_y = self.padding + (available_height - child_height) // 2
            elif self.alignment == Alignment.END:
                child_height = child.height
                child_y = self.padding + available_height - child_height
            else:  # START
                child_height = child.height
                child_y = self.padding

            # Set child position and size
            child.x = current_x
            child.y = child_y
            child.width = child_width
            child.height = child_height

            current_x += child_width + (
                self.spacing if i < len(self.children) - 1 else 0
            )

    def _layout_vertical(self, available_width: int, available_height: int):
        """Layout children vertically"""
        total_spacing = (
            self.spacing * (len(self.children) - 1) if len(self.children) > 1 else 0
        )

        # Calculate fixed and flexible heights
        fixed_height = 0
        total_weight = 0.0

        for child in self.children:
            weight = getattr(child, "_layout_weight", 0.0)
            if weight <= 0:
                fixed_height += child.height
            else:
                total_weight += weight

        # Calculate remaining height for flexible children
        remaining_height = available_height - fixed_height - total_spacing

        # Position children
        current_y = self.padding

        for i, child in enumerate(self.children):
            weight = getattr(child, "_layout_weight", 0.0)

            # Calculate child height
            if weight > 0 and total_weight > 0:
                child_height = int(remaining_height * weight / total_weight)
            else:
                child_height = child.height

            # Calculate child width based on alignment
            if self.alignment == Alignment.STRETCH:
                child_width = available_width
                child_x = self.padding
            elif self.alignment == Alignment.CENTER:
                child_width = child.width
                child_x = self.padding + (available_width - child_width) // 2
            elif self.alignment == Alignment.END:
                child_width = child.width
                child_x = self.padding + available_width - child_width
            else:  # START
                child_width = child.width
                child_x = self.padding

            # Set child position and size
            child.x = child_x
            child.y = current_y
            child.width = child_width
            child.height = child_height

            current_y += child_height + (
                self.spacing if i < len(self.children) - 1 else 0
            )

    def update(self, dt: float):
        super().update(dt)

    def render(self, surface: pygame.Surface, font: Font):
        super().render(surface, font)


class GridLayout(Panel):
    """Layout that arranges children in a grid"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        rows: int,
        columns: int,
        spacing: int = UIConstants.DEFAULT_MARGIN,
        padding: int = UIConstants.DEFAULT_PADDING,
        **kwargs
    ):
        super().__init__(x, y, width, height, **kwargs)
        self.rows = rows
        self.columns = columns
        self.spacing = spacing
        self.padding = padding
        self.grid_children: List[List[Optional[UIComponent]]] = []

        # Initialize grid
        for r in range(rows):
            row: List[Optional[UIComponent]] = [None] * columns
            self.grid_children.append(row)

    def add_child_at(
        self,
        child: UIComponent,
        row: int,
        column: int,
        row_span: int = 1,
        col_span: int = 1,
    ):
        """Add a child at a specific grid position"""
        if 0 <= row < self.rows and 0 <= column < self.columns:
            # Check if the position is available
            for r in range(row, min(row + row_span, self.rows)):
                for c in range(column, min(column + col_span, self.columns)):
                    if self.grid_children[r][c] is not None:
                        return False  # Position occupied

            # Place the child in the grid
            for r in range(row, min(row + row_span, self.rows)):
                for c in range(column, min(column + col_span, self.columns)):
                    self.grid_children[r][c] = child

            # Store grid info on the child
            setattr(child, "_grid_row", row)
            setattr(child, "_grid_column", column)
            setattr(child, "_grid_row_span", row_span)
            setattr(child, "_grid_col_span", col_span)

            super().add_child(child)
            self._update_layout()
            return True

        return False

    def remove_child_at(self, row: int, column: int):
        """Remove a child at a specific grid position"""
        if 0 <= row < self.rows and 0 <= column < self.columns:
            child = self.grid_children[row][column]
            if child:
                # Clear all grid positions for this child
                row_span = getattr(child, "_grid_row_span", 1)
                col_span = getattr(child, "_grid_col_span", 1)
                start_row = getattr(child, "_grid_row", row)
                start_col = getattr(child, "_grid_column", column)

                for r in range(start_row, min(start_row + row_span, self.rows)):
                    for c in range(start_col, min(start_col + col_span, self.columns)):
                        self.grid_children[r][c] = None

                super().remove_child(child)
                self._update_layout()
                return True

        return False

    def _update_layout(self):
        """Update the layout of all children"""
        available_width = self.width - 2 * self.padding
        available_height = self.height - 2 * self.padding

        # Calculate cell dimensions
        total_h_spacing = self.spacing * (self.columns - 1) if self.columns > 1 else 0
        total_v_spacing = self.spacing * (self.rows - 1) if self.rows > 1 else 0

        cell_width = (
            (available_width - total_h_spacing) // self.columns
            if self.columns > 0
            else 0
        )
        cell_height = (
            (available_height - total_v_spacing) // self.rows if self.rows > 0 else 0
        )

        # Position children
        processed_children = set()

        for row in range(self.rows):
            for col in range(self.columns):
                child = self.grid_children[row][col]
                if child and child not in processed_children:
                    processed_children.add(child)

                    # Get child's grid info
                    start_row = getattr(child, "_grid_row", row)
                    start_col = getattr(child, "_grid_column", col)
                    row_span = getattr(child, "_grid_row_span", 1)
                    col_span = getattr(child, "_grid_col_span", 1)

                    # Calculate position and size
                    child_x = self.padding + start_col * (cell_width + self.spacing)
                    child_y = self.padding + start_row * (cell_height + self.spacing)
                    child_width = cell_width * col_span + self.spacing * (col_span - 1)
                    child_height = cell_height * row_span + self.spacing * (
                        row_span - 1
                    )

                    child.x = child_x
                    child.y = child_y
                    child.width = child_width
                    child.height = child_height

    def update(self, dt: float):
        super().update(dt)

    def render(self, surface: pygame.Surface, font: Font):
        super().render(surface, font)


class FlexLayout(Panel):
    """Flexible layout similar to CSS Flexbox"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        direction: LayoutDirection = LayoutDirection.HORIZONTAL,
        justify_content: Alignment = Alignment.START,
        align_items: Alignment = Alignment.START,
        spacing: int = UIConstants.DEFAULT_MARGIN,
        padding: int = UIConstants.DEFAULT_PADDING,
        wrap: bool = False,
        **kwargs
    ):
        super().__init__(x, y, width, height, **kwargs)
        self.direction = direction
        self.justify_content = justify_content  # Main axis alignment
        self.align_items = align_items  # Cross axis alignment
        self.spacing = spacing
        self.padding = padding
        self.wrap = wrap

    def add_child(
        self,
        child: UIComponent,
        flex_grow: float = 0.0,
        flex_shrink: float = 1.0,
        flex_basis: Optional[int] = None,
    ):
        """Add a child with flex properties"""
        super().add_child(child)
        setattr(child, "_flex_grow", flex_grow)
        setattr(child, "_flex_shrink", flex_shrink)
        setattr(child, "_flex_basis", flex_basis)
        self._update_layout()

    def _update_layout(self):
        """Update the flex layout"""
        if not self.children:
            return

        available_width = self.width - 2 * self.padding
        available_height = self.height - 2 * self.padding

        if self.direction == LayoutDirection.HORIZONTAL:
            self._layout_flex_horizontal(available_width, available_height)
        else:
            self._layout_flex_vertical(available_width, available_height)

    def _layout_flex_horizontal(self, available_width: int, available_height: int):
        """Layout flex children horizontally"""
        total_spacing = (
            self.spacing * (len(self.children) - 1) if len(self.children) > 1 else 0
        )
        main_axis_space = available_width - total_spacing

        # Calculate initial sizes
        total_flex_basis = 0
        total_flex_grow = 0

        for child in self.children:
            flex_basis = getattr(child, "_flex_basis", None) or child.width
            flex_grow = getattr(child, "_flex_grow", 0.0)

            child._calculated_width = flex_basis
            total_flex_basis += flex_basis
            total_flex_grow += flex_grow

        # Distribute remaining space
        remaining_space = main_axis_space - total_flex_basis

        if remaining_space > 0 and total_flex_grow > 0:
            for child in self.children:
                flex_grow = getattr(child, "_flex_grow", 0.0)
                if flex_grow > 0:
                    extra_width = int(remaining_space * flex_grow / total_flex_grow)
                    child._calculated_width += extra_width

        # Position children based on justify_content
        current_x = self.padding

        if self.justify_content == Alignment.CENTER:
            total_content_width = (
                sum(child._calculated_width for child in self.children) + total_spacing
            )
            current_x = self.padding + (available_width - total_content_width) // 2
        elif self.justify_content == Alignment.END:
            total_content_width = (
                sum(child._calculated_width for child in self.children) + total_spacing
            )
            current_x = self.padding + available_width - total_content_width

        for i, child in enumerate(self.children):
            # Main axis (width and x)
            child.x = current_x
            child.width = child._calculated_width

            # Cross axis (height and y) based on align_items
            if self.align_items == Alignment.STRETCH:
                child.height = available_height
                child.y = self.padding
            elif self.align_items == Alignment.CENTER:
                child.y = self.padding + (available_height - child.height) // 2
            elif self.align_items == Alignment.END:
                child.y = self.padding + available_height - child.height
            else:  # START
                child.y = self.padding

            current_x += child.width + (
                self.spacing if i < len(self.children) - 1 else 0
            )

    def _layout_flex_vertical(self, available_width: int, available_height: int):
        """Layout flex children vertically"""
        total_spacing = (
            self.spacing * (len(self.children) - 1) if len(self.children) > 1 else 0
        )
        main_axis_space = available_height - total_spacing

        # Calculate initial sizes
        total_flex_basis = 0
        total_flex_grow = 0

        for child in self.children:
            flex_basis = getattr(child, "_flex_basis", None) or child.height
            flex_grow = getattr(child, "_flex_grow", 0.0)

            child._calculated_height = flex_basis
            total_flex_basis += flex_basis
            total_flex_grow += flex_grow

        # Distribute remaining space
        remaining_space = main_axis_space - total_flex_basis

        if remaining_space > 0 and total_flex_grow > 0:
            for child in self.children:
                flex_grow = getattr(child, "_flex_grow", 0.0)
                if flex_grow > 0:
                    extra_height = int(remaining_space * flex_grow / total_flex_grow)
                    child._calculated_height += extra_height

        # Position children based on justify_content
        current_y = self.padding

        if self.justify_content == Alignment.CENTER:
            total_content_height = (
                sum(child._calculated_height for child in self.children) + total_spacing
            )
            current_y = self.padding + (available_height - total_content_height) // 2
        elif self.justify_content == Alignment.END:
            total_content_height = (
                sum(child._calculated_height for child in self.children) + total_spacing
            )
            current_y = self.padding + available_height - total_content_height

        for i, child in enumerate(self.children):
            # Main axis (height and y)
            child.y = current_y
            child.height = child._calculated_height

            # Cross axis (width and x) based on align_items
            if self.align_items == Alignment.STRETCH:
                child.width = available_width
                child.x = self.padding
            elif self.align_items == Alignment.CENTER:
                child.x = self.padding + (available_width - child.width) // 2
            elif self.align_items == Alignment.END:
                child.x = self.padding + available_width - child.width
            else:  # START
                child.x = self.padding

            current_y += child.height + (
                self.spacing if i < len(self.children) - 1 else 0
            )

    def update(self, dt: float):
        super().update(dt)

    def render(self, surface: pygame.Surface, font: Font):
        super().render(surface, font)
