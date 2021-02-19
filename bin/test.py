from pyews import GetSearchableMailboxes, SearchMailboxes, UserConfiguration


# don't include ever this file in git!
# Create a test_config.py file containing `USERNAME` and `PASSWORD`
try:
    from bin.test_config import USERNAME, PASSWORD  # NOQA: F401, F403
except Exception:  # nosec
    print("missing test_config.py file")
    exit(1)

STOP_ON_ERROR = True

# Example of using Autodiscover
userconfig = UserConfiguration(
   USERNAME,
   PASSWORD,
   stop_on_error=True
)

# you can print properties on the useconfig object if needed
"""
print("------")
print("userconfig.autodiscover: ", userconfig.autodiscover)
print("userconfig.get():")
config = userconfig.get()
print({key: config[key] for key in config.keys() if key != "password"})
print("userconfig.credentials.email_address: ", userconfig.credentials.email_address)
print("userconfig.ews_url: ", userconfig.ews_url)
print("userconfig.exchangeVersion: ", userconfig.exchange_version)
"""

# Example of NOT using Autodiscover
'''
userconfig = UserConfiguration(
   'first.last@dev.onmicrosoft.com',
   'password',
   autodiscover=False,
   ewsUrl='https://autodiscover-s.outlook.com/EWS/Exchange.asmx'
)
'''

# get searchable mailboxes based on your accounts permissions
referenceid_list = []
for mailbox in GetSearchableMailboxes(userconfig, stop_on_error=STOP_ON_ERROR).run():
    referenceid_list.append(mailbox['ReferenceId'])

print("referenceid_list: ", referenceid_list)

"""

messages_found = []
for search in SearchMailboxes(userconfig, stop_on_error=STOP_ON_ERROR).run('subject:"Digest"', referenceid_list):
    messages_found.append(search['MessageId'])
    # we can print the results first if we want
    print(search['Subject'])
    print(search['MessageId'])
    print(search['Sender'])
    print(search['ToRecipients'])
    print(search['CreatedTime'])
    print(search['ReceivedTime'])
    # etc.

print("messages_found:")
print(messages_found)

"""

# if we wanted to now delete a specific message then we would call the DeleteItem class

# from pyews import DeleteItem
# deleted_message_response = DeleteItem(messages_found[0], userconfig).response

# print(deleted_message_response)

# once you have the mailboxes "referenceIds" (example in SearchMailboxes below) you need to loop through them and
# provide either a single referenceid or a list of them

# from pyews import SearchMailboxes
# mailboxSearch = SearchMailboxes('subject:account', userconfig, '/o=ExchangeLabs/ou=Exchange Administrative Group (FYDIBOHF23SPDLT)/cn=Recipients/cn=2ae3541cef834557aadf2fa434590af2-mailbox1').response
# print(mailboxSearch)

# We can get InboxRules as well

# from pyews import GetInboxRules
# mailboxRules = GetInboxRules('first.last@dev.onmicrosoft.com', userconfig).response
