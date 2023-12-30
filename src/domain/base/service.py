"""서비스 추상화 클래스 모듈입니다."""
from functools import singledispatch


@singledispatch
def to_dto(obj: object | None) -> object | None:
    """객체를 DTO 객체로 변환합니다."""
    if obj is None:
        return None
    raise NotImplementedError(f"지원하지 않는 타입입니다. type={type(obj)}")
