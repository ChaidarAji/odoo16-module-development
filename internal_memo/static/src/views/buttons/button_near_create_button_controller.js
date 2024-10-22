/** @odoo-module */

import { useService } from "@web/core/utils/hooks";
import { ListController } from "@web/views/list/list_controller";
import { KanbanController } from "@web/views/kanban/kanban_controller";


export class ButtonKanbanController extends KanbanController {
	setup() {
		super.setup();
	}

    async OnFilterKanbanEmployee() {
        // based on last filter
        var session = require('web.session');
        var user = session.user_id 
        var context = {};

        this.actionService.doAction({
            type: 'ir.actions.act_window',
            res_model: 'filter.employee.wizard',
            name:'Filter Employee',
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            target: 'new',
            res_id: false,
            context  : context
        });

    }


}

export class ButtonRegionalValueImportController extends ListController {
	setup() {
		super.setup();
		this.orm = useService("orm");
	}

	async OnImportRegional() {
        // call wizard from javascript
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

    async OnExportKoreksiGaji() {
        // call wizard from javascript
        this.actionService.doAction({
            type        : 'ir.actions.act_window',
            res_model   : 'export.payroll.koreksi.gaji.wizard',
            name        : 'Export Data',
            view_mode   : 'form',
            view_type   : 'form',
            views       : [[false, 'form']],
            target      : 'new',
            res_id      : false
        });
        
    }

    async OnImportKoreksiGaji() {
        // call wizard from javascript
        this.actionService.doAction({
            type: 'ir.actions.act_window',
            res_model: 'import.payroll.koreksi.gaji.wizard',
            name:'Import Data',
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            target: 'new',
            res_id: false,
        });
        
    }

    async OnImportContract() {
        // call wizard from javascript
        this.actionService.doAction({
            type: 'ir.actions.act_window',
            res_model: 'import.contract.wizard',
            name:'Import Data',
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            target: 'new',
            res_id: false,
        });
        
    }

    async OnImportPrepayroll() {
        // call wizard from javascript
        this.actionService.doAction({
            type        : 'ir.actions.act_window',
            res_model   : 'import.pre.payroll.wizard',
            name        :'Import Data',
            view_mode   : 'form',
            view_type   : 'form',
            views       : [[false, 'form']],
            target      : 'new',
            res_id      : false
        });
        
    }

    async OnExportPrepayroll() {
        // call wizard from javascript
        this.actionService.doAction({
            type        : 'ir.actions.act_window',
            res_model   : 'export.pre.payroll.wizard',
            name        : 'Export Data',
            view_mode   : 'form',
            view_type   : 'form',
            views       : [[false, 'form']],
            target      : 'new',
            res_id      : false
        });
        
    }



    async OnExportPayslip() {
        // call wizard from javascript
        this.actionService.doAction({
            type: 'ir.actions.act_window',
            res_model: 'export.payslip.wizard',
            name:'Cetak Excel',
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            target: 'new',
            res_id: false,
        });
        
    }

    async OnFilterPayslip() {
        // based on last filter
        var session = require('web.session');
        var user = session.user_id 
        var context = {'source_menu':'payslip'};

        //var result = this.orm.call('filter.payslip.wizard','search_read',[('create_uid','=', user)])

        const rpc = require('web.rpc')
        await rpc.query({
            model: 'filter.payslip.wizard',
            method: 'search_last',
            args : [('create_uid','=', user)]
        }).then(data => {
            console.log(data)
            if (data.status == 200) {
                if (data.data.length > 0) {
                    context['default_year']  = data.data[0].year
                    context['default_month']  = data.data[0].month

                    // jika array
                    if (Array.isArray(data.data[0].category)) {
                        context['default_category']  = data.data[0].category[0]
                    }

                    if (Array.isArray(data.data[0].payroll_periode)) {
                        context['default_payroll_periode']  = data.data[0].payroll_periode[0]
                    }

                    if (Array.isArray(data.data[0].cost_center)) {
                        context['default_cost_center']  = data.data[0].cost_center[0]
                    }

                    if (Array.isArray(data.data[0].work_location)) {
                        context['default_work_location']  = data.data[0].work_location[0]
                    }

                    if (data.data[0].pay_freq != false) {
                        context['default_pay_freq']  = data.data[0].pay_freq
                    }

                    if (Array.isArray(data.data[0].tax_location)) {
                        context['default_tax_location']  = data.data[0].tax_location[0]
                    }

                    if (data.data[0].tax_type != false) {
                        context['default_tax_type']  = data.data[0].tax_type
                    }

                } 
            } 
        })

        

        this.actionService.doAction({
            type: 'ir.actions.act_window',
            res_model: 'filter.payslip.wizard',
            name:'Filter Payslip',
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            target: 'new',
            res_id: false,
            context  : context
        });
        
    }

    async OnFilterPayslipSendEmail() {
        // based on last filter
        var session = require('web.session');
        var user = session.user_id 
        var context = {'source_menu':'payslip_send_email'};

        //var result = this.orm.call('filter.payslip.wizard','search_read',[('create_uid','=', user)])

        const rpc = require('web.rpc')
        await rpc.query({
            model: 'filter.payslip.wizard',
            method: 'search_last',
            args : [('create_uid','=', user)]
        }).then(data => {
            console.log(data)
            if (data.status == 200) {
                if (data.data.length > 0) {
                    context['default_year']  = data.data[0].year
                    context['default_month']  = data.data[0].month

                    // jika array
                    if (Array.isArray(data.data[0].category)) {
                        context['default_category']  = data.data[0].category[0]
                    }

                    if (Array.isArray(data.data[0].payroll_periode)) {
                        context['default_payroll_periode']  = data.data[0].payroll_periode[0]
                    }

                    if (Array.isArray(data.data[0].cost_center)) {
                        context['default_cost_center']  = data.data[0].cost_center[0]
                    }

                    if (Array.isArray(data.data[0].work_location)) {
                        context['default_work_location']  = data.data[0].work_location[0]
                    }

                    if (data.data[0].pay_freq != false) {
                        context['default_pay_freq']  = data.data[0].pay_freq
                    }

                    if (Array.isArray(data.data[0].tax_location)) {
                        context['default_tax_location']  = data.data[0].tax_location[0]
                    }

                    if (data.data[0].tax_type != false) {
                        context['default_tax_type']  = data.data[0].tax_type
                    }

                } 
            } 
        })

        

        this.actionService.doAction({
            type: 'ir.actions.act_window',
            res_model: 'filter.payslip.wizard',
            name:'Filter Payslip',
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            target: 'new',
            res_id: false,
            context  : context
        });
        
    }


    async OnFilterEmployee() {
        // based on last filter
        var session = require('web.session');
        var user = session.user_id 
        var context = {};

        this.actionService.doAction({
            type: 'ir.actions.act_window',
            res_model: 'filter.employee.wizard',
            name:'Filter Employee',
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            target: 'new',
            res_id: false,
            context  : context
        });

    }

    async OnFilterPrePayroll() {
        // based on last filter
        var session = require('web.session');
        var user = session.user_id 
        var context = {};

        this.actionService.doAction({
            type: 'ir.actions.act_window',
            res_model: 'filter.pre.payroll.wizard',
            name:'Filter Data Payroll',
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            target: 'new',
            res_id: false,
            context  : context
        });

    }

    async OnFilterKoreksiNilaiGaji() {
        // based on last filter
        var session = require('web.session');
        var user = session.user_id 
        var context = {};

        this.actionService.doAction({
            type: 'ir.actions.act_window',
            res_model: 'filter.payroll.koreksi.gaji.wizard',
            name:'Filter Data Payroll',
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            target: 'new',
            res_id: false,
            context  : context
        });

    }

    
    async OnHrPayslipSendEmail() {
        // based on last filter
        var session = require('web.session');
        var user = session.user_id 
        var context = {};

        this.actionService.doAction({
            type: 'ir.actions.act_window',
            res_model: 'hr.payslip.send.email.wizard',
            name:'Payslip Send Email',
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            target: 'new',
            res_id: false,
            context  : context
        });

    }

    async OnHrPayslipBankTransfer() {
        // based on last filter
        var session = require('web.session');
        var user = session.user_id 
        var context = {};

        this.actionService.doAction({
            type: 'ir.actions.act_window',
            res_model: 'hr.payslip.bank.transfer.wizard',
            name:'Payslip Bank Transfer',
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            target: 'new',
            res_id: false,
            context  : context
        });

    }
}





