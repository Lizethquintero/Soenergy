# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID
import pyotp

from . import models
from . import controllers

def calculate_otp_code(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    users = env['res.users'].search([])
    for user in users:
        code = pyotp.random_base32()
        user.otp_secret = code
        user.twoFA_code = pyotp.random_base32()