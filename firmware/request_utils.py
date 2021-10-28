def code_string(code):
    global codes
    if code in codes:
        return codes[code]
    else:
        print("Warning: Response code {} doesn't exist or is not supported".format(code))
        return "Unsupported"


codes = {
    # Informational
    100: "Continue",

    101: "Switching Protocols",
    # Successfull
    200: "OK",
    201: "Created",
    202: "Accepted",

    #  203: "Non-Authoritative Information",
    #  204: "No content",
    #  205: "Reset Content",
    #  206: "Partial Content",
    # Redirections,
    #  300: "Multiple Choices",
    #  301: "Moved Permanently",
    #  302: "Found",
    #  303: "See Other",
    #  304: "Not Modified",
    #  305: "Use Proxy",
    #  307: "Temporary Redirect",
    #  # Client Error ',
    400: "Bad Request",
    #  401: "Unauthorized",
    #  402: "Payment Required",
    #  403: "Forbidden",
    404: "Not Found",
    #  405: "Method Not Allowed",
    #  406: "Not Acceptable",
    #  407: "Proxy Authentication Required",
    #  408: "Request Timeout",
    #  409: "Conflict",
    #  410: "Gone",
    #  411: "Length Required",
    #  412: "Precondition Failed",
    #  413: "Request Entity Too Large",
    #  414: "Request-URI Too Long",
    #  415: "Unsupported Media Type",
    #  416: "Requested Range Not Satisfiable",
    #  417: "Expectation Failed",
    # Server Error
    #  500: "Internal Server Error",
    #  501: "Not Implemented",
    #  502: "Bad Gateway",
    #  503: "Service Unavailable",
    #  504: "Gateway Timeout",
    #  505: "HTTP Version Not Supported"
}