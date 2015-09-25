# Spline Worker

Calculates coordinates for spline fit-line.



* * *

### Spline Worker.done(name, values) 

Returns message to parent after calculations finish

**Parameters**

**name**: `string`, name of brain region

**values**: `Array`, Array of (x,y) coordinates for fit line



### Spline Worker.avg(list) 

Calculates average of given Array

**Parameters**

**list**: `Array`, list to be averaged

**Returns**: `int`, Average of list


### Spline Worker.fit_line(data, domain) 

Calculates fit line

**Parameters**

**data**: `Array`, Array of (x,y) brainspan coordinates

**domain**: `int`, Max time value being rendered in chart

**Returns**: `Array`, - Array of (x,y) coordinates for fit line



* * *










