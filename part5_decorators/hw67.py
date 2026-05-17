import json
from urllib.request import urlopen
from datetime import datetime, timezone
from functools import wraps


INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."


class BreakerError(Exception):
    def __init__(self, func_name, block_time, original_error=None):
        self.func_name = func_name
        self.block_time = block_time

        super().__init__(TOO_MUCH)

        if original_error is not None:
            self.__cause__ = original_error


class CircuitBreaker:
    def __init__(
        self,
        critical_count=5,
        time_to_recover=30,
        triggers_on=Exception,
    ):
        errors = []

        if type(critical_count) != int or critical_count <= 0:
            errors.append(ValueError(INVALID_CRITICAL_COUNT))

        if type(time_to_recover) != int or time_to_recover <= 0:
            errors.append(ValueError(INVALID_RECOVERY_TIME))

        if errors:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)

        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on

        self.errors_count = 0
        self.last_error_time = None
        self.is_open = False

    def __call__(self, func):
        func_name = f"{func.__module__}.{func.__name__}"

        @wraps(func)
        def wrapper(*args, **kwargs):
            # если автомат открыт
            if self.is_open:
                now = datetime.now(timezone.utc)

                # проверяем прошло ли время блокировки
                if self.last_error_time is not None:
                    seconds = (now - self.last_error_time).total_seconds()

                    # если время еще не прошло
                    if seconds < self.time_to_recover:
                        raise BreakerError(
                            func_name,
                            self.last_error_time,
                        )

                # пробуем снова выполнить функцию
                try:
                    result = func(*args, **kwargs)

                    # если успешно -> закрываем автомат
                    self.is_open = False
                    self.errors_count = 0

                    return result

                except Exception as error:
                    self.last_error_time = datetime.now(timezone.utc)

                    raise BreakerError(
                        func_name,
                        self.last_error_time,
                        error,
                    )

            # обычная работа
            try:
                result = func(*args, **kwargs)

                # если запрос успешный
                self.errors_count = 0

                return result

            except Exception as error:
                # реагируем только на нужный тип ошибок
                if isinstance(error, self.triggers_on):
                    self.errors_count += 1
                    self.last_error_time = datetime.now(timezone.utc)

                    # если ошибок слишком много
                    if self.errors_count >= self.critical_count:
                        self.is_open = True

                        raise BreakerError(
                            func_name,
                            self.last_error_time,
                            error,
                        )

                # пробрасываем оригинальную ошибку
                raise

        return wrapper


circuit_breaker = CircuitBreaker(5, 30, Exception)


# @circuit_breaker
def get_comments(post_id: int):
    response = urlopen(
        f"https://jsonplaceholder.typicode.com/comments?postId={post_id}"
    )

    data = response.read()

    return json.loads(data)


if __name__ == "__main__":
    comments = get_comments(1)

    print(comments)