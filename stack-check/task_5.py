import asyncio

from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from typing import Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
    

timeout_seconds = timedelta(seconds=15).total_seconds()

class Response(Enum):
    Success = 1
    RetryAfter = 2
    Failure = 3

class ApplicationStatusResponse(Enum):
    Success = 1
    Failure = 2

@dataclass
class ApplicationResponse:
    application_id: str
    status: ApplicationStatusResponse
    description: str
    last_request_time: datetime
    retriesCount: Optional[int]

async def get_application_status1(identifier: str) -> Response:
    # Пример реализации для сервиса 1
    await asyncio.sleep(2)  # Эмуляция задержки запроса
    return Response.Success

async def get_application_status2(identifier: str) -> Response:
    # Пример реализации для сервиса 2
    await asyncio.sleep(3)  # Эмуляция задержки запроса
    return Response.Failure

async def perform_operation(identifier: str, total_elapsed_time: float = 0, total_retry_count: int = 0) -> ApplicationResponse:
    start_time = datetime.now()

    with ThreadPoolExecutor() as executor:
        task1 = await asyncio.get_event_loop().run_in_executor(
            executor,
            get_application_status1,
            identifier
        )
        task2 = await asyncio.get_event_loop().run_in_executor(
            executor,
            get_application_status2,
            identifier
        )

        responses = await asyncio.gather(task1, task2)

    end_time = datetime.now()
    elapsed_time = (end_time - start_time).total_seconds()
    total_elapsed_time += elapsed_time

    success_count = sum(1 for response in responses if response == Response.Success)
    failure_count = sum(1 for response in responses if response == Response.Failure)
    retry_count = sum(1 for response in responses if response == Response.RetryAfter)
    
    total_retry_count += retry_count

    if total_elapsed_time > timeout_seconds:
        return ApplicationResponse(
            application_id=identifier,
            status=ApplicationStatusResponse.Failure,
            description="Timeout exceeded",
            last_request_time=end_time,
            retriesCount=None
        )

    if success_count == 2:
        return ApplicationResponse(
            application_id=identifier,
            status=ApplicationStatusResponse.Success,
            description="Both services returned success",
            last_request_time=end_time,
            retriesCount=retry_count
        )
    if success_count == 1 and failure_count == 1:
        return ApplicationResponse(
            application_id=identifier,
            status=ApplicationStatusResponse.Failure,
            description="One service returned success, another is failure",
            last_request_time=end_time,
            retriesCount=None
        )
    elif retry_count > 0:
        await asyncio.sleep(3)
        return await perform_operation(identifier, total_elapsed_time, total_retry_count)
    else:
        return ApplicationResponse(
            application_id=identifier,
            status=ApplicationStatusResponse.Failure,
            description="Both services failed",
            last_request_time=end_time,
            retriesCount=retry_count
        )

# Пример использования
async def main():
    result = await perform_operation("example_id")
    print(result)

# Инициализация asyncio loop и запуск асинхронной операции
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
