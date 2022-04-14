import json
import unittest
from io import StringIO
from unittest.mock import patch, call

import botocore
from coverage.annotate import os
from moto.cloudwatch.exceptions import ResourceNotFoundException

from send_email.json_convert_appconfig import ApConfigJsonConvert

os.environ['APP_CONFIG_APPLICATION_ID'] = "swwi0e4"
os.environ['APP_CONFIG_ENVIRONMENT_ID'] = "qn1133e"


@patch('botocore.client.BaseClient._make_api_call')
class TestJsonConvert(unittest.TestCase):

    def test_json_convert(self, boto_mock):

        response_start = {'InitialConfigurationToken': "QQQQwww"}

        response_config_str = '''
                [
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
                '''
        response_body = botocore.response.StreamingBody(StringIO(response_config_str),
                                                        len(str(response_config_str)))
        response_config = {"Configuration": response_body}
        boto_mock.side_effect = [ResourceNotFoundException, response_config]

        event_list = [
            {
                "shipOptionID": 11,
                "shipOptionName": "Standard",
                "shipOptionMinTransitTimeasDays": 3,
                "shipOptionMaxTransitTimeasDays": 5
            },
            {
                "shipOptionID": 2,
                "shipOptionName": "Expedite",
                "shipOptionMinTransitTimeasDays": 2,
                "shipOptionMaxTransitTimeasDays": 31
            }
        ]
        appConfig_json_convert_exception = ApConfigJsonConvert(event_list, "profile_id")
        result = appConfig_json_convert_exception.convert_and_merge()
        self.assertEqual(len(result), 2)
        assert boto_mock.call_count == 1

        boto_mock.side_effect = [response_start, response_config]
        appConfig_json_convert_change = ApConfigJsonConvert(event_list, "profile_id")
        result = appConfig_json_convert_change.convert_and_merge()
        self.assertEqual(len(result), 3)
        assert boto_mock.call_count == 3

    def test_json_convert_lambda_no_change(self, boto_mock):

        response_start = {'InitialConfigurationToken': "QQQQwww"}

        response_config_str = '''
                [
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
                '''
        response_body = botocore.response.StreamingBody(StringIO(response_config_str),
                                                        len(str(response_config_str)))
        response_config = {"Configuration": response_body}
        boto_mock.side_effect = [response_start, response_config]

        event_list = [
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

        appConfig_json_convert = ApConfigJsonConvert(event_list, "profile_id")
        result = appConfig_json_convert.convert_and_merge()
        self.assertEqual(len(result), 2)
        assert boto_mock.call_count == 2


if __name__ == '__main__':
    unittest.main()