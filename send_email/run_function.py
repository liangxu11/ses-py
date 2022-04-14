#!/usr/bin/python3
import logging

import boto3

from entity import AppConfigResult
from entity.appconfig_state_enum import AppconfigState
from send_email.json_convert_appconfig import ApConfigJsonConvert
from send_email.send_email_common import SesMailSender


def demo():
    message_dict = {'This sheet 2th row has error': ['Ship Option ID is not null', 'Ship Option Name is not null'],
                    'This sheet 3th row has error': ['Ship Option ID is null', 'Ship Option Name is not null']
                    }
    # message_dict = {}
    appconfig_result = AppConfigResult(0, "12", "123", "12345", AppconfigState.COMPLETE.value, message_dict,
                                       "shipoption/test1.json")

    sender = SesMailSender()
    # appconfig_email = sender.send_appconfig_email(appconfig_result)
    appconfig_email = sender.send_appconfig_templated_email(appconfig_result)
    print(appconfig_email)
    # message_format = MessageFormat(appconfig_result)
    # html_format = message_format.common_message_text_format()
    # print(html_format)


def demo1():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    event_json = [
        {
            "shipOptionID": 1,
            "shipOptionName": "Standard",
            "shipOptionMinTransitTimeasDays": 3,
            "shipOptionMaxTransitTimeasDays": 5
        },
        {
            "shipOptionID": 2,
            "shipOptionName": "Expedite",
            "shipOptionMinTransitTimeasDays": 2,
            "shipOptionMaxTransitTimeasDays": 3
        }
    ]
    appConfig_json_convert = ApConfigJsonConvert(event_json, 'ngskjdp')
    merge = appConfig_json_convert.convert_and_merge()
    print(merge)


if __name__ == '__main__':
    demo()
    # demo1()
