import asyncio
import serial
import time
from Globals import POLL


class AT:
    def __init__(self, com: str, baudrate: int) -> None:
        self.com = com
        self.baudrate = baudrate
        self.ser = self.init_serial(baudrate, com)
        self.rec_buff = ""
        self.write_queue = asyncio.Queue()  # Queue for managing outgoing commands
        self.task = None  # Task for processing the write queue

    def init_serial(self, baud, com):
        ser = serial.Serial(com, baud, rtscts=True, timeout=0.5)
        return ser

    async def send_at(self, command: str, back: str, timeout: int) -> str:
        """
        Send an AT command and wait for the expected response.
        :param command: str - AT command to be sent
        :param back: str - Expected response to check
        :param timeout: int - Timeout to wait for a response
        :return: str - The response from the device, or an error message.
        """
        if self.task is None or self.task.done():
            self.task = asyncio.create_task(self.process_write_queue())
        self.clear_buffer()
        self.ser.write((command + "\r\n").encode())
        start_time = time.time()
        while True:
            if self.ser.in_waiting > 0:
                self.rec_buff += self.ser.read(self.ser.in_waiting).decode(
                    errors="ignore"
                )
            if back in self.rec_buff:
                response = self.rec_buff
                self.clear_buffer()
                return response
            if time.time() - start_time > timeout:
                self.clear_buffer()
                return f"ERROR: Timeout while waiting for response to '{command}'"

            # Yield control to other tasks and wait a bit before checking again
            await asyncio.sleep(0.1)

    async def process_write_queue(self):
        """
        Asynchronously process the write queue and send commands.
        """
        while True:
            command, back, timeout, repeat = await self.write_queue.get()
            response = await self.send_at(command, back, timeout)
            if "ERROR" in response:
                print(f"Failed to execute: {command}, Error: {response}")
            else:
                print(f"Successfully executed: {command}, Response: {response}")

            # Re-enqueue if repeat is True
            if repeat:
                await asyncio.sleep(POLL)
                await self.write_queue.put((command, back, timeout, repeat))

            # Mark task as done if not repeating
            if not repeat:
                self.write_queue.task_done()

    def close_serial(self) -> None:
        try:
            self.ser.close()
        except:
            print("Failed to close serial: Already closed or inaccessible")

    def clear_buffer(self) -> None:
        if self.ser.in_waiting:
            self.ser.flush()
        self.rec_buff = ""
