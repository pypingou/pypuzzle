#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This program is a simple puzzle game where you have to order n elements
in n + 1 cells.
"""

import sys
import os
import random

try:
    import pygtk
    pygtk.require('2.0')
except ImportError, er:
    pass
try:
    import gtk
except ImportError, er:
    print('GTK Not Availible')
    sys.exit(1)

def _dialog(dialog):
    """ Display a dialog window.
    :arg dialog,
    """
    dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
    dialog.set_modal(True)
    dialog.set_keep_above(True)
    dialog.show_all()
    result = dialog.run()
    dialog.hide()
    return result

def are_in_same_row(cell, free_cell):
    """ Check if the given cell is in the same row than the free_cell.
    :arg cell, the coordinate of the cell in the table.
    :arg free_cell, the coordinate of the free cell in the table.
    """
    ycell = list(cell)[0][1]
    yfreecell = list(free_cell)[0][1]

    return ycell == yfreecell


def are_in_same_column(cell, free_cell):
    """ Check if the given cell is in the same column than the free_cell.
    :arg cell, the coordinate of the cell in the table.
    :arg free_cell, the coordinate of the free cell in the table.
    """
    xcell = list(cell)[0][0]
    xfreecell = list(free_cell)[0][0]

    return xcell == xfreecell


def check_results(table):
    """ Check if the table is in the right order.
    :arg table, the GtkTable to browse which is the board of the game.
    """
    rows = {}
    for child in table.get_children():
        (col, row) = table.child_get(child, 'left-attach', 'top-attach')
        if row in rows.keys():
            rows[row][col] = child.get_label()
        else:
            rows[row] = ["", "", "", ""]
            rows[row][col] = child.get_label()

    return rows[0] == ['1', '2', '3', '4'] \
        and rows[1] == ['5', '6', '7', '8'] \
        and rows[2] == ['9', '10', '11', '12'] \
        and rows[3] == ['13', '14', '15', '']


def exit_game(widget=None):
    """ Quit the application.
    :karg widget, the widget activated to quit the game.
    """
    print 'quitting...'
    sys.exit(0)


def get_free_cells(table):
    """ Returns the cells which are free in the table.
    :arg table a GtkTable used as board for the game.
    """
    free_cells = set([(x, y) for x in range(table.props.n_columns)
                            for y in range(table.props.n_rows)])

    def func(child):
        """ Remove used cells from the list of free cells """
        (left, top) = table.child_get(child, 'left-attach', 'top-attach')
        free_cells.difference_update(set([(left, top)]))

    table.foreach(func)

    return free_cells


def locate_cell(table, cell):
    """ Find the location of the given cell in the table.
    :arg cell a Widget, here a GtkButton to locate in the table.
    :arg table a GtkTable used as board for the game.
    """
    coordinate = set()

    def func(child, cell):
        """ Add cell coordinate to the set of coordinates based on the
        label of the widget sent.
        :arg child, widget present in the table.
        :arg cell, cell to identify in the widget list.
        """
        if child.get_label() == cell.get_label():
            (left, top) = table.child_get(child, 'left-attach',
                                                    'top-attach')
            coord = set([(left, top)])
            coordinate.update(coord)

    table.foreach(func, cell)

    return coordinate


def move_column(cell, free_cell, table):
    """ Move cells in a column to fill the empty cell up to the cell
    activated.
    Returns, the number of cells moved.
    :arg cell, a Widget to move in the table.
    :arg free_cell, the coordinate to which move the cell.
    :arg table, the table in which the moving is made.
    """
    refr = table.child_get(cell, 'top-attach')[0]
    (col, row) = list(free_cell)[0]
    down = True
    if int(refr) > int(row):
        down = False  # we go up

    cells = []
    for cell in table.get_children():
        (ccel, rcel) = table.child_get(cell, 'left-attach', 'top-attach')
        if ccel == col:  # cell in the same column
            if down and int(rcel) >= int(refr) and int(rcel) < int(row):
                # cell is or is under the one activated
                cells.append(cell)
            elif not down and int(rcel) <= int(refr) and int(rcel) > int(row):
                cells.append(cell)

    for cell in cells:
        (ccel, rcel) = table.child_get(cell, 'left-attach', 'top-attach')
        if down:
            table.child_set(cell,   'left-attach', ccel,
                                'right-attach', ccel + 1,
                                'top-attach', rcel + 1,
                                'bottom-attach', rcel + 2)
        else:
            table.child_set(cell,   'left-attach', ccel,
                                'right-attach', ccel + 1,
                                'top-attach', rcel - 1,
                                'bottom-attach', rcel)
    return len(cells)


def move_row(cell, free_cell, table):
    """ Move cells in a row to fill the empty cell up to the cell
    activated.
    Returns, the number of cells moved.
    :arg cell, a Widget to move in the table.
    :arg free_cell, the coordinate to which move the cell.
    :arg table, the table in which the moving is made.
    """
    refc = table.child_get(cell, 'left-attach')[0]
    (col, row) = list(free_cell)[0]
    right = True
    if int(refc) > int(col):
        right = False  # we go to the left

    cells = []
    for cell in table.get_children():
        (ccel, rcel) = table.child_get(cell, 'left-attach', 'top-attach')
        if rcel == row:  # cell in the same row
            if right and int(ccel) >= int(refc) and int(ccel) < int(col):
                # cell is or is on the right of the one activated
                cells.append(cell)
            elif not right and int(ccel) <= int(refc) and int(ccel) > int(col):
                cells.append(cell)

    for cell in cells:
        (ccel, rcel) = table.child_get(cell, 'left-attach', 'top-attach')
        if right:
            table.child_set(cell,   'left-attach', ccel + 1,
                                'right-attach', ccel + 2,
                                'top-attach', rcel,
                                'bottom-attach', rcel + 1)
        else:
            table.child_set(cell,   'left-attach', ccel - 1,
                                'right-attach', ccel,
                                'top-attach', rcel,
                                'bottom-attach', rcel + 1)
    return len(cells)


class PuzzleGui:
    """ Set up the board for the game.
    It is a simple square divided in n elements and in which n-1 element
    are present.
    The goal is to order the element in numerical order.
    """

    def __init__(self):
        """ Load the board game and display it.
        """

        self.builder = gtk.Builder()
        self.builder.add_from_file(os.path.dirname(
            os.path.realpath(__file__)) + '/puzzle.ui')
        self.mainwindow = self.builder.get_object('mainwindow')

        dic = {
            'on_windowMain_destroy': exit_game,
            'gtk_main_quit': exit_game,
            'on_buttonQuit_clicked': exit_game,
            'action_button': self.action_button,
            'new_game': self.new_game,
        }

        self.builder.connect_signals(dic)

        stbar = self.builder.get_object('statusbar')
        stbar.push(1, "Start puzzle")
        self.cnt = 0

        table = self.builder.get_object('grid')
        table.set_size_request(400, 400)

        self.mainwindow.show()

    def action_button(self, widget):
        """ Move the button in the table.
        According to the button clicked, the button is moved to the free
        cell next to it.
        :arg widget, the button pressed.
        """
        table = self.builder.get_object('grid')
        free_cell = get_free_cells(table)
        cell = locate_cell(table, widget)
        if are_in_same_row(cell, free_cell):
            self.cnt += move_row(widget, free_cell, table)
        elif are_in_same_column(cell, free_cell):
            self.cnt += move_column(widget, free_cell, table)

        stbar = self.builder.get_object('statusbar')
        stbar.push(1, "%s moves" % self.cnt)
        if check_results(table):
            dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_INFO)
            dialog.set_markup("<b>" + "You won!!" + "</b>")
            dialog.format_secondary_markup(
                    "Do you want to start a new game?")
            dialog.add_buttons(gtk.STOCK_OK, gtk.RESPONSE_YES,
                                gtk.STOCK_CANCEL, gtk.RESPONSE_NO)
            result = _dialog(dialog)
            if result == gtk.RESPONSE_YES:
                self.new_game()

    def new_game(self, widget=None):
        """ Move the button in the table """
        self.cnt = 0
        stbar = self.builder.get_object('statusbar')
        stbar.push(1, "%s moves" % self.cnt)
        table = self.builder.get_object('grid')
        free_cells = [(x, y) for x in range(table.props.n_columns)
                            for y in range(table.props.n_rows)]

        widgets = []
        for child in table.get_children():
            widgets.append(child)

        while widgets:
            pos = random.randint(0, len(widgets) - 1)
            widget = widgets[pos]
            widgets.remove(widget)
            pos = random.randint(0, len(free_cells) - 1)
            location = free_cells[pos]
            free_cells.remove(location)
            table.child_set(widget, 'left-attach', location[0],
                          'right-attach', location[0] + 1,
                          'top-attach', location[1],
                          'bottom-attach', location[1] + 1)

if __name__ == '__main__':
    PuzzleGui()
    gtk.main()
