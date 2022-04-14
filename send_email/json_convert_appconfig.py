#!/usr/bin/python3
import json
import logging
import os
import traceback

import boto3
import botocore
import json_tools

logger = logging.getLogger(__name__)


class ApConfigJsonConvert:
    """Merge the newly uploaded incremental data into the deployed version of AppConfig"""

    def __init__(self, list_obj, profile_id):
        """
        :param list_obj:the newly uploaded incremental data
        :param profile_id:AppConfig profile id
        """
        self.list_obj = list_obj
        self.profile_id = profile_id

    def convert_and_merge(self):
        """
         JSON data comparison and return the merged data
        :return: list:the merged data
        """
        cache_dict = {}
        config_json = self.get_config()

        if config_json:
            for each_data in config_json:
                cache_dict[each_data["shipOptionID"]] = each_data

        change_num = 0
        for item in self.list_obj:
            ship_id = item["shipOptionID"]
            if ship_id in cache_dict:
                diff_ret = json_tools.diff(item, cache_dict[ship_id])
                if diff_ret:
                    cache_dict[ship_id] = item
                    change_num += 1

            else:
                cache_dict[ship_id] = item
                change_num += 1

        if change_num == 0:
            logging.info("no change--->")
            return config_json
        else:
            list_ret = []
            for value in cache_dict.values():
                list_ret.append(value)
            return list_ret

    def get_config(self):
        """
        Get the latest deployed data form AppConfig
        :return: the latest deployed json data
        """
        application_id = os.getenv("APP_CONFIG_APPLICATION_ID")
        environment_id = os.getenv("APP_CONFIG_ENVIRONMENT_ID")

        client = boto3.client('appconfigdata')

        response = []
        try:
            application_id = os.getenv("APP_CONFIG_APPLICATION_ID")
            response = client.start_configuration_session(
                ApplicationIdentifier=application_id,
                EnvironmentIdentifier=environment_id,
                ConfigurationProfileIdentifier=self.profile_id,
                RequiredMinimumPollIntervalInSeconds=15
            )
        except Exception as exception:
            if type(exception).__name__ == "ResourceNotFoundException":
                logging.info("the first deploy!")
                return []
            else:
                raise

        token = response['InitialConfigurationToken']

        response = client.get_latest_configuration(
            ConfigurationToken=token
        )
        config_json = json.loads(response['Configuration'].read())

        return config_json
