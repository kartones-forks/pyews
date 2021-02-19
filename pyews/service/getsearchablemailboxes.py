import logging
from ..core import Core

__LOGGER__ = logging.getLogger(__name__)


class GetSearchableMailboxes(Core):
    '''Identifies all searchable mailboxes based on the provided UserConfiguration object's permissions

    Example:

    To use any service class you must provide a UserConfiguration object first.

    You can acquire

    ```python
    from pyews import UserConfiguration
    from pyews import GetSearchableMailboxes

    userconfig = UserConfiguration(
        'first.last@company.com',
        'mypassword123'
    )

    searchable_mailboxes = GetSearchableMailboxes(userconfig).run()
    ```

    If you want to use a property from this object with another class then you can iterate through the list of of mailbox properties.
    For example, if used in conjunction with the :doc:`searchmailboxes` you first need to create a list of mailbox reference_ids.

    ```python
    id_list = []
    for id in searchable_mailboxes.run():
        id_list.append(id.get('reference_id'))
    searchResults = SearchMailboxes(userconfig).run('subject:"Phishing Email Subject"', id_list)
    ```

    Args:
        userconfiguration (UserConfiguration): A UserConfiguration object created using the UserConfiguration class
    '''
    def __init__(self, userconfiguration, stop_on_error=False):
        super().__init__(userconfiguration, stop_on_error)

    def __parse_response(self, value):
        '''Creates and sets a response object

        Args:
            value (str): The raw response from a SOAP request
        '''
        if not value:
            raise ValueError("Empty response")

        return_list = []
        if value.find('ResponseCode').string == 'NoError':
            for item in value.find_all('SearchableMailbox'):
                return_list.append({
                    'reference_id': item.ReferenceId.string,
                    'primary_smtp_address': item.PrimarySmtpAddress.string,
                    'display_name': item.DisplayName.string,
                    'is_membership_group': item.IsMembershipGroup.string,
                    'is_external_mailbox': item.IsExternalMailbox.string,
                    'external_email_address': item.ExternalEmailAddress.string,
                    'guid': item.Guid.string
                })
        return return_list

    def run(self):
        soap_message = self.soap()
        __LOGGER__.info("soap message: \n{}".format(soap_message))
        self.raw_xml = self.invoke(soap_message)
        __LOGGER__.info("raw xml response: \n{}".format(self.raw_xml))
        return self.__parse_response(self.raw_xml)

    def soap(self):
        '''Creates the SOAP XML message body

        Returns:
            str: Returns the SOAP XML request body
        '''
        if self.userconfiguration.impersonation:
            impersonation_header = self.userconfiguration.impersonation.header
        else:
            impersonation_header = ''

        return '''<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:t="http://schemas.microsoft.com/exchange/services/2006/types"
               xmlns:m="http://schemas.microsoft.com/exchange/services/2006/messages">
   <soap:Header>
      <t:RequestServerVersion Version="{version}" />
      {header}
   </soap:Header>
   <soap:Body >
      <m:GetSearchableMailboxes>
         <m:ExpandGroupMembership>true</m:ExpandGroupMembership>
      </m:GetSearchableMailboxes>
   </soap:Body>
</soap:Envelope>'''.format(
    version=self.userconfiguration.exchange_version,
    header=impersonation_header)
