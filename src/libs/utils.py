"""유틸리티 함수들을 정의합니다."""
from typing import Any, Iterable


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
