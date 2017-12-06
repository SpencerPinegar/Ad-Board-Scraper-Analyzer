from twilio.rest import Client

class Phone():
    """
    This class is a wrapper for the twilio object so outgoing messages can be customized and sent
    and so incoming messages can be handled
    """

    account_sid = 'AC4e7c63bc0753b5eabfbdaa7ec099172a' # The twilio accound_sid
    auth_token = 'e33523ef24889a9f4ac9c7fbd29e19bc' # the twilio auth_token
    account_phone_number = '+1385236-0131' # the phone number associated with the account
    client = None # the messaging client



    def __init__(self):
        """
        creates the phone object and initializes messaging client
        """
        self.client = Client(Phone.account_sid, Phone.auth_token)



    def send_message(self, to_number, body):
        """
        
        :param to_number: the numbers the message is sent to in an array
        :param body: the body of the message
        """
        if len(body) > 1550:
            body=body[0:1550]
        for number in to_number:
            self.client.messages.create(
                to=Phone.normalize_number(number),
                from_=Phone.account_phone_number,
                body=body
            )


    @staticmethod
    def normalize_number(number):
        """
        A static method that allows the 
        :param number: the number to be normalized as a string
        :return: a normalized number that the client can interact with
        """
        number = str(number).strip()
        if len(number) == 10:
            number = '+1' + number
        if len(number) == 11:
            number = '+' + number
        if len(number) != 12 or number[0] != '+' or number[1] != '1':
            raise ValueError("You entered an invalid number for the phone object")
        return number