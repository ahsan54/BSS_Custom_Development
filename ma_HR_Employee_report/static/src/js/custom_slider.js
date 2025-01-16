

odoo.define('ma_HR_Employee_report.custom_slider', function (require) {
    "use strict";

    var core = require('web.core');
    var FieldRegistry = require('web.field_registry');
    var FieldInteger = require('web.basic_fields').FieldInteger;

    var CustomSlider = FieldInteger.extend({
        // Custom behavior for the slider can be written here
    });

    FieldRegistry.add('slider', CustomSlider);
});
