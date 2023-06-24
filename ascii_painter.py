#!/usr/bin/env python3
import sys
from typing import Tuple

import ascii_painter_engine as ape
from ascii_painter_engine import helper
from ascii_painter_engine.widget import BorderWidget, Pane
from ascii_painter_engine import logger

import argparse

print('success!')


class AsciiPainter:
    def __init__(self):
        self.color = ape.ConsoleColor(ape.Color(15, ape.ColorBits.Bit8), ape.Color(1, ape.ColorBits.Bit8))
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
            alignment=kwargs.pop("alignment", None),
            dimensions=kwargs.pop("dimensions", "Absolute"),
            borderless=kwargs.pop("borderless", False),
            ascii_painter=kwargs.pop("ascii_painter", None)
        )

    def __init__(self, app, x: int, y: int,
                 alignment: ape.Alignment, dimensions: ape.DimensionsFlag = ape.DimensionsFlag.Absolute,
                 borderless: bool = False, ascii_painter: AsciiPainter = None):
        border = (0 if borderless else 2)
        width = 8 * 2 + border
        height = 2 + border
        super().__init__(app=app, x=x, y=y, width=width, height=height, alignment=alignment,
                         dimensions=dimensions, borderless=borderless)
        self.title = 'Colors'
        self.ascii_painter = ascii_painter

    def draw(self):
        super().draw()
        border = 0 if self.borderless else 1
        offset_rows = self.last_dimensions.row + border
        offset_cols = self.last_dimensions.column + border
        width = self.last_dimensions.width - (border * 2)
        height = self.last_dimensions.height - (border * 2)
        start = 0
        end = height
        offset_str = self.app.brush.MoveRight(offset_cols)
        color = ape.Color(0, ape.ColorBits.Bit8)
        for h in range(start, end):
            self.app.brush.MoveCursor(row=offset_rows + h)
            line = offset_str
            for i in range(h * 8, (h + 1) * 8):
                color.color = i
                line += self.app.brush.BgColor(color=color) + '  '
            self.app.brush.print(line + self.app.brush.ResetColor(), end='')

    def point_to_color(self, point: Tuple[int, int]):
        local_column, local_row = self.local_point(point)

        if local_row is None or local_column is None:
            return None

        color_idx = local_row * 8 + (local_column // 2)
        return ape.Color(color_idx, ape.ColorBits.Bit8)

    def handle(self, event):
        if isinstance(event, ape.MouseEvent):
            if event.button in [event.button.LMB, event.button.RMB] and not event.pressed:
                color = self.point_to_color(event.coordinates)
                if color is None:
                    return
                # raise Exception(color)
                if event.button == event.button.LMB:
                    self.ascii_painter.color.fgcolor = color
                elif event.button == event.button.RMB:
                    self.ascii_painter.color.bgcolor = color
                # self.ascii_painter.app.requires_draw = True
                self.ascii_painter.brush_widget.draw()


class BrushWidget(BorderWidget):
    @classmethod
    def from_dict(cls, **kwargs):
        return cls(
            app=kwargs.pop("app"),
            x=kwargs.pop("x"),
            y=kwargs.pop("y"),
            alignment=kwargs.pop("alignment", None),
            dimensions=kwargs.pop("dimensions", "Absolute"),
            borderless=kwargs.pop("borderless", False),
            ascii_painter=kwargs.pop("ascii_painter", None)
        )

    def __init__(self, app, x: int, y: int,
                 alignment: ape.Alignment, dimensions: ape.DimensionsFlag = ape.DimensionsFlag.Absolute,
                 borderless: bool = False, ascii_painter: AsciiPainter = None):
        border = (0 if borderless else 2)
        width = 3 * 2 + border
        height = 2 + border
        super().__init__(app=app, x=x, y=y, width=width, height=height, alignment=alignment,
                         dimensions=dimensions, borderless=borderless)
        self.title = 'Brush'
        self.ascii_painter = ascii_painter

    def draw(self):
        super().draw()
        border = 0 if self.borderless else 1
        offset_rows = self.last_dimensions.row + border
        offset_cols = self.last_dimensions.column + border
        width = self.last_dimensions.width - (border * 2)
        height = self.last_dimensions.height - (border * 2)
        start = 0
        end = height
        offset_str = self.app.brush.MoveRight(offset_cols)
        # fgcolor

        self.app.brush.MoveCursor(row=offset_rows)
        self.app.brush.print(offset_str + self.app.brush.BgColor(
            color=self.ascii_painter.color.fgcolor) + ' ' * width + self.app.brush.ResetColor(), end='')

        # bgcolor
        self.app.brush.MoveCursor(row=offset_rows + 1)
        self.app.brush.print(offset_str + self.app.brush.BgColor(
            color=self.ascii_painter.color.bgcolor) + ' ' * width + self.app.brush.ResetColor(), end='')


class CanvasCell:
    def __init__(self, value, color: ape.ConsoleColor):
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
            alignment=kwargs.pop("alignment", None),
            dimensions=kwargs.pop("dimensions", "Absolute"),
            borderless=kwargs.pop("borderless", False),
            ascii_painter=kwargs.pop("ascii_painter", None)
        )

    def __init__(self, app, x: int, y: int, width: int, height: int,
                 alignment: ape.Alignment, dimensions: ape.DimensionsFlag = ape.DimensionsFlag.Absolute,
                 borderless: bool = False, ascii_painter: AsciiPainter = None):
        self.canvas_width = width
        self.canvas_height = height
        border = (0 if borderless else 2)
        widget_width = width + border
        widget_height = height + border
        super().__init__(app=app, x=x, y=y, width=widget_width, height=widget_height, alignment=alignment,
                         dimensions=dimensions, borderless=borderless)
        self.title = 'Canvas'
        self.ascii_painter = ascii_painter
        self.cells = [[CanvasCell(' ', ape.ConsoleColor()) for cell in range(self.canvas_width)] for row in
                      range(self.canvas_height)]

    def draw(self):
        super().draw()
        border = 0 if self.borderless else 1
        offset_rows = self.last_dimensions.row + border
        offset_cols = self.last_dimensions.column + border
        offset_str = self.app.brush.MoveRight(offset_cols)
        for y in range(self.canvas_height):
            self.app.brush.MoveCursor(row=offset_rows + y)

            row = self.cells[y]
            line = offset_str
            for x in range(self.canvas_width):
                line += self.app.brush.FgBgColor(row[x].color) + row[x].value[0]
            line += self.app.brush.ResetColor()
            self.app.brush.print(line, end='')

    def draw_cell(self, row: int, column: int):
        border = 0 if self.borderless else 1
        offset_rows = self.last_dimensions.row + border
        offset_cols = self.last_dimensions.column + border
        offset_str = self.app.brush.MoveRight(offset_cols + column)
        self.app.brush.MoveCursor(row=offset_rows + row)
        cell = self.cells[row][column]
        line = offset_str + self.app.brush.FgBgColor(cell.color) + cell.value + self.app.brush.ResetColor()
        self.app.brush.print(line, end='')

    def handle(self, event):
        if isinstance(event, ape.MouseEvent):
            if event.button in [event.button.LMB, event.button.RMB] and event.pressed:
                local_column, local_row = self.local_point(event.coordinates)
                if local_row is None or local_column is None:
                    return

                brush_color = self.ascii_painter.color.fgcolor if event.button == event.button.LMB else self.ascii_painter.color.bgcolor

                self.cells[local_row][local_column].color.fgcolor = brush_color
                self.cells[local_row][local_column].color.bgcolor = brush_color

                self.draw_cell(local_row, local_column)


DEFAULT_HEIGHT = 10
DEFAULT_WIDTH = 32


def main(args):
    ascii_painter = AsciiPainter()

    if args.debug:
        ape.logger.log_file('ascii_painter')

    ascii_painter.app = ape.App(log=ape.logger.log)
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
                alignment=ape.Alignment.LeftTop, dimensions=ape.DimensionsFlag.Relative,
                borderless=False)
    pane.title = 'ASCII Painter'

    toolbar_alignment = ape.Alignment.LeftTop if args.toolbar_top else ape.Alignment.LeftBottom

    toolbar = Pane(app=ascii_painter.app, x=0, y=0, height=4, width=100,
                   alignment=toolbar_alignment,
                   dimensions=ape.DimensionsFlag.RelativeWidth)

    row = -1
    col = -1
    widget = Colors8BitPalette(app=ascii_painter.app, x=col, y=row,
                               alignment=ape.Alignment.RightBottom,
                               dimensions=ape.DimensionsFlag.Absolute, ascii_painter=ascii_painter)
    toolbar.add_widget(widget)

    col += 17
    ascii_painter.brush_widget = BrushWidget(app=ascii_painter.app, x=col, y=row,
                                             alignment=ape.Alignment.RightBottom,
                                             dimensions=ape.DimensionsFlag.Absolute, ascii_painter=ascii_painter)

    toolbar.add_widget(ascii_painter.brush_widget)

    canvas = Canvas(app=ascii_painter.app, x=0, y=0, height=height, width=width,
                    alignment=ape.Alignment.LeftTop,
                    dimensions=ape.DimensionsFlag.Absolute,  # Fill fails atm
                    ascii_painter=ascii_painter)

    pane.add_widget(toolbar)
    pane.add_widget(canvas)

    ascii_painter.app.add_widget(pane)

    ascii_painter.app.run()
    return 0


def bind_brush(brush_widget, ascii_painter):
    ascii_painter.brush_widget = brush_widget


def main_json(args):
    toolbar_alignment = ape.Alignment.LeftTop if args.toolbar_top else ape.Alignment.LeftBottom

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

    helper.register_app_dict("main", {
        "ascii_painter": ascii_painter,
        "toolbar_alignment": toolbar_alignment,
        "height": height,
        "width": width,
        "bind_brush_fun": bind_brush
    })

    if args.debug:
        ape.logger.log_file('ascii_painter')

    ascii_painter.app = helper.app_from_json("ascii_painter.json", globals())

    ascii_painter.app.log = ape.logger.log
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

    main_fun = main_json if args.json else main
    ret = main_fun(args)
    sys.exit(ret)
