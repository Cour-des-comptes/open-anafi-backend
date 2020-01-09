from rest_framework.response import Response

def custom_exception_handler(exc):
    # Call REST framework's default exception handler first,
    # to get the standard error response.

    # @TODO add Exception Type filter to put corresponding status code 
    response = Response({'detail': str(exc)}, status = 400)
    ## @TODO add logger in order to write log on file system

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code


    return response