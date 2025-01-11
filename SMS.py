from pi7600.Settings import *
import ParserSMS


class SMS:
    """
    Initialize the SMS class.
    """

    def __init__(self):
        self.settings = Settings()
        self.parser = ParserSMS()

    def __getattr__(self, name):
        try:
            return getattr(self.settings, name)
        except AttributeError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

    async def receive_messages(self, message_type: str) -> list:
        """
        Sends SMS command to AT
        :param message_type: str
        :return: list<dict>
        """
        # self.set_data_mode(1)
        answer = await self.send_at(f'AT+CMGL="{message_type}"', "OK", TIMEOUT)
        return (
            self.parser.parse_sms(message_type)
            if message_type == "ALL"
            else self.parser.parse_sms(message_type, True)
        )

    def read_message(self, message_type: str) -> list:
        """
        Reads message from specified message type.
        :param message_type: str
        :return: list<dict>
        """
        try:
            buffer = self.receive_messages(message_type)
            return buffer
        except Exception as e:
            print("Error:", e)
            if self.ser is not None:
                self.ser.close()

    def loop_for_messages(self, message_type: str) -> list:
        """
        Starts a loop that reads message(s) from specified message type.
        :param message_type: str
        :return: str
        """
        while True:
            try:
                buffer = self.receive_messages(message_type)
                return buffer
            except Exception as e:
                print(f"Unhandled error: {e}")
                if self.ser is not None:
                    self.ser.close()

    async def send_message(self, phone_number: str, text_message: str) -> bool:
        answer = await self.send_at('AT+CMGS="' + phone_number + '"', ">", TIMEOUT)
        if answer:
            self.ser.write(text_message.encode())
            self.ser.write(b"\x1a")
            # 'OK' here means the message sent?
            answer = await self.send_at("", "OK", SMS_SEND_TIMEOUT)
            if answer:
                print(
                    f"Number: {phone_number}\n"
                    f"Message: {text_message}\n"
                    f"Message sent!"
                )
                return True
            else:
                print(
                    f"Error sending message...\n"
                    f"phone_number: {phone_number}\n"
                    f"text_message: {text_message}\n"
                    f"Not sent!"
                )
                return False
        else:
            print(f"error: {answer}")
            return False

    async def delete_message(self, msg_idx: int) -> dict:
        """delete message by index

        Args:
            msg_idx (int): message to delete

        Returns:
            dict: {"response": "Success" | False}
        """
        resp = await self.send_at(f"AT+CMGD={msg_idx}", "OK", TIMEOUT)
        if resp:
            return {"response": "Success"}
        else:
            return {"response": False}
