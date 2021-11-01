#!/usr/bin/env python3

from ascii_painter_engine.main import ConsoleWidgetAlignment, ConsoleView, ConsoleWidgets

print('success!')

def main():
    console_view = ConsoleView(debug=True)
    console_view.color_mode()

    # TODO: Percent of window, fill
    pane = ConsoleWidgets.Pane(console_view=console_view, x=1, y=1, height=100, width=100,
                                 alignment=ConsoleWidgetAlignment.LEFT_TOP, percent=True)
    pane.title = 'ASCII Painter'

    console_view.add_widget(pane)

    console_view.loop(True)

if __name__ == '__main__':
    main()