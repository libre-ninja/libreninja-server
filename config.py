#region Server
PORT = 4433
"""Port this server is listening on"""
LISTEN_PATH = "/"
"""Path of the WebSocket listener"""
#endregion

#region Administration Options
ALLOW_VERSION_CMD = True
"""Allow the Server to reply to requests asking for the Software version running on this server"""
#endregion

#region Logging
DEBUG_LOG = True
"""If True, DebugLogging is active"""
DEBUG_LOG_FILE = "debug.log"
"""Path to the debug log file"""
ERROR_LOG_FILE = "error.log"
"""Path to error log file"""
LOG_FORMAT = '%(asctime)s %(levelname)s:\t %(funcName)s: %(message)s  \t at %(pathname)s::%(lineno)d;'
"""Format for Log File Entries"""
#endregion