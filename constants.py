import os
from fortinet_common import auth
FORTINET_MANAGER_BASE_URL = os.environ.get("FORTINET_MANAGER_BASE_URL")
FORTINET_MANAGER_CREDENTIAL_UUID = os.environ.get("FORTINET_MANAGER_CREDENTIAL_UUID")
FORTINET_ANAYLYZER_BASE_URL = os.environ.get("FORTINET_ANAYLYZER_BASE_URL")
FORTINET_ANAYLYZER_CREDENTIAL_UUID = os.environ.get("FORTINET_ANAYLYZER_CREDENTIAL_UUID")
CLIENT_API_BASE_URL = os.environ.get("CLIENT_API_BASE_URL")
CLIENT_API_CREDENTIAL_UUID = os.environ.get("CLIENT_API_CREDENTIAL_UUID")
FORTINET_IM_SERVER_BASE_URL = os.environ.get("FORTINET_IM_SERVER_BASE_URL")
FORTINET_IM_SERVER_GET_USER_URL = '/protocol/openid-connect/userinfo'
FORTINET_IM_SERVER_USERNAME = os.environ.get("FORTINET_IM_SERVER_USERNAME")
FORTINET_IM_SERVER_PASSWORD = os.environ.get("FORTINET_IM_SERVER_PASSWORD")
FORTINET_IM_SERVER_GRANT_TYPE = os.environ.get("FORTINET_IM_SERVER_GRANT_TYPE")
FORTINET_IM_SERVER_CLIENT_ID = os.environ.get("FORTINET_IM_SERVER_CLIENT_ID")
FORTINET_IM_SERVER_TOKEN_GENERATION = FORTINET_IM_SERVER_BASE_URL + "/protocol/openid-connect/token"
MANAGER_API_CACHE_TIMEOUT = os.environ.get("MANAGER_API_CACHE_TIMEOUT",None)
# METRIC_NAMES = dict()

# --------------------- Status Code ---------------------
SUCCESS_CODE = 200
ERROR_CODE_BAD_REQUEST = 400
ERROR_CODE_UNAUTHORIZED_ACCESS = 401
ERROR_CODE_INTERNAL_SERVER_ERROR = 500
NO_CONTENT = 204
# --------------------- Status Messages ---------------------
SUCCESS_MESSAGE = "Success"
ERROR_CODE_BAD_REQUEST_MESSAGE = "Bad Request"
ERROR_CODE_UNAUTHORIZED_ACCESS_MESSAGE = "Unauthorized"
ERROR_CODE_INTERNAL_SERVER_ERROR_MESSAGE = "Internal Server Error"
ERROR_REPORT_METADATA_SAVE_FAILED = 'An error occured while saving report meta data'
ERROR_INVALID_REPORT_STATUS_REQUEST = 'Invalid status request the report does not exist for the specified tid'
ERROR_INVALID_REPORT_DOWNLOAD_REQUEST = 'Invalid download request the report does not exist for the specified tid'

ERROR_REPORT_METADATA_SAVE_FAILED = 'An error occured while saving report meta data'
ERROR_REPORT_DELETE_FAILED = 'An error occured while deleting report in database'
ERROR_INVALID_REPORT_STATUS_REQUEST = 'Invalid status request the report does not exist for the specified tid'
ERROR_INVALID_REPORT_DOWNLOAD_REQUEST = 'Invalid download request the report does not exist for the specified tid'
NO_CONTENT_MESSAGE = 'No Content'
ERROR_REPORT_METADATA_SAVE_FAILED = 'An error occured while saving report meta data'
ERROR_INVALID_REPORT_STATUS_REQUEST = 'The requested tid was not found'
ERROR_INVALID_REPORT_DOWNLOAD_REQUEST = 'The requested tid was not found'
ERROR_REPORT_IS_DELETED = 'Invalid request the report was deleted'

# -------------- input payload options -------------
SORT_BY_ORDER = 'order'

SORT_BY_OPTIONS = dict()

FILTER_BY_OPTIONS = dict()

VALID_OPERATIONS = list()

VALID_ORDER = {'order': ['asc', 'desc']}

# --------- input payload options ENDS HERE --------
INPUT_PAYLOAD_MIN_LIMIT = 1
INPUT_PAYLOAD_MAX_LIMIT = 500
# --------- input payload options ENDS HERE --------

# -------------- Default Values -------------
DEFAULT_DEVICE_ID = 'All_FortiGate'
DEFAULT_LIMIT_VALUE = 50
APP_CATEGORY_NOT_SCANNED = 'Not.Scanned'
LINK_QUALITY_STATUS_FILTER_BY_INTERFACE = 'interface'
BANDWIDTH_SUMMARY_FILTER_BY_INTERFACE = 'interface'
BANDWIDTH_SUMMARY_FILTER_BY_DEVICE_ID = 'devid'
SLA_MONITOR_FILTER_BY_DEVICE_ID = 'devid'
TYPE_FORTIGATE_MANAGER = 'Fortigate Manager'
TYPE_FORTIGATE_ANALYZER = 'Fortigate Analyzer'
FILTER_BY_DEVICE_ID = 'devid'
FILTER_BY_CLIENT_ID = 'client-id'
FILTER_BY_SITE_STATUS = 'site_status'
FILTER_BY_DEVICE_STATUS = 'device_status'
PERMITTED_STATUS_SITE_DETAILS = ['up', 'down', 'alert']
RISK_ANALYSIS_LEVELS = {"low": 1, "guarded": 2, "elevated": 2, "medium": 3, "high" : 4,  "severe" : 5, "critical" : 5}
DEVID_OPERATOR = "="
# --------- Default Values ENDS HERE --------


ADOM_NAME = "CloudSmartz"
ADOM_NAME_ERROR_CODE_IN_MANAGER = 9006
ADOM_NAME_ERROR_CODE_IN_ANALYZER = 9006

ACCEPTED_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
EPOCH_TO_DATETIME_FORMAT = "%Y-%m-%d %H:%M"
ADOM_EPOCH_TO_DATETIME_FORMAT = "%Y/%m/%d %H:%M"

# --------------------- Widget API related constants ---------------------
WIDGET_SITE_DETAILS = 'site-details'
WIDGET_TOP_APPLICATION_THREATS = 'top-application-threats'
WIDGET_TOP_APPLICATIONS = 'top-applications'
WIDGET_TRAFFIC_SUMMARY = 'traffic-summary'
WIDGET_RESOURCE_USAGE = 'resource-usage'
WIDGET_TOP_USERS = 'top-users'
WIDGET_TOP_DESTINATIONS = 'top-destinations'
WIDGET_BANDWIDTH_RATE = "bandwidth-rate"
WIDGET_SITE_MAP = "site-map"
WIDGET_TOP_APPLICATIONS_USAGE = 'top-application-usage'
WIDGET_APPLICATION_CATEGORIES = 'top-application-categories'
WIDGET_TOP_SOURCES_BY_BANDWIDTH = 'top-sources'
WIDGET_RISK_ANALYSIS = "risk-analysis"
RISK_ANALYSIS_DEFAULT_FILTER = "apprisk=*"
WIDGET_LINK_QUALITY_STATUS = "link-quality-status"
WIDGET_TOP_POLICY_HITS = "top-policy-hits"
WIDGET_SD_WAN_USAGE = "sd-wan-usage"
WIDGET_BANDWIDTH_SUMMARY = 'bandwidth-summary'
WIDGET_SLA_PERFORMANCE = 'sla-performance'
WIDGET_TOP_THREATS = 'top-threats'
# ---------------- Widget API related constants ENDS HERE ----------------

# --------------------- Validation layer constants ---------------------
PROVIDE_VALID_FILTER_OPTION = "Please provide a valid option for filter"
PROVIDE_VALID_FILTER_VALUE = "Please provide a valid value for filter"
PROVIDE_VALID_FILTER_STRUCTURE = "Please provide filter with expected structure"
PROVIDE_VALID_FILTER_OPERATION = "Please provide a valid option for filter operation"
PROVIDE_VALID_FILTER_KEY = "Please provide a valid option for filter key"
PROVIDE_VALID_LIMIT_TYPE = "Please provide a proper number for limit"
PROVIDE_VALID_TIME_RANGE_TYPE = "Please provide a valid time range object"
PROVIDE_START_AND_END_TIME = "Please provide both start and end time"
PROVIDE_START_TIME = "Please provide start time"
PROVIDE_END_TIME = "Please provide end time"
PROVIDE_SAME_DATE_FORMATS = 'Please ensure that the date formats for the dates provided are the same'
PROVIDE_VALID_RANGE = 'Please check the range of your dates provided'
PROVIDE_TIME_RANGE = "Please provide a time range"
PROVIDE_SORT_BY = "Please provide a sort by"
SORT_BY_NOT_SUPPORTED = "Sort by is not supported"
FILTER_NOT_SUPPORTED = "Filter is not supported"
PROVIDE_FILTER= "Please provide filter"
LIMIT_NOT_SUPPORTED = "Limit is not supported"
PROVIDE_FIELD_AND_ORDER_SORT_BY = "Please provide both field and order"
PROVIDE_VALID_DEVICE = "Please provide a valid option for device"
PROVIDE_VALID_SORT_BY = "Please provide a valid option for sort by"
PROVIDE_VALID_SORT_BY_OPTION_FOR_END_POINT = "The value provided for sort by in %s is not proper for this end point"
PROVIDE_LIMIT_IN_PROPER_RANGE = "Please provide a limit that is between {} and {} "
PROVIDE_PROPER_DATE_FORMAT = "incorrect date string format provided. It should be yyyy-MM-ddTHH:mm:ssZ or yyyy-MM-dd HH:mm:ss"
PROVIDE_VALID_METRIC_NAME = "Invalid metric name"
PROVIDE_VALID_REPORT_NAME = "Invalid report name"
PROVIDE_VALID_START_DATE_EPOCH = 'Invalid start_date must be epoch timestamp'
PROVIDE_START_DATE = 'Please provide start date'
PROVIDE_VALID_END_DATE_EPOCH = 'Invalid end_date must be epoch timestamp'
PROVIDE_END_DATE = 'Please provide end date'
PROVIDE_LIMIT = "Please provide limit"
INVALID_METRIC_NAME_FOR_METRIC_TYPE = "The metric name {metric_name} is not allowed for {metric_type}"
WRONG_CLIENT_ID_PROVIDED = "Provided client id does not belong to user's client list"
NO_RECORD_FOUND = 'No Report In Database'
PROVIDE_CLIENT_ID = 'Please provide client id'
PROVIDE_USER_ID = 'Please provide user id'
PROVIDE_TITLE_VALUE = "Please provide title value"
PROVIDE_FORMAT_VALUE= "Please provide format value"
BAD_TITLE = 'Bad title provided'
BAD_FORMAT = 'Bad format provided'
BAD_DATETIME = "Bad datetime provided"
END_DATE_GT_START_DATE = "End date should be greater than Start date"
IP_TO_BASE64_CONVERSION_FAILED = 'IP to base64 conversion failed. Please check client API IP'
PROVIDE_USER_ID = 'Please provide valid user id'
INVALID_CLIENT_ID = 'Invalid client Id'
BAD_TITLE_CODE = 'Please provide proper title code'
INVALID_DEVID = "Invalid device id in filter"
NO_ADOM_FOUND = "Failed to retrieve adom name"
NO_DEVICE_DATA_FOUND = "Failed to retrieve all device data"
INVALID_DEVICE_ID = "Please provide valid device id"
# ---------------- Validation layer constants ENDS HERE ----------------

# --------------------- Database related constants ---------------------
INSTANT_METRIC_POSITION = 0
TIMESERIES_METRIC_POISTION = 1
# ---------------- Database related constants ENDS HERE ----------------

#-------------------  permission  -----------------#
FAI_GET_METRICS = 'FAI_GET_METRICS'
FAI_GET_ADOM_LIST = 'FAI_GET_ADOM_LIST'
FAI_GET_ADOM_DEVICE_REPORT = 'FAI_GET_ADOM_DEVICE_REPORT'
FAI_GET_ADOM_DEVICE = "FAI_GET_ADOM_DEVICE"
FAI_GET_ADOM_DEVICE_LIST ="FAI_GET_ADOM_DEVICE_LIST"
FAI_GET_SYSTEM_STATUS ="FAI_GET_SYSTEM_STATUS"
#------------------- End permission ---------------#