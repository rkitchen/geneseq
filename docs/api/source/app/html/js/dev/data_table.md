# Data_Table

module managing the data table and sidebar input.



* * *

## Class: data_table
Manages the data table

**sliders**: `Array` , Contains sidebar slider objects
**sort**: `Array` , Contains sort column and direction
**celltype**: `Array` , Contains unselected celltypes from sidebar
**requests**: `Array` , Contains requests for url builder
### Data_Table.data_table.getSortIcon(item) 

Gets sort icon (uparrow/downarrow/ellipses) for a column header

**Parameters**

**item**: `string`, Column header value

**Returns**: `string`, Class name of icon

### Data_Table.data_table.tableLinks() 

Attaches click listener to entire row based on `<a>` tag in first column


### Data_Table.data_table.initTableHeaders() 

Attaches click listener to column headers for sorting


### Data_Table.data_table.initSliders() 

Initializes sidebar sliders with bootstrap-slider


### Data_Table.data_table.selection_setAll(inputGroup, state) 

Set all checkboxes in a group

**Parameters**

**inputGroup**: `string`, CSS search string of input group

**state**: `boolean`, State to set checkboses to


### Data_Table.data_table.initSelection() 

Initializes sidebar options list
by pushing all to celltype Array


### Data_Table.data_table.update_url() 

Updates history with current request options


### Data_Table.data_table.add_request(key, value) 

Adds key/value pair to requests for url generation

**Parameters**

**key**: `string`, Variable name for server

**value**: `string | Array | number`, Value assigned to key


### Data_Table.data_table.remove_request(key) 

Removes key/value pair from requests

**Parameters**

**key**: `string`, Variable name


### Data_Table.data_table.init_requests() 

Initializes request variable


### Data_Table.data_table.tableUpdate() 

Performs POST request and updates table and window accordingly




* * *










