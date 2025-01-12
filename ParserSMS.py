from datetime import datetime
from .Models import Messages
from smspdudecoder.easy import read_incoming_sms


def status(status):
    match status:
        case "0":
            return "REC UNREAD"
        case "1":
            return "REC READ"
        case "2":
            return "STO UNSENT"
        case "3":
            return "STO SENT"


class Parser:
    def __init__(self):
        pass

    def parse_sms(
        self,
        sms_buffer: str,
        pdu_mode: bool = False,
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
            self.parse_pdu(sms_buffer)

    def parse_pdu(self, pdu):
        pdu_split = pdu.split("+CMGL: ")[1:-1]
        pdu_split = [x.split("\n")[:-1] for x in pdu_split]
        msg_head = pdu_split[0][0].split(",")
        msgs = []
        for pdu in pdu_split:
            msg_head = pdu[0].split(",")
            msg_idx = msg_head[0]
            msg_status = status(msg_head[1])
            msg_len = msg_head[3]
            pdu_encoded = pdu[1]
            pdu_decoded = read_incoming_sms(pdu_encoded)
            msg_contents = pdu_decoded["content"].encode('utf-8').decode('utf-8')
            fulldate = pdu_decoded["date"]
            msg_sender = pdu_decoded["sender"]
            is_partial = bool(type(pdu_decoded["partial"]) == dict)
            partial_key = None
            partial_count = None
            partial_index = None
            if is_partial:
                partial_dict = pdu_decoded["partial"]
                partial_key = partial_dict["reference"]
                partial_count = int(partial_dict["parts_count"])
                partial_index = int(partial_dict["part_number"])
            formatted_date = fulldate.strftime("%Y-%m-%d")
            formatted_time = fulldate.strftime("%H:%M:%S")
            msgs.append(
                {
                    "message_index": msg_idx,
                    "message_type": msg_status,
                    "message_length": msg_len,
                    "message_contents": msg_contents,
                    "message_originating_address": msg_sender,
                    "message_date": formatted_date,
                    "message_time": formatted_time,
                    "partial_key": partial_key,
                    "partial_count": partial_count,
                    "partial_index": partial_index,
                    "is_partial": bool(is_partial),
                    "in_sim_memory": True,
                    "pdu_decoded": pdu_decoded,
                }
            )

        return [Messages(**msg) for msg in msgs]
