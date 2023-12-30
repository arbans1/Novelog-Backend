"""유효성 검사 모듈"""
from abc import ABCMeta, abstractmethod

__all__ = ("Validator",)


class Validator(metaclass=ABCMeta):
    """유효성 검사 추상 클래스"""

    @classmethod
    @property
    @abstractmethod
    def errors(cls) -> tuple:
        """에러 메시지"""
        raise NotImplementedError

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """유효성 검사"""
        raise NotImplementedError
