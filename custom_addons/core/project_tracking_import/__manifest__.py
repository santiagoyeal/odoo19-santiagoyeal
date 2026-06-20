{
    'name': 'Project Tracking Import',
    'version': '19.0.1.0.0',
    'category': 'Project',
    'summary': 'Import projects from Notion-style markdown files in ZIP archives',
    'description': """
Project Tracking Import
======================
This module allows you to import project tracking data from Notion-style 
markdown files contained in ZIP archives. Each ZIP file contains a .md file 
with project information including budget, clients, dates, priority, status, 
and time tracking table.

Features:
* Import multiple ZIP files at once
* Parse markdown files with project metadata
* Create project tracking records with time lines
* Support for custom field mappings
""",
    'author': 'Santiago Alcalá',
    'website': 'https://github.com/santiagoyeal',
    'license': 'LGPL-3',
    'depends': ['base', 'sale', 'project', 'hr_timesheet', 'account'],
    'data': [
        'security/project_tracking_security.xml',
        'views/project_tracking_views.xml',
        'views/project_tracking_import_wizard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'project_tracking_import/static/src/css/project_tracking.css',
        ],
    },
    'installable': True,
    'application': True,
    'sequence': 10,
}
