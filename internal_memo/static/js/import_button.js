import { KanbanController } from "@web/views/kanban/kanban_controller";
import { registry } from '@web/core/registry';
import { kanbanView } from '@web/views/kanban/kanban_view';
export class SaleKanbanController extends KanbanController {
   setup() {
       super.setup();
   }
   OnImportRegional() {
       this.actionService.doAction({
          type: 'ir.actions.act_window',
          res_model: 'import.payroll.regional.wizard',
          name :'Import Data',
          view_mode: 'form',
          view_type: 'form',
          views: [[false, 'form']],
          target: 'new',
          res_id: false,
      });
   }
}
registry.category("views").add("button_in_kanban", {
   ...kanbanView,
   Controller: SaleKanbanController,
   buttonTemplate: "button_import_regional.KanbanView.Buttons",
});