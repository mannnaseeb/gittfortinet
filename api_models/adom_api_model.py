from flask_restx import  fields, Model


class AdomModel:
    """AdomModel"""

    # -------------- For all adoms --------------
    AllAdoms = Model('AllAdoms', {
        'name': fields.String(required=True),
        'description': fields.String(required=True),
        'state': fields.Integer(required=True),
        'os_version': fields.Integer(required=True),
        'restricted_prds': fields.Integer(required=True),
        'uuid': fields.String(required=True),
        'create_time': fields.Integer(required=True),

    })
    AllAdomsData = Model('AllAdomsData', {
        'data': fields.List(fields.Nested(AllAdoms)),
        'count': fields.Integer(),

    })


    @staticmethod
    def alladoms(api):
        """alladoms"""
        api.models[AdomModel.AllAdoms.name] = AdomModel.AllAdoms
        return AdomModel.AllAdoms

    @staticmethod
    def alladomsdata(api):
        """alladomsdata"""
        api.models[AdomModel.AllAdoms.name] = AdomModel.AllAdoms
        api.models[AdomModel.AllAdomsData.name] = AdomModel.AllAdomsData
        return AdomModel.AllAdomsData
    # --------- For all adoms ENDS HERE ---------


class AdombyNameModel:
    """AdombyNameModel"""


    Adomsbyname = Model('Adomsbyname', {
        'name': fields.String(required=True),
        'description': fields.String(required=True),
        'state': fields.Integer(required=True),
        'os_version': fields.Integer(required=True),
        'restricted_prds': fields.Integer(required=True),
        'uuid': fields.String(required=True),
        'create_time': fields.Integer(required=True),
    })

    AdomsbynameData = Model('AdomsbynameData', {
        'data': fields.List(fields.Nested(Adomsbyname)),
        'count': fields.Integer(),

    })

    @staticmethod
    def adomname(api):
        """adomname"""
        api.models[AdombyNameModel.Adomsbyname.name] = AdombyNameModel.Adomsbyname
        return AdombyNameModel.Adomsbyname

    @staticmethod
    def adomsbynamedata(api):
        """adomsbynamedata"""
        api.models[AdombyNameModel.Adomsbyname.name] = AdombyNameModel.Adomsbyname
        api.models[AdombyNameModel.AdomsbynameData.name] = AdombyNameModel.AdomsbynameData
        return AdombyNameModel.AdomsbynameData


class AdomidModel:
    """AdomidModel"""

    # -------------- For all adoms --------------

    Vdom = Model('Vdom', {
        'comments': fields.String(required=True),
        'device_id': fields.String(required=True),
        'ext_flags': fields.Integer(required=True),
        'flags': fields.Integer(required=True),
        'name': fields.String(required=True),
        'node_flags': fields.String(required=True),
        'oid': fields.Integer(required=True),
        'opmode': fields.Integer(required=True),
        'rtm_prof_id': fields.Integer(required=True),
        'status': fields.String(required=True),
        'tab_status': fields.String(required=True),
        'vpn_id': fields.Integer(required=True),
    })

    AdomId = Model('AdomId', {
        'application_version': fields.String(required=True),
        'antivirus_version': fields.String(rrequired=True),
        'config_status': fields.Integer(required=True),
        'connection_mode': fields.Integer(required=True),
        'connection_status': fields.Integer(required=True),
        'db_status': fields.Integer(required=True),
        'description': fields.String(required=True),
        'hdisk_size': fields.Integer(required=True),
        'hostname': fields.String(required=True),
        'ip_address': fields.String(required=True),

        'ips_version': fields.String(required=True),
        'last_checked': fields.Integer(required=True),
        'last_resync': fields.Integer(required=True),
        'latitude': fields.String(required=True),
        'longitude': fields.String(required=True),

        'logdisk_size': fields.Integer(required=True),
        'maxvdom': fields.Integer(required=True),
        'mgmt_id': fields.Integer(required=True),
        'mgmt_interface': fields.String(required=True),
        'mgmt_mode': fields.Integer(required=True),
        'mgt_vdom': fields.String(required=True),
        'name': fields.String(required=True),
        'oid': fields.Integer(required=True),
        'os_type': fields.Integer(required=True),
        'os_version': fields.Integer(required=True),
        'patch': fields.Integer(required=True),
        'platform': fields.String(required=True),

        'serial_number': fields.String(required=True),
        'source': fields.Integer(required=True),
        'tunnel_ip': fields.String(required=True),
        'version': fields.Integer(required=True),
        'vm_cpu': fields.Integer(required=True),
        'vm_cpu_limit': fields.Integer(required=True),
        'vm_lic_expire': fields.Integer(required=True),
        'vm_memory': fields.Integer(required=True),
        'vm_memory_limit': fields.Integer(required=True),
        'vm_status': fields.Integer(required=True),

        'vdom': fields.List((fields.Nested(Vdom))),

    })

    AdomsidData = Model('AdomsidData', {
        'data': fields.List(fields.Nested(AdomId)),
        'count': fields.Integer(),

    })
    # --------- For all adoms ENDS HERE ---------

    @staticmethod
    def adomid(api):
        """adomid"""
        api.models[AdomidModel.AdomId.name] = AdomidModel.AdomId
        return AdomidModel.AdomId

    @staticmethod
    def adomsbynamedata(api):
        """adomsbynamedata"""
        api.models[AdomidModel.AllAdoms.name] = AdomidModel.AllAdoms
        api.models[AdomidModel.AdomsidData.name] = AdomidModel.AdomsidData
        return AdomidModel.AdomsidData

    @staticmethod
    def adom_id_response(api):
        """adom_id_response"""
        api.models[AdomidModel.Vdom.name] = AdomidModel.Vdom
        api.models[AdomidModel.AdomId.name] = AdomidModel.AdomId
        api.models[AdomidModel.AdomsidData.name] = AdomidModel.AdomsidData
        return AdomidModel.AdomsidData

class SystemStatusModel:
    """SystemStatusModel"""

    # -------------- For all adoms --------------

    Status = Model('Status', {
        'policy-package': fields.String(required=True, attribute = 'pkg'),
        'policy-status': fields.String(required=True, attribute = 'status')

        })

    @staticmethod
    def system_status_data(api):
        """system status data"""
        api.models[SystemStatusModel.Status.name] = SystemStatusModel.Status
        return SystemStatusModel.Status
