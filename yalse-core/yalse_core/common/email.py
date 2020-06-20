import configparser
import logging

import requests


def send_email(message):
    try:
        config = configparser.ConfigParser()
        config.read('secret.ini')

        mailgun_domain = config['email']['mailgun_domain']
        mailgun_key = config['email']['mailgun_key']
        recipient = config['email']['recipient']

        requests.post(f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
                      auth=("api", mailgun_key),
                      data={"from": f"YALSE <mailgun@{mailgun_domain}>",
                            "to": [recipient, ],
                            "subject": "YALSE Sync Report",
                            "text": message})
    except Exception as e:
        logging.error(e)
