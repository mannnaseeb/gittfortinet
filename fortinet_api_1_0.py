from flask import Blueprint
from flask_restx import Api

from apis.adom_api import api as adom_ns
from apis.metrics_api import api as metrics_ns
# from apis.report_api import api as report_ns
from apis.health_check import api as health_check_ns
from apis.report import api as report_ns2

#add authorization in swagger security
authorizations = {
    "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "name": "Authorization"
        },
}

blueprint = Blueprint('fortinet_api_v1', __name__, url_prefix='/api/v1/')
api = Api(blueprint,
          title='Fortinet API v1',
          version='1.0',
          description='This is version 1.0 for fortinet Api',
          security='Bearer Auth',
          authorizations=authorizations
          )

api.add_namespace(adom_ns)
api.add_namespace(metrics_ns)
# api.add_namespace(report_ns)
api.add_namespace(health_check_ns)
api.add_namespace(report_ns2)
