# -*- coding: utf-8 -*-
{
    'name': "internal_memo",

    'summary': """
        Internal memo untuk segala  kebutuhan mulai lembur, pengurangan biaya seragam, training, dan lain-lain""",

    'description': """
        Internal memo untuk segala  kebutuhan mulai lembur, pengurangan biaya seragam, training, dan lain-lain
    """,

    'author': "Gamatechno Indonesia",
    'website': "https://www.gamatechno.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Payroll Localization',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
            
            'base',
            'hr',
            'om_hr_payroll',
            'bms_inherit_employee',
            'bms_inherit_recruitment',
            'weha_smart_approvals',
            'hr_resignation',
            'hr_disciplinary_tracking',
            'hr_holidays',
            'job_portal_kanak',
            'hr_employee_updation',
            'custom_print',
            'hr_gamification'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/rule.xml',
        'views/state.xml',
        'views/job.xml',
        'views/custom_grade.xml',
        'views/custom_job_position.xml',
        'views/custom_payslip.xml',
        'views/custom_payslip_run.xml',
        'views/salary_type.xml',
        'views/reference.xml',
        'views/internal_memo.xml',
        'views/custom_contract.xml',
        'views/custom_employee.xml',
        'views/contract_approval.xml',
        'views/hr_periode.xml',
        'views/ref_religion.xml',
        'views/payroll_date_setting.xml',
        'views/regional.xml',
        'data/setting.xml',
        'views/setting.xml',
        'views/presensi.xml',
        'views/approval.xml',
        'views/divisi.xml',
        'views/cron.xml',
        'views/payfield_views.xml',
        'views/templates.xml',
        'views/position_master_views.xml',
        'views/salary_structure_views.xml',
        'views/multiple_update_payslip.xml',
        'reports/report_payslip_custom3_template.xml',
        'views/salary_rule.xml',
        'views/custom_button.xml',
        #'views/assets.xml',
        'views/mail_template.xml'
    ],
    'assets': {
        'web.assets_backend': [
            #'internal_memo/static/js/import_button_tree.js',
            #'internal_memo/static/xml/import_button.xml',
            'internal_memo/static/css/position_chart.scss',
            'internal_memo/static/xml/pos_org_chart.xml',
            'internal_memo/static/js/pos_org_chart.js',
            '/internal_memo/static/src/views/*/*'
            
            
            #'internal_memo/static/js/import_button.js',
        ]
    },

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
