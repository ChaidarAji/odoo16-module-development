/** @odoo-module */

import { listView } from "@web/views/list/list_view";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { registry } from "@web/core/registry";
import { download } from "@web/core/network/download";
import framework from 'web.framework';
import session from 'web.session';

import { ButtonRegionalValueImportController as Controller } from './button_near_create_button_controller';
import { ButtonKanbanController as KanbanController } from './button_near_create_button_controller';

export const ButtonRegionalValueImportView = {
    ...listView,
    Controller,
    buttonTemplate: 'internal_memo.RegionalValueImportButtonView.Buttons',
};

export const ButtonKoreksiGajiImportView = {
    ...listView,
    Controller,
    buttonTemplate: 'internal_memo.KoreksiGajiImportButtonView.Buttons',
};

export const ButtonContractImportView = {
    ...listView,
    Controller,
    buttonTemplate: 'internal_memo.ContractImportButtonView.Buttons',
};

export const ButtonPayslipExportView = {
    ...listView,
    Controller,
    buttonTemplate: 'internal_memo.PayslipExportButtonView.Buttons',
};

export const ButtonPayslipFilterView = {
    ...listView,
    Controller,
    buttonTemplate: 'internal_memo.PayslipFilterButtonView.Buttons',
};

export const ButtonEmployeeView = {
    ...listView,
    Controller,
    buttonTemplate: 'internal_memo.EmployeeButtonView.Buttons',
};

export const ButtonEmployeeKanbanView = {
    ...kanbanView,
    Controller : KanbanController,
    buttonTemplate: 'internal_memo.EmployeeButtonKanbanView.Buttons',
};


export const ButtonPrePayrollImportView = {
    ...listView,
    Controller,
    buttonTemplate: 'internal_memo.PrePayrollButtonView.Buttons',
};



registry.category("views").add("button_regional_value_button", ButtonRegionalValueImportView);
registry.category("views").add("button_koreksi_gaji_button", ButtonKoreksiGajiImportView);
registry.category("views").add("button_contract_button", ButtonContractImportView);
registry.category("views").add("button_payslip_export_button", ButtonPayslipExportView);
registry.category("views").add("button_employee_button", ButtonEmployeeView);
registry.category("views").add("button_employee_kanban_button", ButtonEmployeeKanbanView);
registry.category("views").add("button_pre_payroll_button", ButtonPrePayrollImportView);


registry.category("ir.actions.report handlers").add("xlsx", async (action) => {
    if (action.report_type === 'xlsx' && action.data.model =='export.payslip.wizard') {
        framework.blockUI();
        var def = $.Deferred();
        session.get_file({
            url: '/excel_payslip_reports',
            data: action.data,
            success: def.resolve.bind(def),
            error: (error) => this.call('crash_manager', 'rpc_error', error),
            complete: framework.unblockUI,
        });
        return def;
    } else if (action.report_type === 'xlsx' && action.data.model =='export.pre.payroll.wizard') {
        framework.blockUI();
        var def = $.Deferred();
        session.get_file({
            url: '/excel_pre_payroll_reports',
            data: action.data,
            success: def.resolve.bind(def),
            error: (error) => this.call('crash_manager', 'rpc_error', error),
            complete: framework.unblockUI,
        });
        return def;
    }
 });


