import json
import logging
import os
import traceback

import boto3
from botocore.exceptions import ClientError

from entity import AppConfigResult
from entity.appconfig_state_enum import AppconfigState

logger = logging.getLogger(__name__)


class EmailBody:
    """
    Contains data about an email.

    :param source: The source email account.
    :param destination: The destination email account.
    :param subject: The subject of the email.
    :param text: The plain text version of the body of the email.
    :param html: The HTML version of the body of the email.
    :param template_name: The name of a previously created template.
    :param template_data: JSON-formatted key-value pairs of replacement values
                              that are inserted in the template before it is sent.
    :param cc: The list of recipients on the 'CC:' line.
    :param bcc: The list of recipients on the 'BCC:' line.
    :param reply_tos: Email accounts that will receive a reply if the recipient
                      replies to the message.

    """

    def __init__(self, source, destination, subject=None, text=None, html=None, template_name=None, template_data=None,
                 cc=None, bcc=None, reply_tos=None):
        self.source = source
        self.destination = destination
        self.subject = subject
        self.text = text
        self.html = html
        self.template_name = template_name
        self.template_data = template_data
        self.cc = cc
        self.bcc = bcc
        self.reply_tos = reply_tos

    def to_service_format(self):
        """
        :return: The destination data in the format expected by Amazon SES.
        """
        svc_format = {'ToAddresses': self.destination.split(",")}
        if self.cc is not None:
            svc_format['CcAddresses'] = self.cc.split(",")
        if self.bcc is not None:
            svc_format['BccAddresses'] = self.bcc.split(",")
        return svc_format


class SesMailSender:
    """Encapsulates functions to send emails with Amazon SES."""

    def __init__(self, ses_client=boto3.client("ses")):
        """
        :param ses_client: A Boto3 Amazon SES client.
        """
        self.ses_client = ses_client

    def send_email(self, email_body):
        """
        Sends an email.

        Note: If your account is in the Amazon SES  sandbox, the source and
        destination email accounts must both be verified.

        :param email_body:
        :return: The ID of the message, assigned by Amazon SES.
        """
        send_args = {
            'Source': email_body.source,
            'Destination': email_body.to_service_format(),
            'Message': {
                'Subject': {'Data': email_body.subject},
                'Body': {'Text': {'Data': email_body.text}, 'Html': {'Data': email_body.html}}}}
        if email_body.reply_tos is not None:
            send_args['ReplyToAddresses'] = email_body.reply_tos.split(',')
        try:
            response = self.ses_client.send_email(**send_args)
            message_id = response['MessageId']
            logger.info(
                "Sent mail %s from %s to %s.", message_id, email_body.source, email_body.destination)
        except ClientError:
            logger.exception(
                "Couldn't send mail from %s to %s.", email_body.source, email_body.destination)
            raise
        else:
            return message_id

    def send_templated_email(self, email_body):
        """
        Sends an email based on a template. A template contains replaceable tags
        each enclosed in two curly braces, such as {{name}}. The template data passed
        in this function contains key-value pairs that define the values to insert
        in place of the template tags.

        Note: If your account is in the Amazon SES  sandbox, the source and
        destination email accounts must both be verified.

        :param email_body:
        :return: The ID of the message, assigned by Amazon SES.
        """
        send_args = {
            'Source': email_body.source,
            'Destination': email_body.to_service_format(),
            'Template': email_body.template_name,
            'TemplateData': json.dumps(email_body.template_data)
        }
        if email_body.reply_tos is not None:
            send_args['ReplyToAddresses'] = email_body.reply_tos.split(',')
        try:
            response = self.ses_client.send_templated_email(**send_args)
            message_id = response['MessageId']
            logger.info(
                "Sent templated mail %s from %s to %s.", message_id, email_body.source,
                email_body.destination)
        except ClientError:
            logger.exception(
                "Couldn't send templated mail from %s to %s.", email_body.source, email_body.destination)
            raise
        else:
            return message_id

    def send_appconfig_email(self, message):
        """
        Sends an email according to the response information of AppConfig Deploy.

        Note: If your account is in the Amazon SES  sandbox, the source and
        destination email accounts must both be verified.

        :param message:
        :return: The ID of the message, assigned by Amazon SES.
        """
        email_body = EmailBody(source=os.getenv("EMAIL_SOURCE"),
                               destination=os.getenv("EMAIL_DESTINATION"))
        try:
            if message.state == AppconfigState.VERIFY_ERROR.value:
                email_body.subject = "Appconfig deploy error notification."
                email_body.text = MessageFormat(message).error_message_text_format()
                email_body.html = MessageFormat(message).error_message_html_format()
            else:
                email_body.subject = "Appconfig deploy " + message.state + " notification."
                email_body.text = MessageFormat(message).common_message_text_format()
                email_body.html = MessageFormat(message).common_message_html_format()
            return self.send_email(email_body)
        except Exception as exception:
            logger.error("send appconfig email fail.")
            traceback.print_exc()
        return None

    def send_appconfig_templated_email(self, message):
        """
        Sends an email based on a template. A template contains replaceable tags
        each enclosed in two curly braces, such as {{name}}. The template data passed
        in this function contains key-value pairs that define the values to insert
        in place of the template tags.

        Note: If your account is in the Amazon SES  sandbox, the source and
        destination email accounts must both be verified.

        :param message:
        :return: The ID of the message, assigned by Amazon SES.
        """
        email_body = EmailBody(source=os.getenv("EMAIL_SOURCE"),
                               destination=os.getenv("EMAIL_DESTINATION"))
        try:
            if message.state == AppconfigState.VERIFY_ERROR.value:
                email_body.template_name = "SendEmailAppConfigError"
                error_message = message.error_message
                error_message_list = []
                for key, value in error_message.items():
                    error_message_each_dict = {"row": key, "msg": ','.join(value)}
                    error_message_list.append(error_message_each_dict)
                template_data = {"error_message": error_message_list}
                email_body.template_data = template_data
            else:
                email_body.template_name = "SendEmailAppConfigCommon"
                common_dict = {"state": message.state, "msg": json.dumps(message, default=AppConfigResult.convert2json)}
                email_body.template_data = common_dict
            return self.send_templated_email(email_body)
        except Exception as exception:
            logger.error("send appconfig template email fail.")
            traceback.print_exc()
        return None


class MessageFormat:
    """Message format output text and html."""

    def __init__(self, appconfig_result):
        """
        param appconfig_result: the response information of AppConfig Deploy.
        """
        self.appconfig_result = appconfig_result

    def error_message_html_format(self):
        appconfig_result = self.appconfig_result
        error_dict = appconfig_result.error_message
        html = "<p>Hello!</p><p>Verification of uploaded excel file failed,details are as follows!</p><p>key:" \
               + appconfig_result.key + "</p>"
        table = "<table border='1'>"
        for key, value in error_dict.items():
            table += "<tr><td>" + key + "</td>"
            table += "<td>" + ','.join(value) + "</td></tr>"

        table += "</table>"
        html += table
        return html

    def error_message_text_format(self):
        appconfig_result = self.appconfig_result
        error_dict = appconfig_result.error_message
        text = "Hello,\r\n" + "Verification of uploaded excel file failed,details are as follows!\r\nkey:" \
               + appconfig_result.key + "\r\n"
        for key, value in error_dict.items():
            text += key + "    " + ','.join(value) + "\r\n"
        return text

    def common_message_html_format(self):
        html = "<p>Hello!</p><p>Deploy details are as follows!</p><p>" + json.dumps(
            self.appconfig_result, default=AppConfigResult.convert2json) + "</p>"
        return html

    def common_message_text_format(self):
        text = "Hello,\r\n" + "Deploy details are as follows!\r\n" + json.dumps(
            self.appconfig_result, default=AppConfigResult.convert2json)
        return text
