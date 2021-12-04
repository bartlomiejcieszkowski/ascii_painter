#!/usr/bin/env python3
from typing import Tuple

import ascii_painter_engine as ape

import argparse

print('success!')


class AsciiPainter:
    def __init__(self):
        self.color = ape.ConsoleColor(ape.Color(15, ape.ColorBits.Bit8), ape.Color(1, ape.ColorBits.Bit8))
        self.brush_widget = None
        self.console_view = None

    def invalidate(self):
        self.pane


class Colors8BitPalette(ape.ConsoleWidgets.BorderWidget):
    def __init__(self, console_view, x: int, y: int,
                 alignment: ape.Alignment, dimensions: ape.DimensionsFlag = ape.DimensionsFlag.Absolute,
                 borderless: bool = False, ascii_painter: AsciiPainter = None):
        border = (0 if borderless else 2)
        width = 8 * 2 + border
        height = 2 + border
        super().__init__(console_view=console_view, x=x, y=y, width=width, height=height, alignment=alignment,
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
        offset_str = self.console_view.brush.MoveRight(offset_cols)
        color = ape.Color(0, ape.ColorBits.Bit8)
        for h in range(start, end):
            self.console_view.brush.MoveCursor(row=offset_rows + h)
            line = offset_str
            for i in range(h * 8, (h + 1) * 8):
                color.color = i
                line += self.console_view.brush.BgColor(color=color) + '  '
            self.console_view.brush.print(line + self.console_view.brush.ResetColor(), end='')

    def coord_to_color(self, coords: Tuple[int, int]):
        border = 0 if self.borderless else 1
        offset_rows = self.last_dimensions.row + border
        offset_cols = self.last_dimensions.column + border
        width = self.last_dimensions.width - (border * 2)
        height = self.last_dimensions.height - (border * 2)

        local_row = coords[0] - offset_rows
        local_column = coords[1] - offset_cols

        # raise Exception(f'w: {width} h: {height} col: {local_column} row: {local_row}')
        if local_column < 0 or local_column >= width or local_row < 0 or local_row >= height:
            return None

        color_idx = local_row * 8 + (local_column // 2)
        return ape.Color(color_idx, ape.ColorBits.Bit8)

    def handle(self, event: ape.Event, coords: Tuple[int, int]):
        # TODO: properly pass whole event
        color = self.coord_to_color(coords)
        if color is None:
            return
        # raise Exception(color)
        self.ascii_painter.color.fgcolor = color
        # self.ascii_painter.console_view.requires_draw = True
        self.ascii_painter.brush_widget.draw()


class BrushWidget(ape.ConsoleWidgets.BorderWidget):
    def __init__(self, console_view, x: int, y: int,
                 alignment: ape.Alignment, dimensions: ape.DimensionsFlag = ape.DimensionsFlag.Absolute,
                 borderless: bool = False, ascii_painter: AsciiPainter = None):
        border = (0 if borderless else 2)
        width = 3 * 2 + border
        height = 2 + border
        super().__init__(console_view=console_view, x=x, y=y, width=width, height=height, alignment=alignment,
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
        offset_str = self.console_view.brush.MoveRight(offset_cols)
        # fgcolor

        self.console_view.brush.MoveCursor(row=offset_rows)
        self.console_view.brush.print(offset_str + self.console_view.brush.BgColor(
            color=self.ascii_painter.color.fgcolor) + ' ' * width + self.console_view.brush.ResetColor(), end='')

        # bgcolor
        self.console_view.brush.MoveCursor(row=offset_rows + 1)
        self.console_view.brush.print(offset_str + self.console_view.brush.BgColor(
            color=self.ascii_painter.color.bgcolor) + ' ' * width + self.console_view.brush.ResetColor(), end='')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='enables debug log')
    parser.add_argument('--toolbar-top', action='store_true', help='toolbar would be on top, default is bottom')

    args = parser.parse_args()



    ascii_painter = AsciiPainter()

    if args.debug:
        ape.log.log_file('ascii_painter')

    ascii_painter.console_view = ape.ConsoleView(log=ape.log.log)
    ascii_painter.console_view.color_mode()

    # TODO: Percent of window, fill
    pane = ape.ConsoleWidgets.Pane(console_view=ascii_painter.console_view, x=0, y=0, height=100, width=100,
                                   alignment=ape.Alignment.LeftTop, dimensions=ape.DimensionsFlag.Relative,
                                   borderless=False)
    pane.title = 'ASCII Painter'

    toolbar_alignment = ape.Alignment.LeftTop if args.toolbar_top else ape.Alignment.LeftBottom

    toolbar = ape.ConsoleWidgets.Pane(console_view=ascii_painter.console_view, x=0, y=0, height=4, width=100,
                                            alignment=toolbar_alignment,
                                            dimensions=ape.DimensionsFlag.RelativeWidth)

    row = -1
    col = -1
    widget = Colors8BitPalette(console_view=ascii_painter.console_view, x=col, y=row,
                               alignment=ape.Alignment.RightBottom,
                               dimensions=ape.DimensionsFlag.Absolute, ascii_painter=ascii_painter)
    toolbar.add_widget(widget)

    col += 17
    ascii_painter.brush_widget = BrushWidget(console_view=ascii_painter.console_view, x=col, y=row,
                                             alignment=ape.Alignment.RightBottom,
                                             dimensions=ape.DimensionsFlag.Absolute, ascii_painter=ascii_painter)

    toolbar.add_widget(ascii_painter.brush_widget)

    pane.add_widget(toolbar)

    ascii_painter.console_view.add_widget(pane)

    ascii_painter.console_view.loop(True)


if __name__ == '__main__':
    main()
