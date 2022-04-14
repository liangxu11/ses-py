import os
import unittest

import boto3

from send_email.send_email_common import EmailBody, SesMailSender

os.environ['EMAIL_SOURCE'] = "xu.liang@cienet.com.cn"
os.environ['EMAIL_DESTINATION'] = "xu@229"
from botocore.exceptions import ClientError
from moto import mock_ses

from entity import AppConfigResult
from entity.appconfig_state_enum import AppconfigState


class TestSendMail(unittest.TestCase):

    @mock_ses
    def test_send_email(self):
        conn = boto3.client("ses", region_name="us-east-2")
        emailBody = EmailBody(source="xu.liang@cienet.com.cn",
                              destination="liangxudoit@163.com",
                              subject="Example of an email template.",
                              text="Hello from the Amazon SES mail demo!",
                              html="<p>Hello!</p><p>From the <b>Amazon SES</b> mail demo!</p>",
                              cc="1209514536@qq.com",
                              bcc="1209514536@qq.com",
                              reply_tos="1209514536@qq.com"
                              )

        sesMailSender = SesMailSender(conn)

        self.assertRaises(ClientError, sesMailSender.send_email, emailBody)

        conn.verify_email_address(EmailAddress="xu.liang@cienet.com.cn")

        sesMailSender.send_email(emailBody)

        send_quota = conn.get_send_quota()
        sent_count = int(send_quota["SentLast24Hours"])
        self.assertEqual(sent_count, 3)

    @mock_ses
    def test_send_template_email(self):
        conn = boto3.client("ses", region_name="us-east-2")

        conn.create_template(
            Template={
                "TemplateName": "MyTemplate",
                "SubjectPart": "lalala",
                "HtmlPart": "1111",
                "TextPart": "1111",
            }
        )

        emailBody = EmailBody(source="xu.liang@cienet.com.cn",
                              destination="liangxudoit@163.com",
                              template_name="MyTemplate",
                              template_data={"name": "Alejandro", "favoriteanimal": "alligator"},
                              cc="1209514536@qq.com",
                              bcc="1209514536@qq.com",
                              reply_tos="1209514536@qq.com"
                              )

        sesMailSender = SesMailSender(conn)
        self.assertRaises(ClientError, sesMailSender.send_templated_email, emailBody)

        conn.verify_email_address(EmailAddress="xu.liang@cienet.com.cn")
        sesMailSender.send_templated_email(emailBody)

        send_quota = conn.get_send_quota()
        sent_count = int(send_quota["SentLast24Hours"])
        self.assertEqual(sent_count, 3)

    @mock_ses
    def test_send_appconfig_email_complete(self):
        conn = boto3.client("ses")

        appconfig_result = AppConfigResult(0, "12", "123", "12345", AppconfigState.COMPLETE.value, "",
                                           "shipoption/test1.json")

        sesMailSender = SesMailSender(conn)
        email = sesMailSender.send_appconfig_email(appconfig_result)
        self.assertEqual(email, None)

        conn.verify_email_address(EmailAddress="xu.liang@cienet.com.cn")

        sesMailSender.send_appconfig_email(appconfig_result)

        send_quota = conn.get_send_quota()
        sent_count = int(send_quota["SentLast24Hours"])
        self.assertEqual(sent_count, 1)

    @mock_ses
    def test_send_appconfig_email_error(self):
        conn = boto3.client("ses")

        message_dict = {'This sheet 2th row has error': ['Ship Option ID is not null', 'Ship Option Name is not null'],
                        'This sheet 3th row has error': ['Ship Option ID is null', 'Ship Option Name is not null']
                        }
        appconfig_result = AppConfigResult(0, "12", "123", "12345", AppconfigState.VERIFY_ERROR.value, message_dict,
                                           "shipoption/test1.json")
        sesMailSender = SesMailSender(conn)

        conn.verify_email_address(EmailAddress="xu.liang@cienet.com.cn")

        sesMailSender.send_appconfig_email(appconfig_result)

        send_quota = conn.get_send_quota()
        sent_count = int(send_quota["SentLast24Hours"])
        self.assertEqual(sent_count, 1)

    @mock_ses
    def test_send_appconfig_template_email_error(self):
        conn = boto3.client("ses")

        message_dict = {'This sheet 2th row has error': ['Ship Option ID is not null', 'Ship Option Name is not null'],
                        'This sheet 3th row has error': ['Ship Option ID is null', 'Ship Option Name is not null']
                        }
        appconfig_result = AppConfigResult(0, "12", "123", "12345", AppconfigState.VERIFY_ERROR.value, message_dict,
                                           "shipoption/test1.json")
        sesMailSender = SesMailSender(conn)
        email = sesMailSender.send_appconfig_templated_email(appconfig_result)
        self.assertEqual(email, None)

        conn.verify_email_address(EmailAddress="xu.liang@cienet.com.cn")
        conn.create_template(
            Template={
                "TemplateName": "SendEmailAppConfigError",
                "SubjectPart": "lalala",
                "HtmlPart": "1111",
                "TextPart": "1111",
            }
        )

        sesMailSender.send_appconfig_templated_email(appconfig_result)

        send_quota = conn.get_send_quota()
        sent_count = int(send_quota["SentLast24Hours"])
        self.assertEqual(sent_count, 1)

    @mock_ses
    def test_send_appconfig_template_email_common(self):
        conn = boto3.client("ses")

        message_dict = {}
        appconfig_result = AppConfigResult(0, "12", "123", "12345", AppconfigState.COMPLETE.value, message_dict,
                                           "shipoption/test1.json")
        sesMailSender = SesMailSender(conn)

        conn.verify_email_address(EmailAddress="xu.liang@cienet.com.cn")
        conn.create_template(
            Template={
                "TemplateName": "SendEmailAppConfigCommon",
                "SubjectPart": "lalala",
                "HtmlPart": "1111",
                "TextPart": "1111",
            }
        )

        sesMailSender.send_appconfig_templated_email(appconfig_result)

        send_quota = conn.get_send_quota()
        sent_count = int(send_quota["SentLast24Hours"])
        self.assertEqual(sent_count, 1)

if __name__ == '__main__':
    unittest.main()
