import zipfile
import io
import re
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProjectTrackingImportWizard(models.TransientModel):
    _name = 'project.tracking.import.wizard'
    _description = 'Import Projects from ZIP Files'

    zip_files = fields.Many2many('ir.attachment', 'wizard_zip_rel', 'wizard_id', 'attachment_id', 'ZIP Files', required=True)
    duplicate_handling = fields.Selection([
        ('skip', 'Skip Duplicates'),
        ('update', 'Update Duplicates'),
    ], 'Duplicate Handling', default='skip', required=True,
       help='How to handle projects that already exist: skip them or update existing records')
    import_log = fields.Text('Import Log', readonly=True)
    
    def action_import(self):
        """Import projects from multiple ZIP files"""
        if not self.zip_files:
            raise UserError(_('Please select at least one ZIP file to import.'))
        
        log_messages = []
        imported_count = 0
        skipped_count = 0
        updated_count = 0
        error_count = 0
        
        for attachment in self.zip_files:
            try:
                # Decode binary data from attachment
                zip_data = io.BytesIO(attachment.datas)
                zip_filename = attachment.name
                
                # Process ZIP (supports nested ZIPs)
                self._process_zip_file(zip_data, zip_filename, log_messages, 
                                       imported_count, updated_count, skipped_count, error_count)
                
            except zipfile.BadZipFile:
                error_count += 1
                log_messages.append(f"✗ Invalid ZIP file: {attachment.name}")
                continue
            except Exception as e:
                error_count += 1
                log_messages.append(f"✗ Error processing {attachment.name}: {str(e)}")
                continue
        
        # Summary
        summary = f"""
=== Import Summary ===
Total ZIP files processed: {len(self.zip_files)}
Successfully imported: {imported_count}
Updated (duplicates): {updated_count}
Skipped (duplicates): {skipped_count}
Errors: {error_count}
"""
        self.import_log = summary + '\n' + '\n'.join(log_messages)
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import Results',
            'res_model': 'project.tracking.import.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def _parse_markdown(self, content):
        """Parse markdown content and extract project data"""
        data = {
            'name': '',
            'budget': 0.0,
            'client': '',
            'client_url': '',
            'end_client': '',
            'due_date': None,
            'priority': 'medium',
            'status': 'not_started',
            'estado': 'development',
            'payment_status': 'unpaid',
            'lines': []
        }
        
        lines = content.split('\n')
        current_section = None
        in_table = False
        table_headers = []
        
        for line in lines:
            line = line.strip()
            
            # Parse title (module name)
            if line.startswith('# ') and not data['name']:
                data['name'] = line[2:].strip()
                continue
            
            # Parse metadata fields
            if ':' in line and not in_table:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip().lower()
                    value = parts[1].strip()
                    
                    if 'budget' in key:
                        # Extract numeric value from budget (e.g., "7500,00 MXN")
                        budget_match = re.search(r'[\d.,]+', value.replace(',', '.'))
                        if budget_match:
                            data['budget'] = float(budget_match.group().replace(',', '.'))
                    
                    elif 'client' in key and 'end' not in key:
                        # Extract client name and URL
                        url_match = re.search(r'\((https?://[^\)]+)\)', value)
                        if url_match:
                            data['client_url'] = url_match.group(1)
                            data['client'] = value.split('(')[0].strip()
                        else:
                            data['client'] = value
                    
                    elif 'cliente final' in key or 'end client' in key:
                        data['end_client'] = value
                    
                    elif 'due date' in key or 'fecha límite' in key:
                        try:
                            # Parse date (e.g., "23 de abril de 2026")
                            date_obj = self._parse_spanish_date(value)
                            if date_obj:
                                data['due_date'] = date_obj.strftime('%Y-%m-%d')
                        except:
                            pass
                    
                    elif 'priority' in key or 'prioridad' in key:
                        priority_map = {
                            'low': 'low', 'baja': 'low',
                            'medium': 'medium', 'media': 'medium',
                            'high': 'high', 'alta': 'high'
                        }
                        value_lower = value.lower()
                        for k, v in priority_map.items():
                            if k in value_lower:
                                data['priority'] = v
                                break
                    
                    elif 'status' in key and 'payment' not in key:
                        status_map = {
                            'not started': 'not_started', 'no iniciado': 'not_started',
                            'in progress': 'in_progress', 'en progreso': 'in_progress',
                            'completed': 'completed', 'completado': 'completed',
                            'on hold': 'on_hold', 'en espera': 'on_hold',
                            'cancelled': 'cancelled', 'cancelado': 'cancelled'
                        }
                        value_lower = value.lower()
                        for k, v in status_map.items():
                            if k in value_lower:
                                data['status'] = v
                                break
                    
                    elif 'estado' in key and 'payment' not in key:
                        estado_map = {
                            'development': 'development', 'desarrollo': 'development',
                            'staging': 'staging',
                            'production': 'production', 'producción': 'production'
                        }
                        value_lower = value.lower()
                        for k, v in estado_map.items():
                            if k in value_lower:
                                data['estado'] = v
                                break
                    
                    elif 'payment' in key or 'pago' in key:
                        payment_map = {
                            'unpaid': 'unpaid', 'sin pago': 'unpaid',
                            'partial': 'partial', 'parcial': 'partial',
                            'paid': 'paid', 'pagado': 'paid'
                        }
                        value_lower = value.lower()
                        for k, v in payment_map.items():
                            if k in value_lower:
                                data['payment_status'] = v
                                break
            
            # Detect table start
            if line.startswith('|') and '---' in line:
                in_table = True
                continue
            
            # Parse table rows
            if in_table and line.startswith('|'):
                parts = [p.strip() for p in line.split('|')]
                parts = [p for p in parts if p]  # Remove empty strings
                
                if len(parts) >= 3:
                    # Check if this is a header row
                    if 'fecha' in parts[0].lower() or 'date' in parts[0].lower():
                        table_headers = parts
                        continue
                    
                    # Parse data row
                    if len(parts) >= 3:
                        date_str = parts[0]
                        description = parts[1]
                        hours_str = parts[2]
                        
                        # Parse date
                        date_obj = self._parse_spanish_date(date_str)
                        if date_obj:
                            date_formatted = date_obj.strftime('%Y-%m-%d')
                        else:
                            date_formatted = date_str
                        
                        # Parse hours (format: "00:10" or "02:30")
                        hours = self._parse_time(hours_str)
                        
                        if hours > 0:
                            data['lines'].append({
                                'date': date_formatted,
                                'description': description,
                                'hours': hours
                            })
        
        return data
    
    def _parse_spanish_date(self, date_str):
        """Parse Spanish date format (e.g., '23 de abril de 2026')"""
        months = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }
        
        date_str = date_str.lower()
        for month_name, month_num in months.items():
            if month_name in date_str:
                # Extract day and year
                day_match = re.search(r'(\d+)', date_str)
                year_match = re.search(r'(\d{4})', date_str)
                
                if day_match and year_match:
                    try:
                        day = int(day_match.group(1))
                        year = int(year_match.group(1))
                        return datetime(year, month_num, day)
                    except:
                        pass
        return None
    
    def _parse_time(self, time_str):
        """Parse time format (e.g., '00:10' or '02:30') to hours"""
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 2:
                try:
                    hours = int(parts[0])
                    minutes = int(parts[1])
                    return hours + (minutes / 60)
                except:
                    pass
        return 0.0
    
    def _check_duplicate(self, data):
        """Check if project already exists"""
        # Check if project with same name exists
        existing_project = self.env['project.project'].search([
            ('name', '=', data['name']),
        ], limit=1)
        
        if existing_project:
            return True, existing_project
        
        return False, None
    
    def _create_project(self, data, zip_filename, is_duplicate=False, existing_record=None):
        """Create or update native Odoo records from parsed data"""
        # 1. Create or find Partner (Client)
        partner = self._find_or_create_partner(data['client'], data['client_url'])
        
        # 2. Create or update Sale Order (Cotización)
        sale_order = self._find_or_create_sale_order(data, partner, zip_filename)
        
        # 3. Create or update Project (vinculado a Sale Order)
        project = self._find_or_create_project(data, sale_order)
        
        # 4. Create or update Analytic Lines (Timesheets)
        self._create_timesheets(data, project)
        
        return sale_order, project
    
    def _find_or_create_partner(self, client_name, client_url):
        """Find or create partner from client name"""
        partner = self.env['res.partner'].search([('name', '=', client_name)], limit=1)
        if not partner:
            partner = self.env['res.partner'].create({
                'name': client_name,
                'is_company': True,
                'customer': True,
            })
        return partner
    
    def _find_or_create_sale_order(self, data, partner, zip_filename):
        """Find or create sale order from project data"""
        # Search for existing sale order by client and project name
        existing = self.env['sale.order'].search([
            ('partner_id', '=', partner.id),
            ('state', 'in', ['draft', 'sent', 'sale']),
        ], limit=1)
        
        if existing:
            # Update existing sale order
            existing.write({
                'note': f"Imported from ZIP: {zip_filename}\nClient URL: {data['client_url']}\nEnd Client: {data['end_client']}",
            })
            return existing
        else:
            # Create new sale order
            sale_order = self.env['sale.order'].create({
                'partner_id': partner.id,
                'date_order': fields.Date.today(),
                'state': 'draft',
                'note': f"Imported from ZIP: {zip_filename}\nClient URL: {data['client_url']}\nEnd Client: {data['end_client']}",
            })
            
            # Create order line with budget
            if data['budget'] > 0:
                self.env['sale.order.line'].create({
                    'order_id': sale_order.id,
                    'name': data['name'],
                    'product_id': self._get_service_product().id,
                    'product_uom_qty': 1,
                    'price_unit': data['budget'],
                })
            
            return sale_order
    
    def _get_service_product(self):
        """Get or create a default service product for sale orders"""
        product = self.env['product.product'].search([
            ('name', '=', 'Consulting Service'),
            ('detailed_type', '=', 'service'),
        ], limit=1)
        
        if not product:
            product = self.env['product.product'].create({
                'name': 'Consulting Service',
                'detailed_type': 'service',
                'list_price': 0.0,
                'sale_ok': True,
            })
        
        return product
    
    def _find_or_create_project(self, data, sale_order):
        """Find or create project linked to sale order"""
        # Search for existing project by name
        existing = self.env['project.project'].search([
            ('name', '=', data['name']),
        ], limit=1)
        
        if existing:
            # Update existing project
            existing.write({
                'partner_id': sale_order.partner_id.id,
                'date_deadline': data['due_date'],
                'description': f"End Client: {data['end_client']}\nStatus: {data['status']}\nEstado: {data['estado']}",
            })
            return existing
        else:
            # Create new project
            project = self.env['project.project'].create({
                'name': data['name'],
                'partner_id': sale_order.partner_id.id,
                'date_deadline': data['due_date'],
                'description': f"End Client: {data['end_client']}\nStatus: {data['status']}\nEstado: {data['estado']}",
            })
            
            # Link project to sale order analytic account
            if sale_order.analytic_account_id:
                project.write({'analytic_account_id': sale_order.analytic_account_id.id})
            
            return project
    
    def _create_timesheets(self, data, project):
        """Create analytic lines (timesheets) from time tracking data"""
        for line_data in data['lines']:
            # Check if timesheet already exists
            existing = self.env['account.analytic.line'].search([
                ('project_id', '=', project.id),
                ('date', '=', line_data['date']),
                ('name', '=', line_data['description']),
            ], limit=1)
            
            if existing:
                existing.write({'unit_amount': line_data['hours']})
            else:
                self.env['account.analytic.line'].create({
                    'project_id': project.id,
                    'date': line_data['date'],
                    'name': line_data['description'],
                    'unit_amount': line_data['hours'],
                })
