import asyncio
from enum import Enum
from typing import List
from datetime import timedelta
from dataclasses import dataclass
# import warnings
# warnings.filterwarnings("ignore", category=RuntimeWarning)
timeout_seconds = timedelta(seconds=15).total_seconds()

@dataclass
class Payload:
    data: str

@dataclass
class Address:
    email: str | None


@dataclass
class Event:
    recipients: List[Address]
    payload: Payload

class Result(Enum):
    Accepted = 1
    Rejected = 2

async def read_data() -> Event:
    # Метод для чтения порции данных
    # Пример реализации: возвращает фиктивные данные
    return Event(
        recipients=[Address(email='sss@domain.su'), Address(email='aaa@domain.su')],
        payload=Payload(data='some data')
    )

async def send_data(address: Address, payload: Payload) -> Result:
    # Метод для рассылки данных
    # Пример реализации: просто принимаем все данные
    await asyncio.sleep(1)
    print(f"Sending data to {address}")
    return Result.Rejected

async def perform_operation() -> None:
    while True:
        try:
            event = await read_data()

            send_tasks = [
                         send_data(recipient, event.payload)
                         for recipient in event.recipients
            ]

            results = await asyncio.gather(*send_tasks)

            for result in results:
                 if result == Result.Rejected:
                    print("Data rejected. Retrying...")
                    await asyncio.sleep(1)
        except asyncio.TimeoutError:
            print("Timeout reading data. Retrying...")


# Initiate asyncio loop
asyncio.run(perform_operation())
