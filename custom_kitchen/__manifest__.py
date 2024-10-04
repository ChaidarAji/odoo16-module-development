# -*- coding: utf-8 -*-
{
    'name': 'Custom Kitchen',
    'version': '1.0.0',
    'category': 'Sales/Point of Sale',
    'description': """Custom Kitchen module""",
    'sequence': '100',
    'website': '',
    'author': 'chaidaraji@gmail.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'sale', 'sale_management','point_of_sale', 'pos_restaurant'],
    'demo': [],
    'data': [
        # 'security/ir.model.access.csv',
        'views/mail_channel_views.xml',
        'views/sale_order_views.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
