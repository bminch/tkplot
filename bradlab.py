#
## Copyright (c) 2018-2020, Bradley A. Minch
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met: 
## 
##     1. Redistributions of source code must retain the above copyright 
##        notice, this list of conditions and the following disclaimer. 
##     2. Redistributions in binary form must reproduce the above copyright 
##        notice, this list of conditions and the following disclaimer in the 
##        documentation and/or other materials provided with the distribution. 
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
## IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
## ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
## LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
## CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
## SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
## INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
## CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
## ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
## POSSIBILITY OF SUCH DAMAGE.
#

import tkinter as tk
import tkplot, pickle, codecs, sys
import string
from numpy import *

sys.path[0] = ''

__root__ = tk.Tk()
__root__.withdraw()
__fig__ = 0
__figs__ = {}
__plot__ = None

class fig:
    
    def __init__(self, title, **kwargs):
        global __root__
        global __plot__
        self.width = float(kwargs.get('width', 560.))
        self.height = float(kwargs.get('height', 420.))
        self.rows = kwargs.get('rows', 1)
        self.cols = kwargs.get('cols', 1)
        self.row = kwargs.get('row', 0)
        self.col = kwargs.get('col', 0)
        self.top = tk.Toplevel(__root__)
        self.top.title(title)
        self.top.protocol('WM_DELETE_WINDOW', self.close)
        subplot_width = round(self.width / self.cols)
        subplot_height = round(self.height / self.rows)
        self.plots = []
        for row in range(self.rows):
            row_frame = tk.Frame(self.top)
            plot_row = []
            for col in range(self.cols):
                plot_frame = tk.Frame(row_frame)
                plot = tkplot.tkplot(parent = plot_frame, width = subplot_width, height = subplot_height)
                plot.yaxes['right'] = plot.y_axis(name = 'right')
                plot.right_yaxis = 'right'
                plot.bindings()
                plot_row.append(plot)
                plot_frame.pack(side = tk.LEFT, fill = 'both', expand = 'yes')
            self.plots.append(plot_row)
            row_frame.pack(side = tk.TOP, fill = 'both', expand = 'yes')
        self.top.lift()
        __plot__ = self.plots[self.row][self.col]

    def close(self):
        global __plot__
        title = self.top.title()
        for row in range(self.rows):
            for col in range(self.cols):
                if __plot__ == self.plots[row][col]:
                    __plot__ = None
        self.top.destroy()
        del(__figs__[title])

def figure(*args, **kwargs):
    '''
    figure([<fig>], [width = <width>], [height = <height>], 
               [rows = <rows>], [cols = <cols>], 
               [row = <row>], [col = <col>])
    
    Create a new figure window or select an existing figure window, raising 
    it to the top of the stacking order.  If <fig> is specified, it can either 
    be an integer or a string.  If the figure window specified by <fig> exists, 
    it is raised to the top of the stacking order and the subplot specified by 
    <row> and <col> is selected.  If the figure window specified by <fig> does 
    not exist, a new figure window is created with a <rows> x <cols> matrix of 
    subplots.  The subplot specified by <row> and <col> is selected.  The 
    optional parameters are given below (default values are provided in square 
    brackets):
    
         width [540.]: Width in pixels to be distributed evenly among the 
                           number of subplot columns specified by <cols>.
        height [420.]: Height in pixels to be distributed evenly among the 
                           number of subplot rows specidied by <rows>.
             rows [1]: Number of subplot rows in the figure window.
             cols [1]: Number of subplot columns in the figure window.
              row [0]: Row index of the selected subplot (the first row 
                           is numbered starting at zero).
              col [0]: Column index of the selected subplot (the first 
                           column is numbered starting at zero).
    '''
    global __figs__
    global __plot__
    global __fig__
    rows = kwargs.get('rows')
    cols = kwargs.get('cols')
    row = kwargs.get('row')
    col = kwargs.get('col')
    if len(args) == 0:
        __fig__ += 1
        title = 'Figure {0!s}'.format(__fig__)
    elif type(args[0]) is int:
        title = 'Figure {0!s}'.format(args[0])
    elif type(args[0]) is str:
        title = args[0]
    else:
        raise TypeError('if specified, figure identifier must be an integer or a string')
    if title in __figs__.keys():
        __figs__[title].top.lift()
        if (rows != None) or (cols != None):
            raise ValueError('the number of subplot rows and columns cannot be changed for an existing figure')
        if row != None:
            if (row >= 0) and (row < __figs__[title].rows):
                __figs__[title].row = row
            else:
                raise IndexError('the specified subplot row is out of range for the selected figure')
        if col != None:
            if (col >= 0) and (col < __figs__[title].cols):
                __figs__[title].col = col
            else:
                raise IndexError('the specified subplot column is out of range for the selected figure')
        __plot__ = __figs__[title].plots[__figs__[title].row][__figs__[title].col]
    else:
        if rows == None:
            rows = 1
        if rows < 1:
            raise ValueError('if specified, the number of subplot rows must be one or greater')
        if row != None:
            if (row < 0) or (row >= rows):
                raise IndexError('the specified subplot row is out of range')
        if cols == None:
            cols = 1
        if cols < 1:
            raise ValueError('if specified, the number of subplot columns must be one or greater')
        if col != None:
            if (col < 0) or (col >= cols):
                raise IndexError('the specified subplot column is out of range')
        __figs__[title] = fig(title, **kwargs)

def select_plot():
    global __root__
    global __figs__
    global __plot__
    if len(__figs__.keys()) == 0:
        figure()
    else:
        stackingorder = __root__.tk.eval('wm stackorder ' + str(__root__))
        figs = stackingorder.split(' ')
        for title in __figs__.keys():
            if str(__figs__[title].top) == figs[-1]:
                __figs__[title].top.lift()
                __plot__ = __figs__[title].plots[__figs__[title].row][__figs__[title].col]

def configure(**kwargs):
    '''
    configure([<parameter1> = <value1>, <parameter2> = <value2>, ...])

    Configure all of the plots in the currently selected figure.  The 
    parameters can be any of the following (default values are shown in 
    square brackets):

               marker_radius [4.0]: Radius in pixels of the pointmarkers.
           marker_lineweight [0.5]: Line weight in pixels of the 
                                        pointmarkers.
            curve_lineweight [1.0]: Line weight in pixels of curves.
                 tick_length [6.0]: Length in pixels of major ticks (minor 
                                        ticks are half the length of 
                                        major ticks).
             tick_lineweight [0.5]: Line weight in pixels of ticks and grid 
                                        lines.
            background ['#CDCDCD']: Background color of the plot.
       axes_background ['#FFFFFF']: Background color of the axes.
            axes_color ['#000000']: Color of the axes frame, ticks, tick 
                                        labels, axes labels, and grid lines.
             axes_lineweight [1.0]: Line weight in pixels of the axes frame.
                    baseline [0.6]: Relative position of the text baseline 
                                        from the top of the bounding box
                                        for SVG output. 
                     fontsize [12]: Font size for tick labels and axes 
                                        labels (must be an integer).
                font ['Helvetica']: Font for tick labels and axes labels.
    '''
    global __figs__
    global __plot__
    if __plot__ == None:
        select_plot()
    title = __plot__.root.winfo_toplevel().title()
    fig = __figs__[title]
    for row in range(fig.rows):
        for col in range(fig.cols):
            fig.plots[row][col].configure(**kwargs)

def config_plot(**kwargs):
    '''
    config_plot([<parameter1> = <value1>, <parameter2> = <value2>, ...])

    Configure the currently selected plot.  The parameters can be any of the 
    following (default values are shown in square brackets):

               marker_radius [4.0]: Radius in pixels of the pointmarkers.
           marker_lineweight [0.5]: Line weight in pixels of the 
                                        pointmarkers.
            curve_lineweight [1.0]: Line weight in pixels of curves.
                 tick_length [6.0]: Length in pixels of major ticks (minor 
                                        ticks are half the length of 
                                        major ticks).
             tick_lineweight [0.5]: Line weight in pixels of ticks and grid 
                                        lines.
            background ['#CDCDCD']: Background color of the plot.
       axes_background ['#FFFFFF']: Background color of the axes.
            axes_color ['#000000']: Color of the axes frame, ticks, tick 
                                        labels, axes labels, and grid lines.
             axes_lineweight [1.0]: Line weight in pixels of the axes frame.
                    baseline [0.6]: Relative position of the text baseline 
                                        from the top of the bounding box
                                        for SVG output. 
                     fontsize [12]: Font size for tick labels and axes 
                                        labels (must be an integer).
                font ['Helvetica']: Font for tick labels and axes labels.
    '''
    global __plot__
    if __plot__ == None:
        select_plot()
    __plot__.configure(**kwargs)

def clear(**kwargs):
    '''
    clear([yaxis = 'left'|'right'|'all'])
    
    Clear the curves associated with the specified y axis or axes of the 
    currently selected plot.  If yaxis is not specified, the curves associated 
    with both y axes are cleared.
    '''
    if __plot__ == None:
        select_plot()
    __plot__.clear_plot(**kwargs)

def draw_now():
    '''
    Force the currently selected plot to update.
    '''
    if __plot__ == None:
        select_plot()
    __plot__.draw_now()

def plot(*args, **kwargs):
    '''
    plot(x, y, [style], [yaxis = 'left'|'right'], [hold = 'on'|'off'])
    
    Plot one or more curves on the currently selected plot on linear axes 
    associated with the specified y axis.  If yaxis is not specified, the curves 
    are plotted on the left y axis.  If the hold argument is specified as 'on', 
    any previously plotted curves are retained.  By default old curves are not 
    retained.
    
    The x and y arguments must either be vectors or lists of vectors.  If x is 
    a vector and y is a list of vectors, then each of the y vectors is plotted 
    against the one x vector.  If x and y are both lists of vectors, then each 
    y vector is plotted against the corresponding x vector.  If x is given as 
    a list of vectors, then y must also be a list of vectors.
    
    The optional style argument can be a string or a list of strings that 
    specify the style of the curves to be plotted.  If a single string is 
    supplied, then it is applied to all curves.  If a list of strings is 
    supplied, then there must be one for each curve.  A style string generally 
    specifies a point marker color, a point marker, a line color, and a line 
    style (in that order) using characters from the following three lists:
    
         b     blue            .     point                  -     solid
         g     green           o     circle                 :     dotted
         r     red             x     ex                     -.    dashdot
         c     cyan            +     plus                   -:    dashdotdot
         m     magenta         *     star                   --    dashed
         y     yellow          s     square               (none)  no line
         k     black           d     diamond
         w     white           v     triangle (down)
                               ^     triangle (up)
                               <     triangle (left)
                               >     triangle (right)
                               p     pentagram
                               h     hexagram
                             (none)  no point marker
    
    If a color is not specified for a point marker or for a curve, then a 
    default color is assigned by cycling through the first six colors in the 
    list in the order shown.  If no point marker is specified and no line 
    style is specified, then by default the corresponding curve is plotted 
    with points and solid lines.
    '''
    if __plot__ == None:
        select_plot()
    __plot__.plot(*args, **kwargs)

def semilogx(*args, **kwargs):
    '''
    semilogx(x, y, [style], [yaxis = 'left'|'right'], [hold = 'on'|'off'])
    
    Plot one or more curves on the currently selected plot on semilogartihmic 
    axes (x-axis logarithmic) associated with the specified y axis.  If yaxis 
    is not specified, the curves are plotted on the left y axis.  If the hold 
    argument is specified as 'on', any previously plotted curves are retained.  
    By default old curves are not retained.  For further details, see help for 
    the plot function.
    '''
    if __plot__ == None:
        select_plot()
    __plot__.semilogx(*args, **kwargs)

def semilogy(*args, **kwargs):
    '''
    semilogy(x, y, [style], [yaxis = 'left'|'right'], [hold = 'on'|'off'])
    
    Plot one or more curves on the currently selected plot on semilogartihmic 
    axes (y-axis logarithmic) associated with the specified y axis.  If yaxis 
    is not specified, the curves are plotted on the left y axis.  If the hold 
    argument is specified as 'on', any previously plotted curves are retained.  
    By default old curves are not retained.  For further details, see help for 
    the plot function.
    '''
    if __plot__ == None:
        select_plot()
    __plot__.semilogy(*args, **kwargs)

def loglog(*args, **kwargs):
    '''
    loglog(x, y, [style], [yaxis = 'left'|'right'], [hold = 'on'|'off'])
    
    Plot one or more curves on the currently selected plot on logartihmic axes 
    associated with the specified y axis.  If yaxis is not specified, the curves 
    are plotted on the left y axis.  If the hold argument is specified as 
    'on', any previously plotted curves are retained.  By default old curves 
    are not retained.  For further details, see help for the plot function.
    '''
    if __plot__ == None:
        select_plot()
    __plot__.loglog(*args, **kwargs)

def grid(*args):
    '''
    grid(['on'|'off'])
    
    Set or get the state of the grid on the currently selected plot.  If no 
    state is specified, the current state of the grid of the selected plot is 
    returned.
    '''
    if __plot__ == None:
        select_plot()
    return __plot__.grid(*args)

def xlabel(*args):
    '''
    xlabel([label])
    
    Set or get the x-axis label of the currently selected plot.  If specified, 
    label becomes the x-axis label of the selected plot.  If no label is 
    specified, the current x-axis label is returned.
    '''
    if __plot__ == None:
        select_plot()
    return __plot__.xlabel(*args)

def ylabel(*args, **kwargs):
    '''
    ylabel([label], [yaxis = 'left'|'right'])
    
    Set or get a y-axis label of the currently selected plot.  If specified, 
    label becomes the label of the specified y axis of the selected plot.  If 
    no label is specified, the current label of the specified y axis is 
    returned.  If yaxis is not specified, the left y axis is assumed.
    '''
    if __plot__ == None:
        select_plot()
    return __plot__.ylabel(*args, **kwargs)

def xaxis(*args):
    '''
    xaxis(['linear'|'log'])
    
    Set or get the x-axis mode of the currently selected plot.  If no mode is 
    specified, the current x-axis mode is returned.
    '''
    if __plot__ == None:
        select_plot()
    return __plot__.xaxis(*args)

def yaxis(*args, **kwargs):
    '''
    yaxis(['linear'|'log'], [yaxis = 'left'|'right'])

    Set or get the mode of the specified y axis of the currently selected 
    plot.  If no mode is specified, the current mode of the specified y 
    axis is returned.  If yaxis is not specified, the left y axis is assumed.
    '''
    if __plot__ == None:
        select_plot()
    return __plot__.yaxis(*args, **kwargs)

def xlimits(*args):
    '''
    xlimits(['auto'|'tight'|xlimits])
    
    Set or get the x-axis limits of the currently selected plot.  If fixed 
    limits are specified, they must be supplied in a two-element list.  If 
    no limits are specified, the current lower and upper x-axis limits are 
    returned in a list.
    '''
    if __plot__ == None:
        select_plot()
    return __plot__.xlimits(*args)

def ylimits(*args, **kwargs):
    '''
    ylimits(['auto'|'tight'|ylimits], [yaxis = 'left'|'right'])

    Set or get the limits of the specified y axis of the currently selected 
    plot.  If fixed limits are specified, they must be supplied in a two-
    element list.  If no limits are specified, the current lower and upper 
    limit of the specified y axis are returned in a list.  If yaxis is not
    specified, the left y axis is assumed.
    '''
    if __plot__ == None:
        select_plot()
    return __plot__.ylimits(*args, **kwargs)

def svg(filename):
    '''
    Export the currently selected figure as a scalable vector graphics (.svg) 
    file whose name is specified by the argument.
    '''
    global __figs__
    global __plot__
    if __plot__ == None:
        select_plot()
    title = __plot__.root.winfo_toplevel().title()
    fig = __figs__[title]
    svg_file = codecs.open(filename, encoding = 'utf-8', mode = 'w')
    width = 0.
    for col in range(fig.cols):
        width += fig.plots[0][col].canvas_width
    height = 0.
    for row in range(fig.rows):
        height += fig.plots[row][0].canvas_height
    svg_file.write(u'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width!s}px" height="{height!s}px" viewBox="0 0 {width!s} {height!s}">\n'.format(width = width, height = height))
    y = 0.
    for row in range(fig.rows):
        x = 0.
        for col in range(fig.cols):
            plot = fig.plots[row][col]
            left_save = plot.canvas_left
            top_save = plot.canvas_top
            plot.canvas_left = x
            plot.canvas_top = y
            plot.svg_file = svg_file
            plot.svg_backend()
            plot.begin_group(name = 'subplot_{0!s}_{1!s}'.format(row, col))
            plot.refresh_plot()
            plot.end_group()
            plot.svg_file = None
            plot.tk_backend()
            plot.canvas_left = left_save
            plot.canvas_top = top_save
            plot.refresh_plot()
            x += fig.plots[row][col].canvas_width
        y += fig.plots[row][col].canvas_height
    svg_file.write(u'</svg>\n')
    svg_file.close()

def workspace():
    filtered = ['ALLOW_THREADS', 'BUFSIZE', 'CLIP', 'ERR_CALL', 'ERR_DEFAULT', 
                'ERR_IGNORE', 'ERR_LOG', 'ERR_PRINT', 'ERR_RAISE', 'ERR_WARN',
                'FLOATING_POINT_SUPPORT', 'FPE_DIVIDEBYZERO', 'FPE_INVALID', 
                'FPE_OVERFLOW', 'FPE_UNDERFLOW', 'MAXDIMS', 'MAY_SHARE_BOUNDS', 
                'MAY_SHARE_EXACT', 'RAISE', 'SHIFT_DIVIDEBYZERO', 
                'SHIFT_INVALID', 'SHIFT_OVERFLOW', 'SHIFT_UNDERFLOW', 
                'ScalarType', 'UFUNC_BUFSIZE_DEFAULT', 'UFUNC_PYVALS_NAME', 
                'WRAP', 'sctypeDict', 'sctypeNA', 'sctypes', 
                'tracemalloc_domain', 'typeDict', 'typeNA', 'typecodes']
    variables = []
    for variable in globals().keys():
        if (variable[0:2] != '__' or variable[-2:] != '__') and (variable not in filtered):
            if (type (globals()[variable]) is dict) or (type (globals()[variable]) is tuple) or (type (globals()[variable]) is list) or (type (globals()[variable]) is str) or (type (globals()[variable]) is float) or (type (globals()[variable]) is int) or isinstance((globals()[variable]), ndarray):
                variables.append(variable)
    return variables

def save_workspace(filename):
    '''
    Save the variables in the current workspace using the pickle module 
    to a file whose name is specified by the argument provided. 
    '''
    file = open(filename, 'w')
    variables = workspace()
    pickle.dump(variables, file)
    for variable in variables:
        pickle.dump((globals()[variable]), file)
    file.close()

def load_workspace(filename):
    '''
    Load variables into the workspace from a file that was created previously 
    using the save function.
    '''
    file = open(filename, 'r')
    variables = pickle.load(file)
    for variable in variables:
        globals()[variable] = pickle.load(file)
    file.close()

def who():
    '''
    Display a list of the names of the variables in the current workspace.
    '''
    print('    '.join(sorted(workspace())))

def whos():
    '''
    Display a detailed list of the names, types, and contents of the variables 
    in the current workspace.
    '''
    print('  Name              Type      Length    Value')
    for variable in sorted(workspace()):
        line = '  {0:<16}  '.format(variable)
        if type (globals()[variable]) is dict:
            line = line + 'dict      {0!s:>6}    '.format(len((globals()[variable])))
            value = str((globals()[variable]))
            if len(value) <= 40:
                line = line + value
            else:
                line = line + value[0:20] + '...' + value[-17:]
        elif type (globals()[variable]) is tuple:
            line = line + 'tuple     {0!s:>6}    '.format(len((globals()[variable])))
            value = str((globals()[variable]))
            if len(value) <= 40:
                line = line + value
            else:
                line = line + value[0:20] + '...' + value[-17:]
        elif type (globals()[variable]) is list:
            line = line + 'list      {0!s:>6}    '.format(len((globals()[variable])))
            value = str((globals()[variable]))
            if len(value) <= 40:
                line = line + value
            else:
                line = line + value[0:20] + '...' + value[-17:]
        elif type (globals()[variable]) is str:
            line = line + "str       {0!s:>6}    '".format(len((globals()[variable])))
            value = (globals()[variable])
            if len(value) <= 38:
                line = line + value + "'"
            else:
                line = line + value[0:20] + '...' + value[-15:] + "'"
        elif type (globals()[variable]) is float:
            line = line + 'float               {0!s}'.format((globals()[variable]))
        elif type (globals()[variable]) is int:
            line = line + 'int                 {0!s}'.format((globals()[variable]))
        elif isinstance((globals()[variable]), ndarray):
            line = line + 'ndarray   {0!s:>6}    '.format(len((globals()[variable])))
            value = str((globals()[variable]))
            if len(value) <= 40:
                line = line + value
            else:
                line = line + value[0:20] + '...' + value[-17:]
        print(line)

def linefit(x, y, epsilon = 0.001):
    '''
    Attempts to fit a straight line to an appropriate part of the curve 
    specified by x and y.  It steps through the curve specified by 
    ndarrays x and y searching for a consecutive run of at least 10 
    coordinate pairs to which a straight line can be fit using linear 
    regression with an R^2 (i.e., goodness of fit) value of greater 
    than 1-epsilon.  If there is more than one such run of points, 
    the one with the steepest slope is selected.  A typical value 
    for epsilon is in the range of 5e-4 to 5e-3.  The return values 
    are [first, last, mmax, bmax, Nmax], where

        first is the index of the first point used in the fit,
        last is the index of the last point used in the fit,
        mmax is the slope of the best fit line,
        bmax is the y-axis intercept of the best-fit line, and
        Nmax is the number of points used in the fit.
    '''
    if isinstance(x, ndarray) and isinstance(y, ndarray):
        if len(x) == len(y):
            first = 0
            last = 0
            mmax = 0
            bmax = 0
            Nmax = 0
            i = 0
            while i < len(x) - 1:
                R2 = 1
                N = 1
                sumX = x[i]
                sumX2 = x[i] * x[i]
                sumY = y[i]
                sumY2 = y[i] * y[i]
                sumXY= x[i] * y[i]
                j = i
                while (j < len(x) - 1) and (R2 > 1 - epsilon):
                    j += 1
                    N += 1
                    sumX += x[j]
                    sumX2 += x[j] * x[j]
                    sumY += y[j]
                    sumY2 += y[j] * y[j]
                    sumXY += x[j] * y[j]
                    SXX = sumX2 - sumX * sumX / N
                    SYY = sumY2 - sumY * sumY / N
                    SXY = sumXY - sumX * sumY / N
                    m = SXY / SXX
                    b = (sumY - m * sumX) / N
                    R2 = SXY * SXY / (SXX * SYY)
                if (N > 10) and (abs(m) > abs(mmax)):
                    first = i
                    last = j
                    mmax = m
                    bmax = b
                    Nmax = N
                i = j
            return [first, last, mmax, bmax, Nmax]
        else:
            raise IndexError('ndarrays supplied to linefit must be of the same length')
    else:
        raise ValueError('x and y arguments supplied to linefit must be ndarrays')

def loadcsv(filename):
    '''
    Import data into the workspace from a comma separated variables file.  
    The first line of the file is asssumed to contain unquoted variable names.  
    Each column of numbers is loaded into a numpy array whose name is give by 
    its heading.
    '''
    file = open(filename, 'r')
    line = file.readline()
    names = line.rstrip().split(',')
    for name in names:
        (globals()[name]) = array([])
    for line in file:
        values = line.lstrip().rstrip().split(',')
        for i in range(len(names)):
            (globals()[names[i]]) = append((globals()[names[i]]), array(float(values[i])))
    file.close()

def loadvar(filename):
    '''
    Import data into the workspace from a tab delimited text file.  The variable 
    name is derived from the name of the file without the extension, which is 
    assumed to be a three characters after the dot.  The file is turned into a 
    list of numpy arrays.  Each line in the file is turned into an element of 
    the list. 
    '''
    file = open(filename, 'r')
    name = filename[:-4]
    (globals()[name]) = []
    for line in file:
        values = line.strip().split('\t')
        values = [float(v) for v in values]
        (globals()[name]).append(array(values))
    if len(globals()[name]) == 1:
        (globals()[name]) = (globals()[name])[0]
    file.close()

def loadspice(filename):
    '''
    Import data into the workspace from an LTspice simulation that has been 
    exported as a text file.  Each column in the file is saved in a variable 
    whose name is derived from the column heading.  If the simulation contained 
    multiple steps, the results from each step becomes a numpy array in a list 
    where each successive step is an element in the list.  If the succession 
    of values of the independent variable is the same for each step, the 
    independent variable values become a single numpy array.  If they are 
    not identical for each simulation step, the different successions of 
    values are stored in a list of numpy arrays, like the dependent variables.  
    The results from AC analyses are imported as complex numbers (i.e., with 
    real and imaginary components), even if they were exported in polar form.  
    The succession of parameter values from each step are stored in a numpy 
    array whose name corresponds to the parameter name.
    '''
    file = open(filename, encoding = 'latin_1')
    line = file.readline()
    line = line.replace('.', '')
    line = line.replace(')', '')
    line = line.replace('V(', '')
    line = line.replace('I(', '')
    names = line.rstrip().split('\t')
    state = 0
    for line in file:
        if state == 0:
            if line.find('Step') == -1:
                for name in names:
                    (globals()[name]) = array([])
                values = line.lstrip().rstrip().split('\t')
                for i in range(len(names)):
                    if values[i].find('dB') != -1:
                        values[i] = values[i].replace('(', '')
                        values[i] = values[i].replace(')', '')
                        values[i] = values[i].replace('dB', '')
                        values[i] = values[i].replace('\xB0', '')
                        [gain, phase] = values[i].split(',')
                        value = 10. ** (float(gain) / 20.) * (cos(float(phase) * pi / 180.) + (0 + 1j) * sin(float(phase) * pi / 180.))
                        (globals()[names[i]]) = append((globals()[names[i]]), value)
                    elif values[i].find(',') != -1:
                        [re, im] = values[i].split(',')
                        value = float(re) + (0 + 1j) * float(im)
                        (globals()[names[i]]) = append((globals()[names[i]]), value)
                    else:
                        (globals()[names[i]]) = append((globals()[names[i]]), float(values[i]))
                state = 1
            else:
                words = line.rstrip().split(' ')
                for word in words:
                    if word.find('=') != -1:
                        [param, value] = word.split('=')
                        value = value.replace('\xB5', 'U')
                        value = value.upper()
                        value = value.replace('T', 'E12')
                        value = value.replace('G', 'E9')
                        value = value.replace('MEG', 'E6')
                        value = value.replace('K', 'E3')
                        value = value.replace('M', 'E-3')
                        value = value.replace('U', 'E-6')
                        value = value.replace('N', 'E-9')
                        value = value.replace('P', 'E-12')
                        value = value.replace('F', 'E-15')
                        (globals()[param]) = array(float(value))
                for name in names:
                    (globals()[name]) = [array([])]
                state = 2
        elif state == 1:
            values = line.lstrip().rstrip().split('\t')
            for i in range(len(names)):
                if values[i].find('dB') != -1:
                    values[i] = values[i].replace('(', '')
                    values[i] = values[i].replace(')', '')
                    values[i] = values[i].replace('dB', '')
                    values[i] = values[i].replace('\xB0', '')
                    [gain, phase] = values[i].split(',')
                    value = 10. ** (float(gain) / 20.) * (cos(float(phase) * pi / 180.) + (0 + 1j) * sin(float(phase) * pi / 180.))
                    (globals()[names[i]]) = append((globals()[names[i]]), value)
                elif values[i].find(',') != -1:
                    [re, im] = values[i].split(',')
                    value = float(re) + (0 + 1j) * float(im)
                    (globals()[names[i]]) = append((globals()[names[i]]), value)
                else:
                    (globals()[names[i]]) = append((globals()[names[i]]), float(values[i]))
        elif state == 2:
            if line.find('Step') == -1:
                values = line.lstrip().rstrip().split('\t')
                for i in range(len(names)):
                    if values[i].find('dB') != -1:
                        values[i] = values[i].replace('(', '')
                        values[i] = values[i].replace(')', '')
                        values[i] = values[i].replace('dB', '')
                        values[i] = values[i].replace('\xB0', '')
                        [gain, phase] = values[i].split(',')
                        value = 10. ** (float(gain) / 20.) * (cos(float(phase) * pi / 180.) + (0 + 1j) * sin(float(phase) * pi / 180.))
                        (globals()[names[i]])[-1] = append((globals()[names[i]])[-1], value)
                    elif values[i].find(',') != -1:
                        [re, im] = values[i].split(',')
                        value = float(re) + (0 + 1j) * float(im)
                        (globals()[names[i]])[-1] = append((globals()[names[i]])[-1], value)
                    else:
                        (globals()[names[i]])[-1] = append((globals()[names[i]])[-1], float(values[i]))
            else:
                words = line.rstrip().split(' ')
                for word in words:
                    if word.find('=') != -1:
                        [param, value] = word.split('=')
                        value = value.replace('\xB5', 'U')
                        value = value.upper()
                        value = value.replace('T', 'E12')
                        value = value.replace('G', 'E9')
                        value = value.replace('MEG', 'E6')
                        value = value.replace('K', 'E3')
                        value = value.replace('M', 'E-3')
                        value = value.replace('U', 'E-6')
                        value = value.replace('N', 'E-9')
                        value = value.replace('P', 'E-12')
                        value = value.replace('F', 'E-15')
                        (globals()[param]) = append((globals()[param]), float(value))
                for name in names:
                    (globals()[name]).append(array([]))

    independent_var = (globals()[names[0]])
    if type(independent_var) is list:
        rows_equal_first_row = []
        for i in range(len(independent_var)):
            rows_equal_first_row.append(array_equal(independent_var[0], independent_var[i]))
        if all(rows_equal_first_row):
            (globals()[names[0]]) = (globals()[names[0]])[0]

    file.close()

