from flask_restx import Resource,Namespace
from models.metric import Metric
from caching import cache

api = Namespace(name="health-check", description="Its a health check api")

@api.route("")
class CheckHealthy(Resource):
    """Check Health."""

    def get(self):
        ''' Health Check Api '''
        Metric.query.all()
        cache.set("healthcheck", 'healthcheck')
        return "i am healthy", 200
