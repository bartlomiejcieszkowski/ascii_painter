#!/usr/bin/env python3

import ascii_painter_engine as ape

print('success!')


def main():
    console_view = ape.ConsoleView(debug=True)
    console_view.color_mode()

    # TODO: Percent of window, fill
    pane = ape.ConsoleWidgets.Pane(console_view=console_view, x=0, y=1, height=100, width=100,
                                   alignment=ape.ConsoleWidgetAlignment.LEFT_TOP, percent=True)
    pane.title = 'ASCII Painter'

    console_view.add_widget(pane)

    console_view.loop(True)


if __name__ == '__main__':
    main()
