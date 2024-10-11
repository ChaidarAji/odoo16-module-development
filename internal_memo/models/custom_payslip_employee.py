from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def wizard_payslip_employee(self):
        return {
            'name'          : 'Filter Pegawai',
            'type'          : 'ir.actions.act_window',
            'view_type'     : 'form',
            'view_mode'     : 'form',
            'res_model'     : 'filter.hr.payslip.generate.wizard',
            'views'         : [(False, 'form')],
            'view_id'       : False,
            'target'        : 'new',
            'context'       : self.env.context,
        }

    def compute_sheet(self):
        payslips = self.env['hr.payslip']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if active_id:
            [run_data] = self.env['hr.payslip.run'].browse(active_id).read(['date_start', 'date_end', 'credit_note','year','month','periode_id'])
        from_date = run_data.get('date_start')
        to_date = run_data.get('date_end')

        

        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))
        
        # should validate to protect only one month process
        not_processed = self.env['hr.payslip'].sudo().search_read([('employee_id','in',data['employee_ids']),('state','=','draft'),('periode_search','!=', run_data.get('month')+'-'+str(run_data.get('year')))],['id','employee_id','position_id','location_id','area_id'])
        
        run_data2 = self.env['hr.payslip.run'].sudo().search([('id','=',active_id)])
        # nggak bisa
        arr_invalid = [(5, 0, 0)]

        run_data2.write({
            'invalid_ids' : arr_invalid
        })

        if len(not_processed) > 0:
            

            arr_invalid = []

            for notpro in not_processed:
                arr_invalid.append((0,0, {
                    'name'          : notpro['employee_id'][0],
                    'batch'         : active_id,
                    'payslip'       : notpro['id'],
                    'position_id'   : notpro['position_id'][0],
                    'location_id'   : notpro['location_id'][0],
                    'area_id'       : notpro['area_id'][0]
                }))
                #self.env['hr.payslip.run.invalid'].sudo().create()

            _logger.error('CHECK INVALID')
            _logger.error(arr_invalid)
            # updating data
            run_data2.write({
                'invalid_ids' : arr_invalid
            })


            return {'type': 'ir.actions.act_window_close'}
        else:
            for employee in self.env['hr.employee'].browse(data['employee_ids']):
                # from date and to date will be based on hr periode
                slip_data2  = self.env['hr.payslip'].onchange_periode_id(run_data.get('month'), run_data.get('year'), employee.id, run_data.get('periode_id')[0])
                #slip_data   = self.env['hr.payslip'].onchange_employee_id(from_date, to_date, employee.id, contract_id=False)
                
                # adding data based on
                slip_data   = self.env['hr.payslip'].onchange_employee_id2(slip_data2['value'].get('date_from'), slip_data2['value'].get('date_to'),slip_data2['value'].get('attend_start'), slip_data2['value'].get('attend_end'), employee.id, contract_id=False)
                

                res = {
                    'employee_id'           : employee.id,
                    'name'                  : slip_data['value'].get('name'),
                    'struct_id'             : slip_data2['value'].get('struct_id'),
                    'contract_id'           : slip_data2['value'].get('contract_id'),
                    'payslip_run_id'        : active_id,
                    'input_line_ids'        : [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                    'worked_days_line_ids'  : [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                    'date_from'             : slip_data2['value'].get('date_from'),
                    'date_to'               : slip_data2['value'].get('date_to'),
                    'credit_note'           : run_data.get('credit_note'),
                    'company_id'            : employee.company_id.id,
                    'year'                  : slip_data2['value'].get('year'),
                    'month'                 : slip_data2['value'].get('month'),
                    'attend_start'          : slip_data2['value'].get('attend_start'),
                    'attend_end'            : slip_data2['value'].get('attend_end'),
                    'tax'                   : slip_data2['value'].get('tax'),
                    'paydate'               : slip_data2['value'].get('paydate'),
                    'parent_id'             : False

                }
                payslips += self.env['hr.payslip'].create(res)
            payslips.compute_sheet()
            return {'type': 'ir.actions.act_window_close'}