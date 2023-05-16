from datetime import datetime
from smtplib import SMTP


def mail(text: str, bookmaker_name: str = ''):
    """
    Sends some text as an e-mail message to all receivers defined in receivers array.

    :param text: Text we want to send.
    :param bookmaker_name: Bookmaker name if we have.
    """

    try:
        sender = 'hybrid_' + bookmaker_name + '@oddsandmore.com'
        receivers = ['AOluic@oddsandmore.com']
        subject = bookmaker_name + '\'s hybrid error'
        message = 'Subject: {}\n\n{}'.format(subject,
                                             str(text.encode('utf-8')) + '\nDate:\t' + str(datetime.utcnow()))
        smtp_obj = SMTP('localhost')
        smtp_obj.sendmail(sender, receivers, message)
        # print("Successfully sent email")
    except Exception as e:
        print(f'notify error (mail): {text},\nerror: {e}')


def email_suggestions(text: str):
    """
    Sends some text as an e-mail message to all receivers defined in receivers array.
    This is used for mapping only.

    :param text: Text we want to send.
    """

    try:
        sender = 'mapping_suggestions@oddsandmore.com'
        # receivers = ['aoluic@oddsandmore.com', 'traders@oddsandmore.com',
        # 'valerio@oddsandmore.com', 'mgerardi@oddsandmore.com']
        receivers = ['traders@oddsandmore.com', 'mapping@oddsandmore.com']
        subject = 'Map request on Monitor'
        message = 'Subject: {}\n\n{}'.format(subject, str(text.encode('utf-8')))
        smtp_obj = SMTP('localhost')
        smtp_obj.sendmail(sender, receivers, message)
        # print("Successfully sent email")
    except Exception as e:
        print(f'notify error (email_suggestions): {text},\nerror: {e}')
