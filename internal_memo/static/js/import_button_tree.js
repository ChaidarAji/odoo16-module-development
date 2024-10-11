/*
odoo.define('internal_memo.define_button_regional_value', function (require) {
    "use strict";

    var ListController  = require('web.ListController');
    var ListView        = require('web.ListView');
    var viewRegistry    = require('web.view_registry');

    var TreeButton = ListController.extend({
        buttons_template: 'internal_memo.button_regional_value',
        events: _.extend({}, ListController.prototype.events, {
            'click .import_regional': 'OnImportRegional',
        }),
        OnImportRegional: function () {
            var self = this;
             this.do_action({
                type            : 'ir.actions.act_window',
                res_model       : 'import.payroll.regional.wizard',
                name            :  'Import Data',
                view_mode       : 'form',
                view_type       : 'form',
                views           : [[false, 'form']],
                target          : 'new',
                res_id          : false,
            });
        }
     });

     var RegionalValueListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: TreeButton,
        }),
     });

     viewRegistry.add('regional_value_button_in_tree', RegionalValueListView);

});
*/

/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';
export class RegionalValueListController extends ListController {
   setup() {
       super.setup();
   }
   OnImportRegional() {
       this.actionService.doAction({
          type: 'ir.actions.act_window',
          res_model: 'import.payroll.regional.wizard',
          name:'Import Data',
          view_mode: 'form',
          view_type: 'form',
          views: [[false, 'form']],
          target: 'new',
          res_id: false,
      });
   }
}
registry.category("views").add("regional_value_button_in_tree", {
   ...listView,
   Controller: RegionalValueListController,
   buttonTemplate: "internal_memo.button_regional_value",
});
