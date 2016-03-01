import httplib
import traceback
import simplejson
import lib.exception.exception as exception
import logconst
from lib.Logger import Logger as LOGGER
from lib.Shared.Config import Config
from tornado import gen
from tornado.httpclient import HTTPError
from tornado.httpclient import HTTPRequest
import tornado.httpclient as httpclient

httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient", max_clients=5000)


class BaseUtil(object):

    key_to_scrub = ['password', 'password_confirmation', 'security_answer', 'secret_1_answer', 'secret_2_answer']

    @classmethod
    @gen.coroutine
    def services_async_curl_request(cls, a_url, a_method='GET', a_headers=None, a_data=None, a_auth_username=None,
                                    a_auth_password=None, a_follow_redirects=False, a_request_id=0, a_api_name=None,
                                    a_operation=None):

        request_data_length = 0

        try:
            http_connect_timeout_sec = Config.get('services.all', 'http_connect_timeout_sec')
            http_request_timeout_sec = Config.get('services.all', 'http_request_timeout_sec')
            api_request_data_logging_enabled = Config.get('toggles', 'enable_api_request_data_logging')

            if not a_headers:
                a_headers = dict()

            # We always want to update the content-length header with the new body size
            if a_data:
                request_data_length = len(a_data)
                a_headers['Content-Length'] = request_data_length

            with LOGGER.abs_exec_time() as abs_exec:
                http_req = HTTPRequest(url=a_url,
                                       method=a_method,
                                       headers=a_headers,
                                       body=a_data,
                                       connect_timeout=int(http_connect_timeout_sec),
                                       request_timeout=int(http_request_timeout_sec),
                                       auth_username=a_auth_username,
                                       auth_password=a_auth_password,
                                       follow_redirects=a_follow_redirects)

                http_client = httpclient.AsyncHTTPClient()
                response = yield gen.Task(http_client.fetch, http_req)

            api_log_extra = BaseUtil._api_logging_extra(a_url, a_method, response, a_api_name, a_operation)

            # Logging request headers and data for developers to debug
            if int(api_request_data_logging_enabled):
                request_headers = a_headers
                request_data = a_data
                if request_data and isinstance(request_data, str):
                    request_data = simplejson.loads(request_data)
                for key in cls.key_to_scrub:
                    request_headers.pop(key, None)
                    if request_data and isinstance(request_data, dict):
                        request_data.pop(key, None)
                api_log_extra['request_header'] = str(request_headers)
                api_log_extra['request_data'] = str(request_data)

            # TODO: Add the response.body None check once the logic for different module is done
            LOGGER.api_detailed_info(a_component_type="API_REQUEST", a_execution_time=abs_exec.time_taken,
                                     a_request_argument_length=request_data_length,
                                     a_response_body_length=len(str(response.body)),
                                     a_request_id=a_request_id, a_api_logging_extra=api_log_extra)

            # We are doing this check because httplib returns an empty body and 599 status
            # message instead of an exception for all the async curl calls which crosses our services timeout limit
            if response.code == 599:
                raise exception.HTTPException(response.code, exception.NETWORK_CONNECT_TIMEOUT_ERROR,
                                              'Proxy connection timed out')

            # Check for all responses under 400 before response.error because redirect and moved responses
            # have a response.error and no body. OAuth server responds with a redirect rather than a 200.
            if response.code > 399 and response.error and not response.body:
                if isinstance(response.error, HTTPError):
                    # We have a communication Error and could not reach beam url
                    if response.error.code > 0 and response.error.message:
                        http_ret_code = response.error.code
                        error_msg = response.error.message
                    else:
                        http_ret_code = httplib.INTERNAL_SERVER_ERROR
                        error_msg = 'Communication Error. Please try again later.'
                    raise exception.HTTPException(http_ret_code, exception.SERVER_ERROR, error_msg)
                raise exception.UnknownHttpException(httplib.GATEWAY_TIMEOUT,
                                                     exception.SERVER_ERROR,
                                                     'Error communicating with Account Platform')

            raise gen.Return(response)
        except gen.Return:
            raise  # Raise the normal return response
        except exception.BaseException as err:
            raise err
        except:
            LOGGER.log_error(traceback.format_exc())
            LOGGER.log_error('Services Curl Error: Error while invoking url="{url}"'.format(url=a_url))
            raise exception.HTTPException(httplib.INTERNAL_SERVER_ERROR,
                                          exception.SERVER_ERROR,
                                          "Internal Server Error. Please try again later")

    @classmethod
    def _api_logging_extra(cls, a_url, a_method, a_response, a_api_name, a_operation):
        api_log_extra = {'api_host': a_url,
                         'http_verb': a_method,
                         'api_response_code': a_response.code,
                         'api_name': a_api_name,
                         'operation': a_operation}

        if a_api_name and a_response.code / 100 == 4:
            if a_api_name == logconst.LOG_VAL_ABS_OAUTH_SERVER:
                error_response = simplejson.loads(a_response.body)
                if 'platform' in error_response:
                    api_log_extra['api_error_message'] = error_response['platform']['message']
                    api_log_extra['api_error_code'] = error_response['platform']['code']
                else:
                    api_log_extra['api_error_message'] = error_response['error']
                    api_log_extra['api_error_description'] = error_response['error_description']

            elif a_api_name == logconst.LOG_VAL_ABS_BEAM:
                error_response = simplejson.loads(a_response.body)
                if 'message' in error_response:
                    api_log_extra['api_error_message'] = error_response['message']
                    api_log_extra['api_error_code'] = error_response['status_code']

        return api_log_extra