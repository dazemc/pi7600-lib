from pi7600.Settings import *


class Phone:
    """
    Initialize the Phone class.
    """

    def __init__(self):
        self.settings = Settings()

    def __getattr__(self, name):
        try:
            return getattr(self.settings, name)
        except AttributeError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

    async def hangup_call(self) -> bool:
        if await self.send_at("AT+CHUP", "OK", PHONE_TIMEOUT):
            return True
        return False

    def call_incoming(self):
        # call_incoming(): Check for incoming calls
        # I will come back to this after I determine concurrency/interrupts/chaining AT commands
        pass

    async def active_calls(self) -> str | bool:
        """
        Returns information on any active calls
        :return: str || bool
        """
        if await self.send_at("AT+CLCC?", "OK", PHONE_TIMEOUT):
            return True
        return False

    async def call(self, contact_number: str, retry: int = 0) -> bool:
        """
        Start outgoing call.
        :param contact_number: str
        :param retry: int
        :return: bool
        """
        # A True return does not mean call was connected, simply means the attempt was valid without errors.
        attempt = 1
        try:
            while True:
                print(
                    f"Attempting to call {contact_number}; Attempt: {attempt}; Retry: {retry}"
                )
                # IF ATD returns an error then determine source of error.
                if await self.send_at(
                    "ATD" + contact_number + ";", "OK", PHONE_TIMEOUT
                ):
                    input("Call connected!\nPress enter to end call")
                    # self.ser.write('AT+CHUP\r\n'.encode())  # Hangup code, why is serial used vs send_at()?
                    self.hangup_call()
                    print("Call disconnected")
                    return True
                elif retry == 0 or attempt == retry:
                    return True
                elif retry != 0:
                    print(
                        f"Retrying call to {contact_number}; Attempt: {attempt}/{retry}"
                    )
                    attempt += 1
        except:
            return False

    def closed_call(self) -> str:
        # This will display information about calls that have been made/attempted
        # Call time, connection status, error outputs, etc
        pass
