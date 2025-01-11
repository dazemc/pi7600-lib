from datetime import datetime


class Parser:
    def parse_sms(
        sms_buffer: str, pdu_mode: bool = False
    ) -> (
        list
    ):  # TODO: check for PDU and parse PDU. PDU is much more informative than text mode.
        """
        Parses the modem sms buffer into a list of dictionaries
        :param sms_buffer: str
        :return: list<dict>
        """
        if not pdu_mode:
            try:
                read_messages = sms_buffer[
                    sms_buffer.find("+CMGL") : sms_buffer.rfind("\r\n\r\nOK\r\n")
                ]
                read_messages = read_messages.split("+CMGL: ")[1:]

                message_list = []
                for msg in read_messages:
                    msg_header = msg[: msg.find("\r\n")].replace('"', "").split(",")
                    msg_contents = msg[msg.find("\r\n") :][2:]
                    msg_contents = (
                        msg_contents[:-2]
                        if msg_contents.endswith("\r\n")
                        else msg_contents
                    )
                    msg_time = msg_header[5][:-3]
                    raw_datetime = f"{msg_header[4]} {msg_time}"
                    parsed_datetime = datetime.strptime(
                        raw_datetime, "%y/%m/%d %H:%M:%S"
                    )
                    formatted_date = parsed_datetime.strftime("%Y-%m-%d")
                    formatted_time = parsed_datetime.strftime("%H:%M:%S")
                    message_list.append(
                        {
                            "message_index": msg_header[0],
                            "message_type": msg_header[1],
                            "message_originating_address": msg_header[2],
                            "message_destination_address": msg_header[3],
                            "message_date": formatted_date,
                            "message_time": formatted_time,
                            "message_contents": msg_contents,
                        }
                    )
                    return message_list
            except Exception as e:
                print(
                    f"ERROR: Parsing SMS: pdu_mode: {pdu_mode}, sms_buffer: {sms_buffer}"
                )

        if pdu_mode:
            print(sms_buffer)
