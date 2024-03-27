import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile
import boto3
import tele_bot

# AWS credentials
#aws_access_key_id = 'your_access_key'
#aws_secret_access_key = 'your_secret_key'
#aws_session_token = 'your_session_token'  # If using temporary credentials, otherwise set to None

# S3 bucket
bucket_name = 'amirz-bucket'
region = 's3.us-west-1'
aws_server = '.s3.us-west-1.amazonaws.com'

# Create an S3 client
s3 = boto3.client('s3')


class Bot:

    def __init__(self, token, telegram_chat_url):
        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)

        # set the webhook URL
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    @staticmethod
    def is_current_msg_photo(msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        # Downloads the photos that sent to the Bot to `photos` directory (should be existed)

        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )

    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')


class QuoteBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if msg["text"] != 'Please don\'t quote me':
            self.send_text_with_quote(msg['chat']['id'], msg["text"], quoted_msg_id=msg["message_id"])


class ObjectDetectionBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if self.is_current_msg_photo(msg):
            pass
            # TODO download the user photo (utilize download_user_photo) - done
            # TODO upload the photo to S3
            # Local directory containing files to upload
            local_upload_directory = 'uploads'

            # Check if the local directory 'uploads' exists and contains files
            if os.path.exists(local_upload_directory) and os.path.isdir(local_upload_directory):
                files_to_upload = [f for f in os.listdir(local_upload_directory) if
                                   os.path.isfile(os.path.join(local_upload_directory, f))]

                if files_to_upload:
                    # Upload each file to S3
                    for file_name in files_to_upload:
                        local_file_path = os.path.join(local_upload_directory, file_name)
                        s3_key = file_name  # Use the same file name in S3

                        print(f"Uploading {local_file_path} to S3 key: {s3_key}")
                        s3.upload_file(local_file_path, bucket_name, s3_key)

                    print("Upload complete!")
                else:
                    print("No files found in the 'uploads' folder.")
            else:
                print("The 'uploads' folder does not exist or is not a directory.")

            # TODO send a request to the `yolo5` service for prediction - in progress

            # TODO send results to the Telegram end-user - in progress

