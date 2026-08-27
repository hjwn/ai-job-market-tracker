"""Minimal client for the Saramin Job Search API.

The collector intentionally returns the verified raw JSON object. Mapping API
fields to the shared JobPosting model belongs to the normalization layer and is
left until real responses have been collected and validated.
"""

from __future__ import annotations

import argparse
import json
import socket
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from src.config import ConfigurationError, load_settings


SARAMIN_JOB_SEARCH_ENDPOINT = "https://oapi.saramin.co.kr/job-search"
DEFAULT_TIMEOUT_SECONDS = 10.0

# Keep external parameter names in one place so API changes remain localized.
QUERY_PARAMETERS = {
    "access_key": "access-key",
    "keywords": "keywords",
    "start": "start",
    "count": "count",
}


class SaraminCollectorError(RuntimeError):
    """Base error for Saramin collection failures."""


class SaraminAPIError(SaraminCollectorError):
    """Raised when the Saramin API request or response is unsuccessful."""


class SaraminResponseError(SaraminCollectorError):
    """Raised when the response cannot be parsed as the expected JSON object."""


@dataclass(frozen=True, slots=True)
class SaraminSearchParams:
    """Parameters for one result page.

    ``start`` is separated from request execution so pagination can later
    iterate this value without changing the HTTP or parsing code.
    """

    keywords: str | None = None
    start: int = 0
    count: int = 10

    def __post_init__(self) -> None:
        if self.start < 0:
            raise ValueError("start는 0 이상이어야 합니다.")
        if not 1 <= self.count <= 110:
            raise ValueError("count는 1 이상 110 이하여야 합니다.")

    def as_query_params(self) -> dict[str, str | int]:
        params: dict[str, str | int] = {
            QUERY_PARAMETERS["start"]: self.start,
            QUERY_PARAMETERS["count"]: self.count,
        }
        if self.keywords:
            params[QUERY_PARAMETERS["keywords"]] = self.keywords
        return params


class SaraminCollector:
    """Fetch raw job-search pages from Saramin."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        endpoint: str = SARAMIN_JOB_SEARCH_ENDPOINT,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        resolved_key = api_key.strip() if api_key else None
        if not resolved_key:
            resolved_key = load_settings().require_saramin_api_key()
        if timeout <= 0:
            raise ValueError("timeout은 0보다 커야 합니다.")

        self._api_key = resolved_key
        self.endpoint = endpoint
        self.timeout = timeout

    def build_query_params(
        self,
        search: SaraminSearchParams,
    ) -> dict[str, str | int]:
        """Build API query parameters, including the private access key."""
        params = search.as_query_params()
        params[QUERY_PARAMETERS["access_key"]] = self._api_key
        return params

    def request_page(self, search: SaraminSearchParams) -> bytes:
        """Execute one HTTP request and return its unparsed response body."""
        query_string = urlencode(self.build_query_params(search))
        request = Request(
            f"{self.endpoint}?{query_string}",
            headers={"Accept": "application/json"},
            method="GET",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                return response.read()
        except HTTPError as exc:
            raise SaraminAPIError(
                f"사람인 API 요청에 실패했습니다 (HTTP {exc.code}). "
                "요청 조건과 API 이용 상태를 확인하세요."
            ) from None
        except (TimeoutError, socket.timeout):
            raise SaraminAPIError(
                f"사람인 API 요청이 {self.timeout:g}초 안에 완료되지 않았습니다."
            ) from None
        except URLError:
            raise SaraminAPIError(
                "사람인 API에 연결할 수 없습니다. 네트워크 상태를 확인하세요."
            ) from None

    @staticmethod
    def parse_response(response_body: bytes | str) -> dict[str, Any]:
        """Parse a successful response while preserving its raw field layout."""
        try:
            if isinstance(response_body, bytes):
                response_body = response_body.decode("utf-8")
            payload = json.loads(response_body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise SaraminResponseError(
                "사람인 API 응답을 JSON 객체로 해석할 수 없습니다."
            ) from None

        if not isinstance(payload, dict):
            raise SaraminResponseError(
                "사람인 API 응답의 최상위 값이 JSON 객체가 아닙니다."
            )

        # The official API documents top-level code/message error responses.
        if "code" in payload and "message" in payload and "jobs" not in payload:
            raise SaraminAPIError(
                f"사람인 API가 오류를 반환했습니다 (code={payload['code']})."
            )

        return payload

    def fetch_page(
        self,
        search: SaraminSearchParams | None = None,
    ) -> dict[str, Any]:
        """Fetch and parse one page of raw job-search results."""
        request_params = search or SaraminSearchParams()
        response_body = self.request_page(request_params)
        return self.parse_response(response_body)


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="사람인 채용공고 원본 JSON 조회")
    parser.add_argument("--keywords", help="검색할 키워드")
    parser.add_argument("--start", type=int, default=0, help="0부터 시작하는 페이지 번호")
    parser.add_argument("--count", type=int, default=10, help="페이지당 결과 수 (1~110)")
    return parser


def main() -> int:
    """Run a single-page collection from the command line."""
    args = _build_argument_parser().parse_args()

    try:
        collector = SaraminCollector()
        payload = collector.fetch_page(
            SaraminSearchParams(
                keywords=args.keywords,
                start=args.start,
                count=args.count,
            )
        )
    except (ConfigurationError, SaraminCollectorError, ValueError) as exc:
        print(f"오류: {exc}")
        return 1

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
