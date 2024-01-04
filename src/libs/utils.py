"""유틸리티 함수들을 정의합니다."""
from typing import Any, Iterable
from urllib.parse import urlparse


def merge_dictionaries(*dicts_to_merge: dict[str, Any]) -> dict[str, Any]:
    """여러 사전들을 병합하여 하나의 사전으로 만듭니다.

    각 사전의 키와 값을 병합하는 규칙은 다음과 같습니다:
    - 같은 키에 대한 값들이 모두 사전일 경우, 재귀적으로 병합합니다.
    - 값들이 반복 가능한 객체일 경우(문자열 제외), 나중 값의 타입에 맞추어 병합합니다.
    - 그 외의 경우, 나중에 오는 값으로 덮어씁니다.

    Args:
        *dicts_to_merge (dict[str, Any]): 병합할 사전들.

    Returns:
        dict[str, Any]: 병합된 결과 사전.

    Examples:
        >>> dict1 = {"a": 1, "b": [2, 3]}
        >>> dict2 = {"b": [4, 5], "c": 7}
        >>> result = merge_dictionaries(dict1, dict2)
        >>> result
        {'a': 1, 'b': [2, 3, 4, 5], 'c': 7}
    """
    merged_result = {}

    for current_dict in dicts_to_merge:
        for key, value in current_dict.items():
            if key in merged_result:
                merged_result[key] = merge_values(merged_result[key], value)
            else:
                merged_result[key] = value

    return merged_result


def merge_values(existing_value: Any, new_value: Any) -> Any:
    """기존 값과 새로운 값을 병합합니다.

    Args:
        existing_value (Any): 기존 값.
        new_value (Any): 새로운 값.

    Returns:
        Any: 병합된 결과.
    """
    if isinstance(existing_value, dict) and isinstance(new_value, dict):
        return merge_dictionaries(existing_value, new_value)
    if (
        isinstance(existing_value, Iterable)
        and not isinstance(existing_value, str)
        and isinstance(new_value, Iterable)
        and not isinstance(new_value, str)
    ):
        return type(new_value)(existing_value) + type(new_value)(new_value)
    return new_value


def parse_last_path(url: str, is_digit: bool = False) -> str | None:
    """주어진 URL에서 마지막 경로를 추출합니다.

    Args:
        url (str): 분석할 URL.
        is_digit (bool): 마지막 경로가 숫자인지 확인할지 여부. 기본값은 True입니다.

    Returns:
        str | None: 추출된 경로, 숫자여야 하는데 아닌 경우는 None.

    예시:
        >>> parse_last_path("https://ridibooks.com/books/5211000001?_rdt_sid=fantasy_webnovel_reading_book&_rdt_idx=0")
        '5211000001'
    """
    parsed = urlparse(url)

    # 경로의 마지막 부분을 추출
    path_parts = parsed.path.split("/")
    if path_parts:
        last_part = path_parts[-1]
        if is_digit and not last_part.isdigit():
            return None
        return last_part

    return None
