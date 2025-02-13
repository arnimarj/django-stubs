import sys
from io import BytesIO
from typing import (
    Any,
    BinaryIO,
    Dict,
    Iterable,
    List,
    Mapping,
    NoReturn,
    Optional,
    Pattern,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.base import SessionBase
from django.contrib.sites.models import Site
from django.core.files import uploadedfile, uploadhandler
from django.urls import ResolverMatch
from django.utils.datastructures import CaseInsensitiveMapping, ImmutableList, MultiValueDict

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal

RAISE_ERROR: object = ...
host_validation_re: Pattern[str] = ...

class UnreadablePostError(OSError): ...
class RawPostDataException(Exception): ...

UploadHandlerList = Union[List[uploadhandler.FileUploadHandler], ImmutableList[uploadhandler.FileUploadHandler]]

class HttpHeaders(CaseInsensitiveMapping[str]):
    HTTP_PREFIX: str = ...
    UNPREFIXED_HEADERS: Set[str] = ...
    def __init__(self, environ: Mapping[str, Any]) -> None: ...
    @classmethod
    def parse_header_name(cls, header: str) -> Optional[str]: ...

class HttpRequest(BytesIO):
    GET: _ImmutableQueryDict = ...
    POST: _ImmutableQueryDict = ...
    COOKIES: Dict[str, str] = ...
    META: Dict[str, Any] = ...
    FILES: MultiValueDict[str, uploadedfile.UploadedFile] = ...
    path: str = ...
    path_info: str = ...
    method: Optional[str] = ...
    resolver_match: Optional[ResolverMatch] = ...
    content_type: Optional[str] = ...
    content_params: Optional[Dict[str, str]] = ...
    user: Union[AbstractBaseUser, AnonymousUser]
    site: Site
    session: SessionBase
    _stream: BinaryIO
    # The magic. If we instantiate HttpRequest directly somewhere, it has
    # mutable GET and POST. However, both ASGIRequest and WSGIRequest have immutable,
    # so when we use HttpRequest to refer to any of them we want exactly this.
    # Case when some function creates *exactly* HttpRequest (not subclass)
    # remain uncovered, however it's probably the best solution we can afford.
    def __new__(cls) -> _MutableHttpRequest: ...
    # When both __init__ and __new__ are present, mypy will prefer __init__
    # (see comments in mypy.checkmember.type_object_type)
    # def __init__(self) -> None: ...
    def get_host(self) -> str: ...
    def get_port(self) -> str: ...
    def get_full_path(self, force_append_slash: bool = ...) -> str: ...
    def get_full_path_info(self, force_append_slash: bool = ...) -> str: ...
    def get_signed_cookie(
        self, key: str, default: Any = ..., salt: str = ..., max_age: Optional[int] = ...
    ) -> Optional[str]: ...
    def get_raw_uri(self) -> str: ...
    def build_absolute_uri(self, location: Optional[str] = ...) -> str: ...
    @property
    def scheme(self) -> Optional[str]: ...
    def is_secure(self) -> bool: ...
    def is_ajax(self) -> bool: ...
    @property
    def encoding(self) -> Optional[str]: ...
    @encoding.setter
    def encoding(self, val: str) -> None: ...
    @property
    def upload_handlers(self) -> UploadHandlerList: ...
    @upload_handlers.setter
    def upload_handlers(self, upload_handlers: UploadHandlerList) -> None: ...
    @property
    def accepted_types(self) -> List[MediaType]: ...
    def __repr__(self) -> str: ...
    def parse_file_upload(
        self, META: Mapping[str, Any], post_data: BinaryIO
    ) -> Tuple[QueryDict, MultiValueDict[str, uploadedfile.UploadedFile]]: ...
    @property
    def headers(self) -> HttpHeaders: ...
    @property
    def body(self) -> bytes: ...
    def _load_post_and_files(self) -> None: ...
    def accepts(self, media_type: str) -> bool: ...

class _MutableHttpRequest(HttpRequest):
    GET: QueryDict = ...  # type: ignore[assignment]
    POST: QueryDict = ...  # type: ignore[assignment]

_Q = TypeVar("_Q", bound="QueryDict")
_Z = TypeVar("_Z")

class QueryDict(MultiValueDict[str, str]):
    _mutable: bool = ...
    # We can make it mutable only by specifying `mutable=True`.
    # It can be done a) with kwarg and b) with pos. arg. `overload` has
    # some problems with args/kwargs + Literal, so two signatures are required.
    # ('querystring', True, [...])
    @overload
    def __init__(
        self: QueryDict,
        query_string: Optional[Union[str, bytes]],
        mutable: Literal[True],
        encoding: Optional[str] = ...,
    ) -> None: ...
    # ([querystring='string',] mutable=True, [...])
    @overload
    def __init__(
        self: QueryDict,
        *,
        mutable: Literal[True],
        query_string: Optional[Union[str, bytes]] = ...,
        encoding: Optional[str] = ...,
    ) -> None: ...
    # Otherwise it's immutable
    @overload
    def __init__(  # type: ignore[misc]
        self: _ImmutableQueryDict,
        query_string: Optional[Union[str, bytes]] = ...,
        mutable: bool = ...,
        encoding: Optional[str] = ...,
    ) -> None: ...
    @classmethod
    def fromkeys(  # type: ignore
        cls: Type[_Q],
        iterable: Iterable[Union[bytes, str]],
        value: Union[str, bytes] = ...,
        mutable: bool = ...,
        encoding: Optional[str] = ...,
    ) -> _Q: ...
    @property
    def encoding(self) -> str: ...
    @encoding.setter
    def encoding(self, value: str) -> None: ...
    def __setitem__(self, key: Union[str, bytes], value: Union[str, bytes]) -> None: ...
    def __delitem__(self, key: Union[str, bytes]) -> None: ...
    def setlist(self, key: Union[str, bytes], list_: Iterable[Union[str, bytes]]) -> None: ...
    def setlistdefault(self, key: Union[str, bytes], default_list: Optional[List[str]] = ...) -> List[str]: ...
    def appendlist(self, key: Union[str, bytes], value: Union[str, bytes]) -> None: ...
    # Fake signature (because *args is used in source, but it fails with more that 1 argument)
    @overload
    def pop(self, key: Union[str, bytes], /) -> str: ...
    @overload
    def pop(self, key: Union[str, bytes], default: Union[str, _Z] = ..., /) -> Union[str, _Z]: ...
    def popitem(self) -> Tuple[str, str]: ...
    def clear(self) -> None: ...
    def setdefault(self, key: Union[str, bytes], default: Union[str, bytes, None] = ...) -> str: ...
    def copy(self) -> QueryDict: ...
    def urlencode(self, safe: Optional[str] = ...) -> str: ...

class _ImmutableQueryDict(QueryDict):
    _mutable: Literal[False]
    # def __init__(
    #     self, query_string: Optional[Union[str, bytes]] = ..., mutable: bool = ..., encoding: Optional[str] = ...
    # ) -> None: ...
    def __setitem__(self, key: Union[str, bytes], value: Union[str, bytes]) -> NoReturn: ...
    def __delitem__(self, key: Union[str, bytes]) -> NoReturn: ...
    def setlist(self, key: Union[str, bytes], list_: Iterable[Union[str, bytes]]) -> NoReturn: ...
    def setlistdefault(self, key: Union[str, bytes], default_list: Optional[List[str]] = ...) -> NoReturn: ...
    def appendlist(self, key: Union[str, bytes], value: Union[str, bytes]) -> NoReturn: ...
    # Fake signature (because *args is used in source, but it fails with more that 1 argument)
    @overload
    def pop(self, key: Union[str, bytes], /) -> NoReturn: ...
    @overload
    def pop(self, key: Union[str, bytes], default: Union[str, _Z] = ..., /) -> NoReturn: ...
    def popitem(self) -> NoReturn: ...
    def clear(self) -> NoReturn: ...
    def setdefault(self, key: Union[str, bytes], default: Union[str, bytes, None] = ...) -> NoReturn: ...
    def copy(self) -> QueryDict: ...  # type: ignore[override]
    def urlencode(self, safe: Optional[str] = ...) -> str: ...
    # Fakes for convenience (for `request.GET` and `request.POST`). If dict
    # was created by Django, there is no chance to hit `List[object]` (empty list)
    # edge case.
    def __getitem__(self, key: str) -> str: ...
    def dict(self) -> Dict[str, str]: ...  # type: ignore[override]

class MediaType:
    def __init__(self, media_type_raw_line: str) -> None: ...
    @property
    def is_all_types(self) -> bool: ...
    def match(self, other: str) -> bool: ...

@overload
def bytes_to_text(s: None, encoding: str) -> None: ...
@overload
def bytes_to_text(s: Union[bytes, str], encoding: str) -> str: ...
def split_domain_port(host: str) -> Tuple[str, str]: ...
def validate_host(host: str, allowed_hosts: Iterable[str]) -> bool: ...
