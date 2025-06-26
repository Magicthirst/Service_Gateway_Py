from typing import Literal

from pydantic import BaseModel


class Host(BaseModel):
    uuid: str = 'some-host_uuid'
    only_friends: bool = True
    allow_nonames: bool = False
    friends: list[str] = ['this-gui-host_uuid', 'other-guy-host_uuid']
    banlist: list[str] = ['that-guy-host_uuid']


class Token(BaseModel):
    token: str


class Message(BaseModel):
    message: str


class NotFoundThisOrOther(BaseModel):
    message: Literal['not found this', 'not found other']


class NotFoundOtherOrOtherOrNotFoundIsPredicateResult(BaseModel):
    message: Literal['not found this', 'not found other', '~none~']


class LaunchSessionResponse(BaseModel):
    session_id: int
    source_of_truth_key: str
