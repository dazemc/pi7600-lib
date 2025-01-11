import asyncio
from pi7600.Settings import *


class GPS:
    """
    Initialize the GPS class.
    """

    def __init__(self):
        self.settings = Settings()
        self.loc = ""
        self.is_running = False  # Initialized to False; actual status will be checked asynchronously later

    def __getattr__(self, name):
        try:
            return getattr(self.settings, name)
        except AttributeError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

    async def session_check(self):
        check = await self.send_at("AT+CGPS?", "+CGPS", TIMEOUT)
        self.is_running = True if "+CGPS: 1,1" in check else False
        return self.is_running

    async def gps_session(self, start: bool) -> bool:
        """
        True to start session. False to close session.
        :param start: bool
        :return: bool
        """
        await self.session_check()
        if start:
            print("Starting GPS session...")
            if await self.send_at(
                "AT+CGPS=0,1", "OK", GPS_TIMEOUT
            ) and await self.send_at("AT+CGPS=1,1", "OK", GPS_TIMEOUT):
                print("Started successfully")
                await asyncio.sleep(2)
                self.is_running = True
                return True
        else:
            print("Closing GPS session...")
            self.rec_buff = ""
            if await self.send_at("AT+CGPS=0,1", "OK", GPS_TIMEOUT):
                self.is_running = False
                return True
            else:
                print("Error closing GPS, is it open?")
                return False

    async def get_gps_position(self, retries: int = GPS_RETRY) -> str | bool:
        await self.session_check()  # Ensure session status is checked asynchronously
        if self.is_running:
            for _ in range(retries):
                answer = await self.send_at("AT+CGPSINFO", "+CGPSINFO: ", GPS_TIMEOUT)
                if answer and ",,,,,," not in answer:
                    return answer
                elif ",,,,,," in answer:
                    return "GPS is active but no signal was found"
                else:
                    print("Error accessing GPS, attempting to close session")
                    if not await self.gps_session(False):  # Await the async method
                        print("GPS was not found or did not close correctly")
                    else:
                        print("Done")
                    return False
            print("Retry limit reached; GPS signal not found...")
            return False
        else:
            print(
                "Attempting to get location without an open GPS session, trying to open one now..."
            )
            await self.gps_session(True)  # Await the async method
            return await self.get_gps_position()  # Await the async recursive call
