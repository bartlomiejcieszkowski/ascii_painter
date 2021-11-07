#!/usr/bin/env python3

import ascii_painter_engine as ape

print('success!')


class Colors8BitPalette(ape.ConsoleWidgets.BorderWidget):
    def __init__(self, console_view, x: int, y: int,
                 alignment: ape.Alignment, dimensions: ape.DimensionsFlag = ape.DimensionsFlag.Absolute, borderless: bool = False):
        border = (0 if borderless else 2)
        width = 8 * 2 + border
        height = 2 + border
        super().__init__(console_view=console_view, x=x, y=y, width=width, height=height, alignment=alignment,
                         dimensions=dimensions, borderless=borderless)
        self.title = 'Colors'

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
        for h in range(start, end):
            self.console_view.brush.MoveCursor(row=offset_rows + h)
            line = offset_str
            for i in range(h*8, (h+1)*8):
                line += self.console_view.brush.BgColor(color=i, bits=ape.Brush.ColorBits.Bit8) + '  '
            self.console_view.brush.print(line + self.console_view.brush.ResetColor(), end='')


def main():
    console_view = ape.ConsoleView(debug=True)
    console_view.color_mode()

    # TODO: Percent of window, fill
    pane = ape.ConsoleWidgets.Pane(console_view=console_view, x=0, y=0, height=100, width=100,
                                   alignment=ape.Alignment.LeftTop, dimensions=ape.DimensionsFlag.Relative,
                                   borderless=False)
    pane.title = 'ASCII Painter'

    color_pane = Colors8BitPalette(console_view=console_view, x=0, y=0,
                                   alignment=ape.Alignment.RightBottom,
                                   dimensions=ape.DimensionsFlag.Absolute)
    pane.add_widget(color_pane)

    console_view.add_widget(pane)

    console_view.loop(True)


if __name__ == '__main__':
    main()
