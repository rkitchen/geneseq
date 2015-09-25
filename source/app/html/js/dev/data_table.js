/**
 * @overview module managing the data table and sidebar input.
 * @module Data_Table
 * @author Michael Laraia
 */

/**
 * Manages the data table
 * @this - data_table namespace
 * @class data_table
 * @constructor
*/
var data_table = new function() {
    var self = this;
    /**
     * Contains sidebar slider objects
     * @name data_table.sliders
     * @type Array
     */
    self.sliders = [];

    /**
     * Contains sort column and direction
     * @name data_table.sort
     * @type Array
     */
    self.sort = ['expression', -1];

    /**
     * Contains unselected celltypes from sidebar
     * @name data_table.celltype
     * @type Array
     */
    self.celltype = [];

    /**
     * Contains requests for url builder
     * @name data_table.requests
     * @type Array
     */
    self.requests;

    self.init = function() {
        tableLinks();
        init_requests();

        initTableHeaders();
        initSliders();
        initSelection();
        return self;
    };

    /**
     * Gets sort icon (uparrow/downarrow/ellipses) for a column header
     * @param {string} item - Column header value
     * @return {string} Class name of icon
     */
    var getSortIcon = function(item) {
        console.log('item: ' + item);
        console.log('sort: ' + self.sort);
        if (item == self.sort[0]) {
            if (self.sort[1] == -1) return 'arrow_drop_down';
            else return 'arrow_drop_up';
        } else return 'more_horiz';
    };

    /**
     * Attaches click listener to entire row based on `<a>` tag in first column
     */
    var tableLinks = function() {
        $('#data tbody tr').click(function() {
            window.location = $(this).find('a').attr('href');
        }).hover(function() {
            $(this).toggleClass('hover');
        });
    };

    /**
     * Attaches click listener to column headers for sorting
     */
    var initTableHeaders = function() {
        $('table#data th').each(function(index, item) {
            var key = item.getAttribute('value');
            console.log('key: ' + key);
            $(item).click({value: key}, function(event) {
                console.log(event);
                console.log('table header clicked: ' + event.data.value);
                if (self.sort[0] == event.data.value) {
                    self.sort[1] = -self.sort[1];
                } else {
                    self.sort = [event.data.value, -1];
                }

                tableUpdate();
            });
        });
    };

    /**
     * Initializes sidebar sliders with bootstrap-slider
     */
    var initSliders = function() {
        $('input.table-filter.range').each(function(index, item) {
            var slider = new Slider(item);
            slider.name = item.getAttribute('name');
            slider.init = slider.getValue();
            slider.on('slideStop', tableUpdate);

            slider.on('slide', function(item) {
                console.log(item);
                for (var i = 0; i < self.sliders.length; i++) {
                    if (self.sliders[i].getValue() == item) {
                        $(self.sliders[i].element).siblings('span#value').text(item);
                    }
                }
            });
            self.sliders.push(slider);
        });
    };

    /**
     * Set all checkboxes in a group
     * @param {string} inputGroup - CSS search string of input group
     * @param {boolean} state - State to set checkboses to
     */
    var selection_setAll = function(inputGroup, state) {
        options = [];
        $(inputGroup).find('input').each(function(index, item) {
            $(item).prop('checked', state);
            options.push($(item).attr('value'));
        });
        if (!state) self.celltype = options;
        else self.celltype = [];
        tableUpdate();
    };

    /**
     * Initializes sidebar options list
     * by pushing all to celltype Array
     */
    var initSelection = function() {
        var selections = $('li.table-filter.selection');
        selections.find('input.selection').change(function() {
            console.log($(this).is(':checked'));
            console.log($(this).attr('value'));
            value = $(this).attr('value');
            if ($(this).is(':checked')) {
                index = self.celltype.indexOf(value);
                if (index > -1) {
                    self.celltype.splice(index, 1);
                }
            } else {
                self.celltype.push($(this).attr('value'));
            }
            console.log(self.celltype);
            tableUpdate();
        });

        selections.each(function(index, item) {
            console.log(item);
            $(item).find('#select-all').click(function(event) {
                event.preventDefault();
                inputGroup = $(this).parent().parent();
                selection_setAll(inputGroup, true);
            });
            $(item).find('#deselect-all').click(function(event) {
                event.preventDefault();
                inputGroup = $(this).parent().parent();
                selection_setAll(inputGroup, false);
            });
        });
    };

    /**
     * Updates history with current request options
     */
    var update_url = function() {
        var requests = self.requests;
        console.log('update_url requests: ' + requests);
        var url = [];
        if (requests.length > 0) {
            for (var i = 0; i < requests.length; i++) {
                url.push(requests[i].join('='));
            }
            url = url.join('&');
            history.replaceState(null, null, './table?' + url);
        } else history.replaceState(null, null, './table');
        _menu.update_urls();
    };

    /**
     * Adds key/value pair to requests for url generation
     * @param {string} key - Variable name for server
     * @param {string|Array|number} value - Value assigned to key
     */
    var add_request = function(key, value) {
        var requests = self.requests;
        var exists = false;
        for (var i = 0; i < requests.length; i++) {
            if (key == requests[i][0]) {
                requests[i][1] = value;
                exists = true;
                break;
            }
        }

        if (!exists) {
            console.log('pushing');
            requests.push([key, value]);
            console.log('requets: ' + requests);
        }
        self.requests = requests;
        console.log('requests after add: ' + self.requests);
    };

    /**
     * Removes key/value pair from requests
     * @param {string} key - Variable name
     */
    var remove_request = function(key) {
        console.log('removing key ' + key);
        requests = self.requests;
        if (requests.length > 0) {
            for (var i = 0; i < requests.length; i++) {
                if (requests[i][0] == key) {
                    console.log('found');
                    requests.splice(i, 1);
                    self.requests = requests;
                    break;
                }
            }

            console.log('after remove: ' + self.requests);
        }
    };

    /**
     * Initializes request variable
     */
    var init_requests = function() {
        console.log('initializing requests');
        var current = window.location.search.substring(1);
        if (current.length <= 0) self.requests = [];
        else {
            var requests = [];
            $.each(current.split('&'), function(index, item) {
                requests.push(item.split('='));
            });
            self.requests = requests;
        }
    };

    /**
     * Performs POST request and updates table and window accordingly
     */
    var tableUpdate = function() {
        $('#data tbody').empty();

        var post_data = {};

        //sets sorting to post data
        if (self.sort) {
            post_data.sort = self.sort;
        }

        //sets celltypes to post data and updates url
        if (self.celltype.length > 0) {
            post_data.celltype = self.celltype;
            value = '[' + self.celltype + ']';
            add_request('celltype', value);
        } else remove_request('celltype');

        //sets slider values to post data and updates url
        post_data['sliders'] = true;
        $.each(self.sliders, function(index, slider) {
            if (slider.getValue() != slider.init) {
                value = slider.getValue();
                post_data[slider.name] = value;
                if (typeof value != 'number') value = '[' + value + ']';
                add_request(slider.name, value);
            }
        });

        console.log(self.requests);
        update_url();

        //convert data to json to prevent nested object data loss
        post_data = JSON.stringify(post_data);
        console.log(post_data);

        $.post('./table', {'json': post_data},
        function(data, status) {
            console.log('data: ' + data);
            console.log('status: ' + status);
            data = jQuery.parseJSON(data);
            self.returned_data = data;

            if (status == 'success') {
                //propagates data to table
                var table = $('table#data tbody');
                $.each(data, function(index, item) {
                    var row = [];
                    var columns = self.columns;
                    console.log('columns: ' + columns);
                    row.push('<a href="./gene?id=' +
                        item['_id'] + '">' +
                        item[columns[0]] +
                        '</a>');
                    for (var i = 1; i < columns.length; i++) {
                        row.push(item[columns[i]]);
                    }

                    table.append(['<tr><td>',
                        row.join('</td><td>'),
                        '</td></tr>'].join(''));
                });

                //sets sort icons
                $('table#data thead th').each(function(index, item) {
                    $(item).children('i').
                        text(getSortIcon(item.getAttribute('value')));
                });

                //adds click listener to each table row
                tableLinks();
            }
        });
    };
}

$(document).ready(function() {
    var d = data_table;
    d.init();

    var columns = [];
    $('table#data thead th').each(function(index, item) {
        columns.push(item.getAttribute('value'));
    });
    d['columns'] = columns;
});
