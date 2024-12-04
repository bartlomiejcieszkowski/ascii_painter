#!/usr/bin/env python3
import os.path
import sys
from typing import Tuple

RETUI_PATH = os.environ.get("RETUI_PATH", None)
if RETUI_PATH and os.path.exists(os.path.realpath(os.path.join(RETUI_PATH, "src"))):
    print(f"retui from env var RETUI_PATH={RETUI_PATH}")
    RETUI_PATH = os.path.realpath(os.path.join(RETUI_PATH, "src"))
    sys.path.append(RETUI_PATH)

from retui.base import TerminalColor, Color, ColorBits, Rectangle, json_convert
from retui.enums import TextAlign, Dock, DimensionsFlag
from retui import json_loader, App
from retui.widgets import BorderWidget, Pane
from retui.input_handling import MouseEvent

import argparse

import logging
import logging.handlers

from pathlib import Path


class AsciiPainter:
    def __init__(self):
        self.color = TerminalColor(Color(15, ColorBits.Bit8), Color(1, ColorBits.Bit8))
        self.brush_widget = None
        self.app = None

    def invalidate(self):
        self.pane


class Colors8BitPalette(BorderWidget):
    @classmethod
    def from_dict(cls, **kwargs):
        return cls(
            app=kwargs.pop("app"),
            x=kwargs.pop("x"),
            y=kwargs.pop("y"),
            dock=json_convert("dock", kwargs.pop("dock", None)),
            dimensions=json_convert("dimensions", kwargs.pop("dimensions", None)),
            borderless=kwargs.pop("borderless", False),
            ascii_painter=kwargs.pop("ascii_painter", None)
        )

    def __init__(self, app, x: int, y: int,
                 dock: Dock, dimensions: DimensionsFlag = DimensionsFlag.Absolute,
                 borderless: bool = False, ascii_painter: AsciiPainter = None):
        border = (0 if borderless else 2)
        width = 8 * 2 + border
        height = 2 + border
        super().__init__(app=app, x=x, y=y, width=width, height=height, dock=dock,
                         dimensions=dimensions, borderless=borderless)
        self.title = 'Colors'
        self.ascii_painter = ascii_painter

    def draw(self):
        super().draw()
        border = 0 if self.borderless else 1
        y = self.last_dimensions.y + border
        x = self.last_dimensions.x + border
        width = self.last_dimensions.width - (border * 2)
        height = self.last_dimensions.height - (border * 2)
        start = 0
        end = height
        offset_str = self.app.brush.str_right(x)
        color = Color(0, ColorBits.Bit8)
        for h in range(start, end):
            self.app.brush.move_cursor(row=y + h)
            line = offset_str
            for i in range(h * 8, (h + 1) * 8):
                color.color = i
                line += self.app.brush.background_color(color=color) + '  '
            self.app.brush.print(line + self.app.brush.reset_color(), end='')

    def point_to_color(self, point: Tuple[int, int]):
        local_column, local_row = self.local_point(point)

        if local_row is None or local_column is None:
            return None

        color_idx = local_row * 8 + (local_column // 2)
        return Color(color_idx, ColorBits.Bit8)

    def handle(self, event):
        if isinstance(event, MouseEvent):
            if event.button in [event.button.LMB, event.button.RMB] and not event.pressed:
                color = self.point_to_color(event.coordinates)
                if color is None:
                    return
                # raise Exception(color)
                if event.button == event.button.LMB:
                    self.ascii_painter.color.foreground = color
                elif event.button == event.button.RMB:
                    self.ascii_painter.color.background = color
                # self.ascii_painter.app.requires_draw = True
                self.ascii_painter.brush_widget.draw()


class BrushWidget(BorderWidget):
    @classmethod
    def from_dict(cls, **kwargs):
        return cls(
            app=kwargs.pop("app"),
            x=kwargs.pop("x"),
            y=kwargs.pop("y"),
            dock=json_convert("dock", kwargs.pop("dock", None)),
            dimensions=json_convert("dimensions", kwargs.pop("dimensions", None)),
            borderless=kwargs.pop("borderless", False),
            ascii_painter=kwargs.pop("ascii_painter", None)
        )

    def __init__(self, app, x: int, y: int,
                 dock: Dock, dimensions: DimensionsFlag = DimensionsFlag.Absolute,
                 borderless: bool = False, ascii_painter: AsciiPainter = None):
        border = (0 if borderless else 2)
        width = 3 * 2 + border
        height = 2 + border
        super().__init__(app=app, x=x, y=y, width=width, height=height, dock=dock,
                         dimensions=dimensions, borderless=borderless)
        self.title = 'Brush'
        self.ascii_painter = ascii_painter

    def draw(self):
        super().draw()
        border = 0 if self.borderless else 1
        y = self.last_dimensions.y + border
        x = self.last_dimensions.x + border
        width = self.last_dimensions.width - (border * 2)
        height = self.last_dimensions.height - (border * 2)
        start = 0
        end = height
        offset_str = self.app.brush.str_right(x)

        space = ' ' * width
        # fgcolor
        self.app.brush.move_cursor(row=y)
        self.app.brush.print(offset_str, self.app.brush.background_color(
            color=self.ascii_painter.color.foreground), space, self.app.brush.reset_color(), end='')

        # bgcolor
        self.app.brush.move_cursor(row=y + 1)
        self.app.brush.print(offset_str, self.app.brush.background_color(
            color=self.ascii_painter.color.background), space, self.app.brush.reset_color(), end='')


class CanvasCell:
    def __init__(self, value, color: TerminalColor):
        self.value = value
        self.color = color


class Canvas(BorderWidget):
    @classmethod
    def from_dict(cls, **kwargs):
        return cls(
            app=kwargs.pop("app"),
            x=kwargs.pop("x"),
            y=kwargs.pop("y"),
            width=kwargs.pop("width"),
            height=kwargs.pop("height"),
            dock=json_convert("dock", kwargs.pop("dock", None)),
            dimensions=json_convert("dimensions", kwargs.pop("dimensions", None)),
            borderless=kwargs.pop("borderless", False),
            ascii_painter=kwargs.pop("ascii_painter", None)
        )

    def __init__(self, app, x: int, y: int, width: int, height: int,
                 dock: Dock, dimensions: DimensionsFlag = DimensionsFlag.Absolute,
                 borderless: bool = False, ascii_painter: AsciiPainter = None):
        self.canvas_width = width
        self.canvas_height = height
        border = (0 if borderless else 2)
        widget_width = width + border
        widget_height = height + border
        super().__init__(app=app, x=x, y=y, width=widget_width, height=widget_height, dock=dock,
                         dimensions=dimensions, borderless=borderless)
        self.title = 'Canvas'
        self.ascii_painter = ascii_painter
        self.cells = [[CanvasCell(' ', TerminalColor()) for cell in range(self.canvas_width)] for row in
                      range(self.canvas_height)]

    def draw(self):
        super().draw()
        border = 0 if self.borderless else 1
        y = self.last_dimensions.y + border
        x = self.last_dimensions.x + border
        offset_str = self.app.brush.str_right(x)
        for y_offset in range(self.canvas_height):
            self.app.brush.move_cursor(row=y + y_offset)

            row = self.cells[y_offset]
            line = offset_str
            for x_offset in range(self.canvas_width):
                line += self.app.brush.color(row[x_offset].color) + row[x_offset].value[0]
            line += self.app.brush.reset_color()
            self.app.brush.print(line, end='')

    def draw_cell(self, row: int, column: int):
        border = 0 if self.borderless else 1
        y = self.last_dimensions.y + border
        x = self.last_dimensions.x + border
        offset_str = self.app.brush.str_right(x + column)
        self.app.brush.move_cursor(row=y + row)
        cell = self.cells[row][column]
        line = offset_str + self.app.brush.color(cell.color) + cell.value + self.app.brush.reset_color()
        self.app.brush.print(line, end='')

    def handle(self, event):
        if isinstance(event, MouseEvent):
            if event.button in [event.button.LMB, event.button.RMB] and event.pressed:
                local_column, local_row = self.local_point(event.coordinates)
                if local_row is None or local_column is None:
                    return

                brush_color = self.ascii_painter.color.foreground if event.button == event.button.LMB else self.ascii_painter.color.background

                if local_row >= len(self.cells) or local_column >= len(self.cells[local_row]):
                    return

                self.cells[local_row][local_column].color.foreground = brush_color
                self.cells[local_row][local_column].color.background = brush_color

                self.draw_cell(local_row, local_column)


DEFAULT_HEIGHT = 10
DEFAULT_WIDTH = 32


def main(args):
    ascii_painter = AsciiPainter()

    ascii_painter.app = App()
    ascii_painter.app.color_mode()

    height = DEFAULT_HEIGHT
    width = DEFAULT_WIDTH

    if args.input_txt:
        # TODO
        # load file
        # while loading remember to find longest line
        # count of lines is height
        pass

    if args.size:
        try:
            w_x_h = args.size.split('x')
            if len(w_x_h) != 2:
                raise Exception('expected {int}x{int} string')
            width = int(w_x_h[0], 10)
            height = int(w_x_h[1], 10)
        except Exception as ex:
            print(ex, file=sys.stderr)
            return -1

    # TODO: Percent of window, fill
    pane = Pane(app=ascii_painter.app, x=0, y=0, height=100, width=100,
                dock=Dock.NONE, dimensions=DimensionsFlag.Relative,
                borderless=False)
    pane.title = 'ASCII Painter'

    toolbar_dock = Dock.TOP if args.toolbar_top else Dock.BOTTOM

    toolbar = Pane(app=ascii_painter.app, x=0, y=0, height=6, width=100,
                   dock=toolbar_dock,
                   dimensions=DimensionsFlag.RelativeWidth)

    row = -1
    col = -1
    widget = Colors8BitPalette(app=ascii_painter.app, x=col, y=row,
                               dock=Dock.RIGHT,
                               dimensions=DimensionsFlag.Absolute, ascii_painter=ascii_painter)
    toolbar.add_widget(widget)

    col += 17
    ascii_painter.brush_widget = BrushWidget(app=ascii_painter.app, x=col, y=row,
                                             dock=Dock.RIGHT,
                                             dimensions=DimensionsFlag.Absolute, ascii_painter=ascii_painter)

    toolbar.add_widget(ascii_painter.brush_widget)

    canvas = Canvas(app=ascii_painter.app, x=0, y=0, height=height, width=width,
                    dock=Dock.FILL,
                    dimensions=DimensionsFlag.Absolute,  # Fill fails atm
                    ascii_painter=ascii_painter)

    pane.add_widget(toolbar)
    pane.add_widget(canvas)

    ascii_painter.app.add_widget(pane)

    ascii_painter.app.run()
    return 0


def bind_brush(brush_widget, ascii_painter):
    ascii_painter.brush_widget = brush_widget


def main_json(args):
    toolbar_dock = Dock.TOP if args.toolbar_top else Dock.BOTTOM

    height = DEFAULT_HEIGHT
    width = DEFAULT_WIDTH

    if args.size:
        try:
            w_x_h = args.size.split('x')
            if len(w_x_h) != 2:
                raise Exception('expected {int}x{int} string')
            width = int(w_x_h[0], 10)
            height = int(w_x_h[1], 10)
        except Exception as ex:
            print(ex, file=sys.stderr)
            return -1

    ascii_painter = AsciiPainter()

    if args.input_txt:
        # TODO
        # load file
        # while loading remember to find longest line
        # count of lines is height
        pass

    ascii_painter.app = json_loader.app_from_json(Path(__file__).parents[0] / "ascii_painter.json", globals(), app_dict={
        "ascii_painter": ascii_painter,
        "toolbar_dock": toolbar_dock,
        "height": height,
        "width": width,
        "bind_brush_fun": bind_brush
    })

    ascii_painter.app.run()
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='enables debug log')
    parser.add_argument('--toolbar-top', action='store_true', help='toolbar would be on top, default is bottom')
    parser.add_argument('-s', '--size', type=str, default=None)
    parser.add_argument('--input-txt', type=str, default=None, help='txt file with ascii art, eg. jp2a output')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(
            handlers=[
                logging.handlers.RotatingFileHandler(
                    Path(__file__).stem + ".log", maxBytes=1024 * 1024 * 1024 * 10, backupCount=5
                )
            ],
            force=True,
            level=logging.DEBUG,
        )

    main_fun = main_json if args.json else main
    ret = main_fun(args)
    sys.exit(ret)
