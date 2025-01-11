from Globals import *
from Utils import *
from AT import *


class Settings(metaclass=SingletonMeta):
    def __init__(self, com=COM, baudrate=BAUDRATE) -> None:
        """
        Initializes Settings class
        :param port: str
        :param baudrate: int
        """
        self.at = AT(com=com, baudrate=baudrate)
        self.first_run = True

    def __getattr__(self, name):
        try:
            return getattr(self.at, name)
        except AttributeError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

    async def perform_initial_checks(self) -> None:
        """
        Initial environment checks asynchronously.
        """
        checks = {
            "Python version requirements not met": lambda: py_version_check(),
            "SIM device not ready": lambda: self.sim_ready_check(),
        }
        check_failed = False
        for check, result_function in checks.items():
            result = await result_function()  # Await the result from the function
            if result is False:
                check_failed = True
                print(check)
        if check_failed:
            sys.exit(EXIT_FAILURE_CODE)
        else:
            self.first_run = False

    async def enable_verbose_logging(self) -> bool:
        if await self.send_at("AT+CMEE=2", "OK", TIMEOUT):
            return True
        return False

    async def sim_ready_check(self) -> bool:
        if await self.send_at("AT+CPIN?", "READY", TIMEOUT):
            return True
        return False

    async def get_config(self) -> str | bool:
        if await self.send_at("AT&V", "OK", TIMEOUT):
            return True
        return False

    async def set_usb_os(self, os: str) -> bool:
        """
        USB setting for RNDIS, OS specific. "WIN" or "UNIX".
        :param os: str
        :return: bool
        """
        if os == "WIN":
            await self.send_at("AT+CUSBPIDSWITCH=9001,1,1", "OK", TIMEOUT)
        elif os == "UNIX":
            await self.send_at("AT+CUSBPIDSWITCH=9011,1,1", "OK", TIMEOUT)
        for _ in range(6):  # Wait up to 3 mins for reboot
            time.sleep(30)
            try:
                self.init_serial(BAUDRATE, COM)
                if await self.send_at("AT", "OK", TIMEOUT):
                    print(f"Set usb for {os}")
                    return True
            except:
                print("Waiting for device to reboot...")
        print("Failed to set USB mode.")
        return False

    async def set_sms_storage(self, mode: str) -> bool:
        """
        Set SMS storage location
        :param mode: str
        :return: bool
        """
        if await self.send_at(
            f'AT+CPMS="{mode}","{mode}","{mode}"', "OK", TIMEOUT
        ):  # Store messages on SIM(SM), "ME"/"MT" is flash
            return True
        return False

    async def set_data_mode(self, mode: int) -> None:
        """
        HEX is automatically used if there is data issues, such as low signal quality.
        :param mode: int
        :return: None
        """
        if mode == 1:
            await self.send_at("AT+CMGF=1", "OK", TIMEOUT)  # Set to text mode
        if mode == 0:
            await self.send_at("AT+CMGF=0", "OK", TIMEOUT)  # Set to hex mode

    async def set_encoding_mode(self, mode: int) -> None:
        """
        Set encoding mode. 0=IRA, 1=GSM, 2=UCS2
        :param mode: int
        :return: None
        """
        if mode == 2:
            await self.send_at('AT+CSCS="UCS2"', "OK", TIMEOUT)
        if mode == 1:
            await self.send_at('AT+CSCS="GSM"', "OK", TIMEOUT)
        if mode == 0:
            await self.send_at('AT+CSCS="IRA"', "OK", TIMEOUT)
