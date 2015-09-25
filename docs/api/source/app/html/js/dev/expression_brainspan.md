# Brainspan

Brainspan module.



* * *

## Class: brainspan
Manages the brainspan chart

**canvases**: `Object` , Contains each brain region chart being rendered
### Brainspan.brainspan.get_width(count) 

Gets width for svg

**Parameters**

**count**: `int`, number of charts being rendered

**Returns**: `int`, width of svg

### Brainspan.brainspan.get_height() 

Gets height for svg including margins

**Returns**: `int`, height of svg

### Brainspan.brainspan.get_ticks(max) 

Gets tick locations for y axis

Deprecated: true

**Parameters**

**max**: `int`, maximum value

**Returns**: `Array`, with range of ticks

### Brainspan.brainspan.draw_plot(canvas, data, dimen, axis, scales) 

Draws a plot for one region

**Parameters**

**canvas**: `Object`, d3 <g> to draw plot in

**data**: `Object`, object containing `name` of
brain region and `points` (x, y) coordinates

**dimen**: `Object`, object containing `width` and `height`

**axis**: `Object`, object containing `x` x-axis and `y` y-axis

**scales**: `Object`, object containing `x` x-scale and `y` y-scale


### Brainspan.brainspan.draw_line(e) 

Callback function for spline-calculating worker

**Parameters**

**e**: `Object`, message returned from worker containing Array
`data` list of (x,y) coordinates for spline


### Brainspan.brainspan.draw_svg(id, source, params) 

Draws svg plot and calls draw_plot for each brain region

**Parameters**

**id**: `string`, gene id to plot

**source**: `string`, data source to POST to

**params**: `dict`, JSON object containing height, widht, and radius


### Brainspan.brainspan.avg(list) 

Calculates average of given Array

**Parameters**

**list**: `Array`, list to be averaged

**Returns**: `int`, Average of list

### Brainspan.brainspan.plot(id, source, params) 

Public function to draw plot

**Parameters**

**id**: `string`, gene id to plot

**source**: `string`, data source to POST to

**params**: `dict`, optional




* * *










