"""Common error model"""
from flask_restx import fields, Model

CommonError = Model("CommonError",{
    'error-code': fields.String(required=True),
    'error-auxiliary': fields.String(required=True),
    'error-message': fields.String(required=True),
    })

def common_error_response(api):
    """common_error_response"""
    api.models[CommonError.name] = CommonError
    return CommonError
