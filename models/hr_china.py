#-*- coding: utf-8 -*-

import math

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from datetime import datetime
import time

from pprint import pprint


class SpecialWorkingDays(models.Model):
    _name = 'hr_china.special_working_days'

    @api.multi
    def _compute_total_days(self):
        for item in self:
            tot_time = 0
            if item.start_date and item.end_date:
                from_dt = fields.Datetime.from_string(item.start_date)
                to_dt = fields.Datetime.from_string(item.end_date)

                time_delta = to_dt - from_dt
                tot_time = math.ceil(time_delta.days + float(time_delta.seconds) / 86400)
            item.total_days = tot_time + 1

    name = fields.Char(string='Name')
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    total_days = fields.Integer('Total Days', compute=_compute_total_days)


class HRChinaHoliday(models.Model):
    _name = 'hr_china.holiday'
    _description = 'Employee Management (Holiday)'
    _order = 'start_date asc'

    name = fields.Char('Holiday')
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')

    @api.multi
    def _compute_total_days(self):
        for item in self:
            tot_time = 0
            if item.start_date and item.end_date:
                from_dt = fields.Datetime.from_string(item.start_date)
                to_dt = fields.Datetime.from_string(item.end_date)

                time_delta = to_dt - from_dt
                tot_time = math.ceil(time_delta.days + float(time_delta.seconds) / 86400)
            item.total_days = tot_time + 1

    total_days = fields.Integer('Total Days', compute=_compute_total_days)


class HRChinaContractTemplateWorkingTime(models.Model):
    _name = 'hr_china.template_working_time'
    _description = 'List of Employee Working Time'
    _order = 'sequence'

    name = fields.Char(string='Name')
    dayofweek = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], 'Day of Week', required=True, index=True, default='0')
    date_from = fields.Date(string='Starting Date')
    date_to = fields.Date(string='End Date')
    hour_from = fields.Float(string='Work from (Hour)', required=True, index=True, help="Start and End time of working.")
    hour_to = fields.Float(string='Work to (Hour)', required=True)
    sequence = fields.Integer('Sequence')
    break_hours = fields.Integer('Break Hours')
    day_type = fields.Selection([('weekday', 'Weekday'), ('weekend', 'Weekend')])


class HRBenefits(models.Model):
    _name = 'hr_china.benefits'

    @api.multi
    def _get_currency_default(self):
        cny = self.env['res.currency'].search([('name', '=', 'CNY')])
        if cny: return cny.id

    name = fields.Char('Name')
    benefit_type = fields.Selection([('one-time', 'One Time'), ('monthly', 'Monthly'), ('yearly', 'Yearly')], string='Type')
    amount = fields.Float('Amount')
    currency = fields.Many2one('res.currency', string="Currency", default=_get_currency_default)


class HRDeductions(models.Model):
    _name = 'hr_china.deductions'

    @api.multi
    def _get_currency_default(self):
        cny = self.env['res.currency'].search([('name', '=', 'CNY')])
        if cny: return cny.id

    name = fields.Char('Name')
    deduction_type = fields.Selection([('one-time', 'One Time'), ('monthly', 'Monthly'), ('yearly', 'Yearly')],
                                    string='Type')
    amount = fields.Float('Amount')
    currency = fields.Many2one('res.currency', string="Currency", default=_get_currency_default)


class HRContractTemplate(models.Model):
    _name = 'hr_china.contracts_template'

    @api.multi
    def _get_currency_default(self):
        cny = self.env['res.currency'].search([('name', '=', 'CNY')])
        if cny:
            return cny.id

    name = fields.Char('Name')
    wage_type = fields.Many2one('hr_china.wage_type', string='Wage Type', required=True)
    payment_method = fields.Many2one('hr_china.payment_method', string='Payment Method')
    # wage_type = fields.Selection([('hourly', 'Hourly'), ('monthly', 'Monthly')], default="hourly",
    #                              string='Wage Type', required=True)
    monthly_fee = fields.Float(string='Monthly Fee')
    hourly_rate = fields.Float(string='Hourly Rate')
    weekday_daily_fee = fields.Float(string='Weekly Daily Fee')
    weekday_overtime_fee = fields.Float(string='Weekday Overtime Fee')
    weekends_fee = fields.Float(string='Weekends Fee')
    weekends_daily_fee = fields.Float(string='Weekends Daily Fee')
    holiday_fee = fields.Float(string='Holiday Fee')
    holiday_daily_fee = fields.Float(string='Holiday Daily Fee')
    dayoff_deduction = fields.Float(string='Day Off Deduction')
    other_info = fields.Text(string='Additional Information')
    weekend_overtime_fee = fields.Float(string='Weekend Overtime Fee')

    working_time = fields.Many2many('hr_china.template_working_time', string='Working Time')
    benefits_id = fields.Many2many('hr_china.benefits', string='Benefits')
    deductions_id = fields.Many2many('hr_china.deductions', string='Deductions')
    currency_id = fields.Many2one('res.currency', string='Currency', default=_get_currency_default)

    converted_wage_type = fields.Char()
    allowed_leave = fields.Integer(string='Allowed Leave')

    @api.multi
    def _get_wagetype_info(self):
        for item in self:
            item.wage_type_info = ""

    @api.multi
    def _get_currency_info(self):
        for item in self:
            item.currency_info = ""

    @api.multi
    def _get_monthly_info(self):
        for item in self:
            item.monthly_fee_info = "Monthly fixed rate"

    @api.multi
    def _get_dayoff_info(self):
        for item in self:
            item.dayoff_deduction_info = "Day off deduction is calculated in the monthly fee divided by wage type monthly days (22 or 26)"

    @api.multi
    def _get_payment_info(self):
        for item in self:
            item.payment_method_info = ""

    @api.multi
    def _get_weekday_hourly_rate_info(self):
        for item in self:
            item.weekday_hourly_rate_info = "Hourly rate weekdays"

    @api.multi
    def _get_weekday_daily_fee_info(self):
        for item in self:
            item.weekday_daily_fee_info = "The daily rate of the employee (e.i, if hourly rate is 10 multiplied by 8 hours. Daily fee is 80.00)"

    @api.multi
    def _get_weekday_ot_fee_info(self):
        for item in self:
            item.weekday_ot_fee_info = "Overtime rate per hour on regular days (depends on the days of the week you set up in the tab below)"

    @api.multi
    def _get_weekend_hourly_fee_info(self):
        for item in self:
            item.weekend_hourly_rate_info = "Hourly rate of the employee during weekends"

    @api.multi
    def _get_weekend_daily_fee_info(self):
        for item in self:
            item.weekend_daily_fee_info = "The daily rate of the employee during weekends. It will be equivalent to the hourly rate multiplied by the regular work hours"

    @api.multi
    def _get_holiday_fee_info(self):
        for item in self:
            item.holiday_fee_info = "Special rate is given during holidays"

    @api.multi
    def _get_holiday_daily_info(self):
        for item in self:
            item.holiday_daily_fee_info = "The total rate of an employee when they work on holiday"

    @api.multi
    def _get_allowed_leave_info(self):
        for item in self:
            item.allowed_leave_info = "The total allowed leave in a year"

    wage_type_info = fields.Text(compute=_get_wagetype_info)
    currency_info = fields.Text(compute=_get_currency_info)
    monthly_fee_info = fields.Text(compute=_get_monthly_info)
    dayoff_deduction_info = fields.Text(compute=_get_dayoff_info)
    payment_method_info = fields.Text(compute=_get_payment_info)
    weekday_hourly_rate_info = fields.Text(compute=_get_weekday_hourly_rate_info)
    weekday_daily_fee_info = fields.Text(compute=_get_weekday_daily_fee_info)
    weekday_ot_fee_info = fields.Text(compute=_get_weekday_ot_fee_info)
    weekend_hourly_rate_info = fields.Text(compute=_get_weekend_hourly_fee_info)
    weekend_daily_fee_info = fields.Text(compute=_get_weekend_daily_fee_info)
    holiday_fee_info = fields.Text(compute=_get_holiday_fee_info)
    holiday_daily_fee_info = fields.Text(compute=_get_holiday_daily_info)
    allowed_leave_info = fields.Text(compute=_get_allowed_leave_info)

    @api.onchange('wage_type')
    def onchange_wage_type(self):
        for item in self:
            item.converted_wage_type = item.wage_type.wage_type


class HRJobTitles(models.Model):
    _name = 'hr_china.job_titles'

    name = fields.Char('Name')
    department = fields.Many2one('hr.department', string='Department')
    is_active = fields.Boolean('Active', default=True)


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def _get_currency_default(self):
        cny = self.env['res.currency'].search([('name', '=', 'CNY')])
        if cny:
            return cny.id

    first_name = fields.Char('First Name')
    second_name = fields.Char('Second Name')
    middle_name = fields.Char('Middle Name')
    nick_name = fields.Char('Nick Name')

    contact_number = fields.Char('Contact Number')
    emergency_contact_number = fields.Char('Emergency Contact No')
    emergency_contact_name = fields.Char('Emergency Contact Name')
    emergency_contact_relation = fields.Char('Emergency Contact Relation')
    citizenship = fields.Char('Citizenship')
    bank_name = fields.Many2one('hr_china.bank_list', string='Beneficiary Bank')
    bank_branch = fields.Char('Beneficiary Bank Branch')
    account_name = fields.Char('Beneficiary Account Name')
    account_number = fields.Char('Beneficiary Account Number')
    identification_image = fields.Binary('Identification Image')

    contract_template_id = fields.Many2one('hr_china.contracts_template', string='Contract Template ID')
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')

    contract_name = fields.Char()
    c_wage_type = fields.Many2one('hr_china.wage_type', string='Wage Type')
    c_monthly_fee = fields.Float(string='Monthly Fee')
    c_weekday_daily_fee = fields.Float(string='Weekly Daily Fee')
    c_weekday_overtime_fee = fields.Float(string='Weekday Overtime Fee')
    c_weekends_fee = fields.Float(string='Weekends Fee')
    c_weekends_daily_fee = fields.Float(string='Weekends Daily Fee')
    c_holiday_fee = fields.Float(string='Holiday Fee')
    c_holiday_daily_fee = fields.Float(string='Holiday Daily Fee')
    c_hourly_rate = fields.Float(string='Hourly Rate')
    c_dayoff_deduction = fields.Float(string='Day Off Deduction')
    c_other_info = fields.Text(string='Additional Information')
    c_is_contract_active = fields.Boolean()
    c_weekend_overtime_fee = fields.Float(string='Weekend Overtime Fee')

    job_new_id = fields.Many2one('hr_china.job_titles', string='Job Title')
    currency_id = fields.Many2one('res.currency', string='Currency', default=_get_currency_default)
    payment_method = fields.Many2one('hr_china.payment_method', string='Payment Method')

    new_attendance_ids = fields.One2many('hr_china.attendance', 'employee_id', help='List of Attendances for the Employee')
    new_last_attendance_id = fields.Many2one('hr_china.attendance', compute='_new_compute_last_attendance_id')
    new_attendance_state = fields.Selection(string="Attendance", compute='_new_compute_attendance_state',
                                            selection=[('checked_out', "Checked Out"), ('checked_in', "Checked In")],
                                            default='checked_out')
    converted_wage_type = fields.Char()

    @api.multi
    def _get_wagetype_info(self):
        for item in self:
            item.wage_type_info = ""

    @api.multi
    def _get_currency_info(self):
        for item in self:
            item.currency_info = ""

    @api.multi
    def _get_monthly_info(self):
        for item in self:
            item.monthly_fee_info = "Monthly fixed rate"

    @api.multi
    def _get_dayoff_info(self):
        for item in self:
            item.dayoff_deduction_info = "Rate by day to be deducted if absent"

    @api.multi
    def _get_payment_info(self):
        for item in self:
            item.payment_method_info = ""

    @api.multi
    def _get_weekday_hourly_rate_info(self):
        for item in self:
            item.weekday_hourly_rate_info = "Hourly rate weekdays"

    @api.multi
    def _get_weekday_daily_fee_info(self):
        for item in self:
            item.weekday_daily_fee_info = "The daily rate of the employee (e.i, if hourly rate is 10 multiplied by 8 hours. Daily fee is 80.00)"

    @api.multi
    def _get_weekday_ot_fee_info(self):
        for item in self:
            item.weekday_ot_fee_info = "Overtime rate per hour on Regular Days (Monday - Friday)"

    @api.multi
    def _get_weekend_hourly_fee_info(self):
        for item in self:
            item.weekend_hourly_rate_info = "Hourly rate of the employee during weekends"

    @api.multi
    def _get_weekend_daily_fee_info(self):
        for item in self:
            item.weekend_daily_fee_info = "The daily rate of the employee during weekends. It will be equivalent to the hourly rate multiplied by the regular work hours"

    @api.multi
    def _get_holiday_fee_info(self):
        for item in self:
            item.holiday_fee_info = "Special rate is given during holidays"

    @api.multi
    def _get_holiday_daily_info(self):
        for item in self:
            item.holiday_daily_fee = "The total rate of an employee when they work on holiday"

    wage_type_info = fields.Text(compute=_get_wagetype_info)
    currency_info = fields.Text(compute=_get_currency_info)
    monthly_fee_info = fields.Text(compute=_get_monthly_info)
    dayoff_deduction_info = fields.Text(compute=_get_dayoff_info)
    payment_method_info = fields.Text(compute=_get_payment_info)
    weekday_hourly_rate_info = fields.Text(compute=_get_weekday_hourly_rate_info)
    weekday_daily_fee_info = fields.Text(compute=_get_weekday_daily_fee_info)
    weekday_ot_fee_info = fields.Text(compute=_get_weekday_ot_fee_info)
    weekend_hourly_rate_info = fields.Text(compute=_get_weekend_hourly_fee_info)
    weekend_daily_fee_info = fields.Text(compute=_get_weekend_daily_fee_info)
    holiday_fee_info = fields.Text(compute=_get_holiday_fee_info)
    holiday_daily_fee = fields.Text(compute=_get_holiday_daily_info)

    @api.multi
    def _get_payslips_count(self):
        for item in self:
            payslip_count = self.env['hr_china.payslip'].search([('employee_id', '=', item.id)])
            item.payslips_count = len(payslip_count)

    @api.multi
    def _get_contract_count(self):
        for item in self:
            contract_count = self.env['hr_china.contract'].search([('employee_id', '=', item.id)])
            item.contract_count = len(contract_count)

    @api.multi
    def _get_timesheet_count(self):
        for item in self:
            timesheet_count = self.env['hr_china.timesheet'].search([('employee_id', '=', item.id)])
            item.timesheet_count = len(timesheet_count)

    payslips_count = fields.Integer(compute=_get_payslips_count)
    contract_count = fields.Integer(compute=_get_contract_count)
    timesheet_count = fields.Integer(compute=_get_timesheet_count)

    @api.onchange('c_wage_type')
    def onchange_wage_type(self):
        for item in self:
            item.converted_wage_type = item.c_wage_type.wage_type

    @api.depends('new_attendance_ids')
    def _new_compute_last_attendance_id(self):
        for employee in self:
            employee.new_last_attendance_id = employee.new_attendance_ids and employee.new_attendance_ids[0] or False

    @api.depends('new_last_attendance_id')
    def _new_compute_attendance_state(self):
        for employee in self:
            if employee.new_last_attendance_id:
                employee.new_attendance_state = 'checked_out'
                if employee.new_last_attendance_id.check_in_am or employee.new_last_attendance_id.check_in_pm:
                    employee.new_attendance_state = 'checked_in'

                if employee.new_last_attendance_id.check_out_am or employee.new_last_attendance_id.check_out_pm:
                    employee.new_attendance_state = 'checked_out'

    @api.multi
    def _get_active_contract(self):
        for item in self:
            emp_contracts = self.env['hr_china.contract'].search(
                [('employee_id', '=', item.id)], order='start_date DESC')
            active_contract = False
            for empc in emp_contracts:
                if empc.is_contract_active:
                    active_contract = empc.id
                    break
            if active_contract:
                item.active_contract = active_contract

    @api.multi
    def check_contract_status(self):
        for item in self:
            contracts = self.env['hr_china.contract'].search([('employee_id', '=', item.id)], order='id asc', limit=1)
            if contracts:
                start_date = datetime.strptime(contracts.start_date, '%Y-%m-%d %H:%M:%S')
                now = datetime.today()

                years = relativedelta(now, start_date).years

                if years > 0:
                    item.enable_allowed_leave = True
                else:
                    item.enable_allowed_leave = False

    employee_benefit = fields.One2many('hr_china.employee_benefits', 'employee_id', string='Benefits')
    employee_deduction = fields.One2many('hr_china.employee_deductions', 'employee_id', string='Deductions')
    employee_working_time = fields.One2many('hr_china.employee_working_time', 'employee_id', string='Working Time')
    new_contract_id = fields.One2many('hr_china.contract', 'employee_id', string='Contract')
    all_contracts = fields.Many2many('hr_china.contract', string='All Contracts')
    active_contract = fields.Many2one('hr_china.contract', string='Active Contract', compute=_get_active_contract)
    employee_contracts = fields.One2many('hr_china.employee_contract', 'employee_id', string='Contract')
    is_contract_active = fields.Boolean('Contract is Active')
    allowed_leave = fields.Integer('Allowed Leave')
    enable_allowed_leave = fields.Boolean('Enable', default=False, compute=check_contract_status)

    @api.onchange('contract_template_id')
    def contract_templ_change(self):
        templ_contract = self.contract_template_id
        working_time_lines = []
        for working_line in self.contract_template_id.working_time:
            vals = {
                'employee_id': self.id,
                'name': working_line.name,
                'day_type': working_line.day_type,
                'dayofweek': working_line.dayofweek,
                'date_from': working_line.date_from,
                'date_to': working_line.date_to,
                'hour_from': working_line.hour_from,
                'hour_to': working_line.hour_to,
                'break_hours': working_line.break_hours,
            }
            working_time_lines.append((0, 0, vals))

        benefits_lines = []
        for benefit_line in self.contract_template_id.benefits_id:
            vals = {
                'employee_id': self.id,
                'benefits_id': benefit_line.id,
                'benefit_type': benefit_line.benefit_type,
                'amount': benefit_line.amount,
            }
            benefits_lines.append((0, 0, vals))

        deductions_lines = []
        for deduction_line in self.contract_template_id.deductions_id:
            vals = {
                'employee_id': self.id,
                'deductions_id': deduction_line.id,
                'deduction_type': deduction_line.deduction_type,
                'amount': deduction_line.amount,
            }
            deductions_lines.append((0, 0, vals))

        self.employee_benefit = benefits_lines
        self.employee_deduction = deductions_lines
        self.employee_working_time = working_time_lines

        if templ_contract:
            self.contract_name = self.name + " - " + templ_contract.name
            self.currency_id = templ_contract.currency_id
            self.c_wage_type = templ_contract.wage_type.id
            self.c_monthly_fee = templ_contract.monthly_fee
            self.c_hourly_rate = templ_contract.hourly_rate
            self.c_weekday_daily_fee = templ_contract.weekday_daily_fee
            self.c_weekday_overtime_fee = templ_contract.weekday_overtime_fee
            self.c_weekends_fee = templ_contract.weekends_fee
            self.c_holiday_fee = templ_contract.holiday_fee
            self.c_dayoff_deduction = templ_contract.dayoff_deduction
            self.c_other_info = templ_contract.other_info
            self.c_working_time = templ_contract.working_time
            self.c_benefits_id = templ_contract.benefits_id
            self.c_deductions_id = templ_contract.deductions_id
            self.c_weekend_overtime_fee = templ_contract.weekend_overtime_fee
        else:
            self.contract_name = False
            self.currency_id = False
            self.start_date = False
            self.end_date = False
            self.c_wage_type = False
            self.c_monthly_fee = False
            self.c_hourly_rate = False
            self.c_weekday_daily_fee = False
            self.c_weekday_overtime_fee = False
            self.c_weekends_fee = False
            self.c_holiday_fee = False
            self.c_dayoff_deduction = False
            self.c_other_info = False
            self.c_working_time = False
            self.c_benefits_id = False
            self.c_deductions_id = False
            self.c_weekend_overtime_fee = False

    @api.multi
    def write(self, vals):
        ret_val = super(HREmployee, self).write(vals)

        if 'all_contracts' not in vals and 'new_contract_id' not in vals:
            if 'contract_template_id' in vals:

                if vals['contract_template_id']:
                    created_contract = self.env['hr_china.contract'].create({
                        'employee_id': self.id,
                        'name': self.contract_name,
                        'currency_id': self.currency_id.id,
                        'wage_type': self.contract_template_id.wage_type.id,
                        'monthly_fee': self.contract_template_id.monthly_fee,
                        'hourly_rate': self.contract_template_id.hourly_rate,
                        'weekday_daily_fee': self.contract_template_id.weekday_daily_fee,
                        'weekday_overtime_fee': self.contract_template_id.weekday_overtime_fee,
                        'weekends_fee': self.contract_template_id.weekends_fee,
                        'holiday_fee': self.contract_template_id.holiday_fee,
                        'dayoff_deduction': self.contract_template_id.dayoff_deduction,
                        'other_info': self.contract_template_id.other_info,
                        'start_date': self.start_date,
                        'end_date': self.end_date,
                        'contract_template_id': self.contract_template_id.id,
                        'weekend_overtime_fee': self.contract_template_id.weekend_overtime_fee
                    })

                    self.new_contract_id = created_contract
                    self.all_contracts = [[4, created_contract.id]]

                    working_time_lines = []
                    contract_wt = self.env['hr_china.employee_contract'].search([('employee_id', '=', self.id), ('is_active', '=', True)])
                    for working_line in contract_wt.working_time:
                        vals = {
                            'contract_id': created_contract.id,
                            'name': working_line.name,
                            'day_type': working_line.day_type,
                            'dayofweek': working_line.dayofweek,
                            'date_from': working_line.date_from,
                            'date_to': working_line.date_to,
                            'hour_from': working_line.hour_from,
                            'hour_to': working_line.hour_to,
                            'break_hours': working_line.break_hours,
                        }
                        working_time_lines.append((0, 0, vals))

                    if len(working_time_lines) > 0:
                        for oldtime in self.employee_working_time:
                            oldtime.unlink()

                    benefits_lines = []
                    contract_benefits = self.env['hr_china.employee_contract'].search(
                        [('employee_id', '=', self.id), ('is_active', '=', True)])
                    for benefit_line in contract_benefits.benefits_id:
                        vals = {
                            'contract_id': created_contract.id,
                            'benefits_id': benefit_line.benefits_id.id,
                            'benefit_type': benefit_line.benefit_type,
                            'amount': benefit_line.amount,
                        }
                        benefits_lines.append((0, 0, vals))

                    if len(benefits_lines) > 0:
                        for oldbenefits in self.employee_benefit:
                            oldbenefits.unlink()

                    deductions_lines = []
                    contract_deductions = self.env['hr_china.employee_contract'].search(
                        [('employee_id', '=', self.id), ('is_active', '=', True)])
                    for deduction_line in contract_deductions.deductions_id:
                        vals = {
                            'contract_id': created_contract.id,
                            'deductions_id': deduction_line.deductions_id.id,
                            'deduction_type': deduction_line.deduction_type,
                            'amount': deduction_line.amount,
                        }
                        deductions_lines.append((0, 0, vals))

                    if len(deductions_lines) > 0:
                        for olddeduction in self.employee_deduction:
                            olddeduction.unlink()

                    created_contract.benefits_id = benefits_lines
                    created_contract.deductions_id = deductions_lines
                    created_contract.working_time = working_time_lines

        active_cont_dict = {}
        if 'c_holiday_fee' in vals:
            active_cont_dict['holiday_fee'] = vals['c_holiday_fee']
        if 'c_dayoff_deduction' in vals:
            active_cont_dict['dayoff_deduction'] = vals['c_dayoff_deduction']
        if 'c_wage_type' in vals:
            active_cont_dict['wage_type'] = vals['c_wage_type']
        if 'c_monthly_fee' in vals:
            active_cont_dict['monthly_fee'] = vals['c_monthly_fee']
        if 'c_hourly_rate' in vals:
            active_cont_dict['hourly_rate'] = vals['c_hourly_rate']
        if 'c_weekday_daily_fee' in vals:
            active_cont_dict['weekday_daily_fee'] = vals['c_weekday_daily_fee']
        if 'c_weekday_overtime_fee' in vals:
            active_cont_dict['weekday_overtime_fee'] = vals['c_weekday_overtime_fee']
        if 'c_weekends_fee' in vals:
            active_cont_dict['weekends_fee'] = vals['c_weekends_fee']
        if 'start_date' in vals:
            active_cont_dict['start_date'] = vals['start_date']
        if 'end_date' in  vals:
            active_cont_dict['end_date'] = vals['end_date']
        if 'is_contract_active' in vals:
            active_cont_dict['is_contract_active'] = vals['is_contract_active']
        if 'c_weekend_overtime_fee' in vals:
            active_cont_dict['weekend_overtime_fee'] = vals['c_weekend_overtime_fee']

        if len(active_cont_dict) > 0:
            self.new_contract_id.write(active_cont_dict)

        return ret_val


class HRChinaContract(models.Model):
    _name = 'hr_china.contract'
    _order = 'id'

    @api.multi
    def _check_contract_status(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                if datetime.strptime(rec.start_date, "%Y-%m-%d %H:%M:%S") <= datetime.now() <= \
                        datetime.strptime(rec.end_date, "%Y-%m-%d %H:%M:%S"):
                    rec.is_contract_active = 'active'
                    rec.active = True
                else:
                    rec.is_contract_active = 'expired'
                    rec.active = False

    @api.multi
    def _get_currency_default(self):
        cny = self.env['res.currency'].search([('name', '=', 'CNY')])
        if cny:
            return cny.id

    employee_id = fields.Many2one('hr.employee', string='Employee')
    active = fields.Boolean(string='Active', default=True)
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    contract_template_id = fields.Many2one('hr_china.contracts_template')
    #is_contract_active = fields.Boolean('Contract is Active', compute=_check_contract_status)
    is_contract_active = fields.Selection([('expired', 'Expired'), ('active', 'Active')])
    name = fields.Char('Name')
    # wage_type = fields.Selection([('hourly', 'Hourly'), ('monthly', 'Monthly')], default="hourly",
    #                              string='Wage Type')
    wage_type = fields.Many2one('hr_china.wage_type', string='Wage Type')
    monthly_fee = fields.Float(string='Monthly Fee')
    weekday_daily_fee = fields.Float(string='Weekly Daily Fee')
    weekday_overtime_fee = fields.Float(string='Weekday Overtime Fee')
    weekends_fee = fields.Float(string='Weekends Fee')
    holiday_fee = fields.Float(string='Holiday Fee')
    dayoff_deduction = fields.Float(string='Day Off Deduction')
    other_info = fields.Text(string='Additional Information')
    weekend_overtime_fee = fields.Float(string='Weekend Overtime Fee')

    working_time = fields.One2many('hr_china.contract_working_time', 'contract_id',
                                   string='Working Time')
    benefits_id = fields.One2many('hr_china.contract_benefits', 'contract_id',
                                  string='Benefits')
    deductions_id = fields.One2many('hr_china.contract_deductions', 'contract_id',
                                    string='Deductions')
    currency_id = fields.Many2one('res.currency', string='Currency')


class ZuluHREmployeeContract(models.Model):
    _name = 'hr_china.employee_contract'
    _order = 'id desc'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    contract_template_id = fields.Many2one('hr_china.contracts_template', string='Contract Template ID')
    name = fields.Char('Name')
    wage_type = fields.Many2one('hr_china.wage_type', string='Wage Type')
    monthly_fee = fields.Float(string='Monthly Fee')
    weekday_daily_fee = fields.Float(string='Weekly Daily Fee')
    weekday_overtime_fee = fields.Float(string='Weekday Overtime Fee')
    weekends_fee = fields.Float(string='Weekends Fee')
    weekends_daily_fee = fields.Float(string='Weekends Daily Fee')
    holiday_fee = fields.Float(string='Holiday Fee')
    holiday_daily_fee = fields.Float(string='Holiday Daily Fee')
    hourly_rate = fields.Float(string='Hourly Rate')
    dayoff_deduction = fields.Float(string='Day Off Deduction')
    other_info = fields.Text(string='Additional Information')

    working_time = fields.One2many('zulu_hr.active_contract_work_time', 'employee_id', string='Working Time')
    benefits_id = fields.One2many('zulu_hr.active_contract_benefits', 'employee_id', string='Benefits')
    deductions_id = fields.One2many('zulu_hr.active_contract_deductions', 'employee_id', string='Deductions')
    currency_id = fields.Many2one('res.currency', string='Currency')
    payment_method = fields.Many2one('hr_china.payment_method', string='Payment Method')

    @api.multi
    def check_contract_status(self):
        for item in self:
            contracts = self.env['hr_china.employee_contract'].search([('employee_id', '=', item.id),
                                                                       ('is_active', '=', True)], limit=1)
            if contracts:
                start_date = datetime.strptime(contracts.start_date, '%Y-%m-%d %H:%M:%S')
                now = datetime.today()

                years = relativedelta(now, start_date).years

                if years > 0:
                    item.enable_allowed_leave = True
                else:
                    item.enable_allowed_leave = False

    is_active = fields.Boolean('Active', default=True)
    converted_wage_type = fields.Char()
    allowed_leave = fields.Integer('Allowed Leave')
    enable_allowed_leave = fields.Boolean('Enable', default=False, compute=check_contract_status)

    @api.constrains('is_active')
    def change_active_status(self):
        if self.is_active:
            records = self.env['hr_china.employee_contract'].search([('id', '!=', self.id)])
            for rec in records:
                rec.is_active = False
            employee = self.env['hr.employee'].browse(int(self.employee_id.id))
            employee.write({
                'contract_template_id': self.contract_template_id.id,
                'c_wage_type': self.wage_type.id,
                'currency_id': self.currency_id.id,
                'payment_method': self.payment_method.id,
                'start_date': self.start_date,
                'end_date': self.end_date
            })

        working_time_lines = []
        for working_line in self.working_time:
            vals = {
                'employee_id': self.employee_id.id,
                'name': working_line.name,
                'day_type': working_line.day_type,
                'dayofweek': working_line.dayofweek,
                'date_from': working_line.date_from,
                'date_to': working_line.date_to,
                'hour_from': working_line.hour_from,
                'hour_to': working_line.hour_to,
                'break_hours': working_line.break_hours,
            }
            working_time_lines.append((0, 0, vals))

        benefits_line = []
        for benefit_line in self.benefits_id:
            vals = {
                'employee_id': self.employee_id.id,
                'benefits_id': benefit_line.benefits_id.id,
                'benefit_type': benefit_line.benefit_type,
                'amount': benefit_line.amount,
            }
            benefits_line.append((0, 0, vals))

        deductions_lines = []
        for deduction_line in self.deductions_id:
            vals = {
                'employee_id': self.employee_id.id,
                'deductions_id': deduction_line.deductions_id.id,
                'deduction_type': deduction_line.deduction_type,
                'amount': deduction_line.amount,
            }
            deductions_lines.append((0, 0, vals))

        self.employee_id.employee_benefit = benefits_line
        self.employee_id.employee_deduction = deductions_lines
        self.employee_id.employee_working_time = working_time_lines

    @api.onchange('wage_type')
    def onchange_wage_type(self):
        for item in self:
            item.converted_wage_type = item.wage_type.wage_type

    @api.onchange('contract_template_id')
    def contract_templ_change(self):
        templ_contract = self.contract_template_id
        working_time_lines = []
        for working_line in self.contract_template_id.working_time:
            vals = {
                'employee_id': self.employee_id.id,
                'name': working_line.name,
                'day_type': working_line.day_type,
                'dayofweek': working_line.dayofweek,
                'date_from': working_line.date_from,
                'date_to': working_line.date_to,
                'hour_from': working_line.hour_from,
                'hour_to': working_line.hour_to,
                'break_hours': working_line.break_hours,
            }
            working_time_lines.append((0, 0, vals))

        benefits_lines = []
        for benefit_line in self.contract_template_id.benefits_id:
            vals = {
                'employee_id': self.employee_id.id,
                'benefits_id': benefit_line.id,
                'benefit_type': benefit_line.benefit_type,
                'amount': benefit_line.amount,
            }
            benefits_lines.append((0, 0, vals))

        deductions_lines = []
        for deduction_line in self.contract_template_id.deductions_id:
            vals = {
                'employee_id': self.employee_id.id,
                'deductions_id': deduction_line.id,
                'deduction_type': deduction_line.deduction_type,
                'amount': deduction_line.amount,
            }
            deductions_lines.append((0, 0, vals))

        self.benefits_id = benefits_lines
        self.deductions_id = deductions_lines
        self.working_time = working_time_lines

        if templ_contract:
            self.name = self.employee_id.name + " - " + templ_contract.name
            self.currency_id = templ_contract.currency_id
            self.wage_type = templ_contract.wage_type.id
            self.monthly_fee = templ_contract.monthly_fee
            self.hourly_rate = templ_contract.hourly_rate
            self.weekday_daily_fee = templ_contract.weekday_daily_fee
            self.weekday_overtime_fee = templ_contract.weekday_overtime_fee
            self.weekends_fee = templ_contract.weekends_fee
            self.holiday_fee = templ_contract.holiday_fee
            self.dayoff_deduction = templ_contract.dayoff_deduction
            self.other_info = templ_contract.other_info

        else:
            self.name = False
            self.currency_id = False
            self.start_date = False
            self.end_date = False
            self.wage_type = False
            self.monthly_fee = False
            self.hourly_rate = False
            self.weekday_daily_fee = False
            self.weekday_overtime_fee = False
            self.weekends_fee = False
            self.holiday_fee = False
            self.dayoff_deduction = False
            self.other_info = False

    # @api.multi
    # def write(self, vals):
    #     ret_val = super(ZuluHREmployeeContract, self).write(vals)
    #     pprint("############################################")
    #     pprint(vals)
    #     if 'employee_id' in vals:
    #         employee = self.env['hr.employee'].browse(int(vals['employee_id']))
    #         employee.write({
    #             'contract_template_id': vals['contract_template_id'],
    #             'c_wage_type': vals['wage_type'],
    #             'currency_id': vals['currency_id'],
    #             'payment_method': vals['payment_method'],
    #             'start_date': vals['start_date'],
    #             'end_date': vals['end_date']
    #         })
    #
    #     return ret_val


class HRChinaContractBenefits(models.Model):
    _name = 'hr_china.contract_benefits'

    @api.multi
    def _get_currency_default(self):
        cny = self.env['res.currency'].search([('name', '=', 'CNY')])
        if cny:
            return cny.id

    contract_id = fields.Many2one('hr_china.contract', string='Contract')
    benefit_type = fields.Selection([('one-time', 'One Time'), ('monthly', 'Monthly'), ('yearly', 'Yearly')],
                                    string='Type')
    benefits_id = fields.Many2one('hr_china.benefits', string='Name')
    amount = fields.Float('Amount')
    currency = fields.Many2one('res.currency', string="Currency", default=_get_currency_default)


class HRChinaContractDeductions(models.Model):
    _name = 'hr_china.contract_deductions'

    @api.multi
    def _get_currency_default(self):
        cny = self.env['res.currency'].search([('name', '=', 'CNY')])
        if cny:
            return cny.id

    contract_id = fields.Many2one('hr_china.contract', string='Contract')
    deduction_type = fields.Selection([('one-time', 'One Time'), ('monthly', 'Monthly'), ('yearly', 'Yearly')],
                                      string='Type')
    deductions_id = fields.Many2one('hr_china.deductions', string='Name')
    amount = fields.Float('Amount')
    currency = fields.Many2one('res.currency', string="Currency", default=_get_currency_default)


class HRChinaContractWorkingTime(models.Model):
    _name = 'hr_china.contract_working_time'

    contract_id = fields.Many2one('hr_china.contract', string='Contract')
    name = fields.Char(string='Name')
    dayofweek = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], 'Day of Week', required=True, index=True, default='0')
    date_from = fields.Date(string='Starting Date')
    date_to = fields.Date(string='End Date')
    hour_from = fields.Float(string='Work from', required=True, index=True, help="Start and End time of working.")
    hour_to = fields.Float(string='Work to', required=True)
    break_hours = fields.Integer('Break Hours')
    day_type = fields.Selection([('weekday', 'Weekday'), ('weekend', 'Weekend')])


class HRChinaEmployeeBenefits(models.Model):
    _name = 'hr_china.employee_benefits'
    _description = 'List of Employee Benefits'

    @api.multi
    def _get_currency_default(self):
        cny = self.env['res.currency'].search([('name', '=', 'CNY')])
        if cny:
            return cny.id

    @api.onchange('benefits_id')
    def onchange_benefits_id(self):
        if self.benefits_id:
            self.benefits_id = self.benefits_id.id
            self.benefit_type = self.benefits_id.benefit_type
            self.amount = self.benefits_id.amount
            self.currency = self.benefits_id.currency

    employee_id = fields.Many2one('hr.employee', string='Employee')
    contract_id = fields.Many2one('hr_china.contract', string='Contract')
    benefit_type = fields.Selection([('one-time', 'One Time'), ('monthly', 'Monthly'), ('yearly', 'Yearly')],
                                    string='Type')
    benefits_id = fields.Many2one('hr_china.benefits', string='Name')
    amount = fields.Float('Amount')
    currency = fields.Many2one('res.currency', string="Currency", default=_get_currency_default)


class HRChinaEmployeeDeductions(models.Model):
    _name = 'hr_china.employee_deductions'
    _description = 'List of Employee Salary Deductions'

    @api.multi
    def _get_currency_default(self):
        cny = self.env['res.currency'].search([('name', '=', 'CNY')])
        if cny:
            return cny.id

    @api.onchange('deductions_id')
    def onchange_deductions_id(self):
        if self.deductions_id:
            self.deductions_id = self.deductions_id.id
            self.deduction_type = self.deductions_id.deduction_type
            self.amount = self.deductions_id.amount
            self.currency = self.deductions_id.currency

    employee_id = fields.Many2one('hr.employee', string='Employee')
    contract_id = fields.Many2one('hr_china.contract', string='Contract')
    deduction_type = fields.Selection([('one-time', 'One Time'), ('monthly', 'Monthly'), ('yearly', 'Yearly')],
                                      string='Type')
    deductions_id = fields.Many2one('hr_china.deductions', string='Name')
    amount = fields.Float('Amount')
    currency = fields.Many2one('res.currency', string="Currency", default=_get_currency_default)


class HRChinaEmployeeWorkingTime(models.Model):
    _name = 'hr_china.employee_working_time'
    _description = 'List of Employee Working Time'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    contract_id = fields.Many2one('hr_china.contract', string='Contract')
    name = fields.Char(string='Name')
    dayofweek = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], 'Day of Week', required=True, index=True, default='0')
    date_from = fields.Date(string='Starting Date')
    date_to = fields.Date(string='End Date')
    hour_from = fields.Float(string='Work from', required=True, index=True, help="Start and End time of working.")
    hour_to = fields.Float(string='Work to', required=True)
    break_hours = fields.Integer('Break Hours')
    day_type = fields.Selection([('weekday', 'Weekday'), ('weekend', 'Weekend')], string="Type of Day")


class ZuluHRActiveContractBenefits(models.Model):
    _name = 'zulu_hr.active_contract_benefits'

    @api.multi
    @api.multi
    def _get_currency_default(self):
        cny = self.env['res.currency'].search([('name', '=', 'CNY')])
        if cny:
            return cny.id

    @api.onchange('benefits_id')
    def onchange_benefits_id(self):
        if self.benefits_id:
            self.benefits_id = self.benefits_id.id
            self.benefit_type = self.benefits_id.benefit_type
            self.amount = self.benefits_id.amount
            self.currency = self.benefits_id.currency

    employee_id = fields.Many2one('hr.employee', string='Employee')
    contract_id = fields.Many2one('hr_china.contract', string='Contract')
    benefit_type = fields.Selection([('one-time', 'One Time'), ('monthly', 'Monthly'), ('yearly', 'Yearly')],
                                    string='Type')
    benefits_id = fields.Many2one('hr_china.benefits', string='Name')
    amount = fields.Float('Amount')
    currency = fields.Many2one('res.currency', string="Currency", default=_get_currency_default)


class ZuluHRActiveContractDeductions(models.Model):
    _name = 'zulu_hr.active_contract_deductions'

    @api.multi
    def _get_currency_default(self):
        cny = self.env['res.currency'].search([('name', '=', 'CNY')])
        if cny:
            return cny.id

    @api.onchange('deductions_id')
    def onchange_deductions_id(self):
        if self.deductions_id:
            self.deductions_id = self.deductions_id.id
            self.deduction_type = self.deductions_id.deduction_type
            self.amount = self.deductions_id.amount
            self.currency = self.deductions_id.currency

    employee_id = fields.Many2one('hr.employee', string='Employee')
    contract_id = fields.Many2one('hr_china.contract', string='Contract')
    deduction_type = fields.Selection([('one-time', 'One Time'), ('monthly', 'Monthly'), ('yearly', 'Yearly')],
                                      string='Type')
    deductions_id = fields.Many2one('hr_china.deductions', string='Name')
    amount = fields.Float('Amount')
    currency = fields.Many2one('res.currency', string="Currency", default=_get_currency_default)


class ZuluHRActiveContractWorkTime(models.Model):
    _name = 'zulu_hr.active_contract_work_time'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    contract_id = fields.Many2one('hr_china.contract', string='Contract')
    name = fields.Char(string='Name')
    dayofweek = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], 'Day of Week', required=True, index=True, default='0')
    date_from = fields.Date(string='Starting Date')
    date_to = fields.Date(string='End Date')
    hour_from = fields.Float(string='Work from', required=True, index=True, help="Start and End time of working.")
    hour_to = fields.Float(string='Work to', required=True)
    break_hours = fields.Integer('Break Hours')
    day_type = fields.Selection([('weekday', 'Weekday'), ('weekend', 'Weekend')], string="Type of Day")


class HRChinaAttendance(models.Model):
    _inherit = 'hr.employee'

    def show_emp_attendance(self):
        return {
            'name': 'Attendance',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'hr_china.attendance',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'self',
            'context': {
                'search_default_employee_id': self.id
            }
        }

    # def show_emp_attendance(self):
    #     return {
    #         'name': 'Attendance',
    #         'view_type': 'form',
    #         'view_mode': 'tree',
    #         'res_model': 'hr.attendance',
    #         'view_id': False,
    #         'type': 'ir.actions.act_window',
    #         'target': 'self',
    #         'context': {
    #             'search_default_employee_id': self.id
    #         }
    #     }