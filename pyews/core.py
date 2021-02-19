import logging
import requests
import xmltodict
import json
from bs4 import BeautifulSoup

__LOGGER__ = logging.getLogger(__name__)


class Core:

    SOAP_REQUEST_HEADER = {'content-type': 'text/xml; charset=UTF-8'}

    def __init__(self, userconfiguration, stop_on_error=False):
        '''Parent class of all endpoints implemented within pyews

        Args:
            userconfiguration (UserConfiguration): A UserConfiguration object created using the UserConfiguration class
        '''
        self.userconfiguration = userconfiguration
        self.stop_on_error = stop_on_error

    def camel_to_snake(self, s):
        if s != 'UserDN':
            return ''.join(['_'+c.lower() if c.isupper() else c for c in s]).lstrip('_')
        else:
            return 'user_dn'

    @staticmethod
    def _error_message_from(parsed_response):
        for field in [parsed_response.find("MessageText"), parsed_response.find("ErrorMessage")]:
            if field and field.string:
                return field.string

        return ""

    def invoke(self, soap_body):
        '''Used to invoke an Autodiscover SOAP request

        Args:
            soap_body (str): A formatted SOAP XML request body string
            userconfiguration (UserConfiguration): A UserConfiguration object created using the UserConfiguration class

        Raises:
            SoapResponseHasError: Raises an error when unable to parse a SOAP response
        '''
        endpoint = self.userconfiguration.ews_url
        try:
            response = requests.post(
                url=endpoint,
                data=soap_body,
                headers=self.SOAP_REQUEST_HEADER,
                auth=(self.userconfiguration.credentials.email_address, self.userconfiguration.credentials.password),
                verify=True
            )
            parsed_response = BeautifulSoup(response.content, 'xml')

            response_code = parsed_response.find('ResponseCode').string if parsed_response.find('ResponseCode') else None  # NOQA: E501
            error_code = parsed_response.find("ErrorCode").string if parsed_response.find("ErrorCode") else None

            if response_code == 'NoError' and not error_code:
                return parsed_response

            __LOGGER__.info("Error '{code}': {message}".format(
                code=error_code,
                message=self._error_message_from(parsed_response)
            ))
        except requests.exceptions.HTTPError as errh:
            __LOGGER__.info("An Http Error occurred attempting to connect to {ep}:".format(ep=endpoint) + repr(errh))
        except requests.exceptions.ConnectionError as errc:
            __LOGGER__.info("An Error Connecting to the API occurred attempting to connect to {ep}:".format(ep=endpoint) + repr(errc))
        except requests.exceptions.Timeout as errt:
            __LOGGER__.info("A Timeout Error occurred attempting to connect to {ep}:".format(ep=endpoint) + repr(errt))
        except requests.exceptions.RequestException as err:
            __LOGGER__.info("An Unknown Error occurred attempting to connect to {ep}:".format(ep=endpoint) + repr(err))

        __LOGGER__.warning('Unable to parse response from {current}'.format(current=self.__class__.__name__))

        if self.stop_on_error:
            exit(1)
        else:
            return None
