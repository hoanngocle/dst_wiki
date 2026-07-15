import hashlib
import json
import os
import random
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

from tools.crawl_wiki.parser import normalize_base_url


DEFAULT_USER_AGENT = "dst-wiki-crawler/1.0 (https://dontstarve.wiki.gg/)"
_TRANSIENT_API_CODES = {
    "maxlag",
    "readonly",
    "ratelimited",
    "internal_api_error_DBConnectionError",
}


class ClientError(RuntimeError):
    def __init__(
        self,
        message: str,
        retryable: bool,
        status: Optional[int] = None,
        code: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.retryable = retryable
        self.status = status
        self.code = code


@dataclass(frozen=True)
class DownloadResult:
    final_url: str
    byte_size: int
    sha256: str


class MediaWikiClient:
    def __init__(
        self,
        base_url: str,
        delay: float = 0.5,
        timeout: float = 30.0,
        max_attempts: int = 5,
        user_agent: str = DEFAULT_USER_AGENT,
        maxlag: int = 5,
        opener: Optional[Any] = None,
        monotonic: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        jitter: Callable[[], float] = random.random,
        require_https_downloads: bool = True,
    ) -> None:
        if delay < 0:
            raise ValueError("delay must be non-negative")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        if max_attempts <= 0:
            raise ValueError("max attempts must be positive")
        if not user_agent.strip():
            raise ValueError("user agent must not be empty")
        self.base_url = normalize_base_url(base_url)
        self.api_url = urllib.parse.urljoin(self.base_url, "api.php")
        self.delay = float(delay)
        self.timeout = float(timeout)
        self.max_attempts = int(max_attempts)
        self.user_agent = user_agent.strip()
        self.maxlag = int(maxlag)
        self.opener = opener or urllib.request.build_opener()
        self.monotonic = monotonic
        self.sleep = sleep
        self.jitter = jitter
        self.require_https_downloads = require_https_downloads
        self._last_request_at: Optional[float] = None

    def _wait_for_rate_limit(self) -> None:
        now = self.monotonic()
        if self._last_request_at is not None:
            remaining = self._last_request_at + self.delay - now
            if remaining > 0:
                self.sleep(remaining)
        self._last_request_at = self.monotonic()

    def _request(self, url: str, accept: str) -> urllib.request.Request:
        return urllib.request.Request(
            url,
            headers={"User-Agent": self.user_agent, "Accept": accept},
            method="GET",
        )

    def _backoff(
        self, attempt: int, retry_after: Optional[str] = None
    ) -> None:
        delay: Optional[float] = None
        if retry_after is not None:
            try:
                delay = max(0.0, float(retry_after))
            except ValueError:
                delay = None
        if delay is None:
            delay = min(60.0, float(2 ** (attempt - 1))) + max(
                0.0, float(self.jitter())
            )
        self.sleep(delay)

    def _api(self, params: Mapping[str, Any]) -> Dict[str, Any]:
        merged: Dict[str, Any] = {
            "format": "json",
            "formatversion": 2,
            "maxlag": self.maxlag,
        }
        merged.update(params)
        url = self.api_url + "?" + urllib.parse.urlencode(merged)
        last_error: Optional[ClientError] = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                self._wait_for_rate_limit()
                with self.opener.open(
                    self._request(url, "application/json"),
                    timeout=self.timeout,
                ) as response:
                    payload = response.read()
                try:
                    decoded = json.loads(payload.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as error:
                    raise ClientError(
                        "MediaWiki returned invalid JSON: {}".format(error),
                        retryable=False,
                    )
                if not isinstance(decoded, dict):
                    raise ClientError(
                        "MediaWiki JSON response must be an object",
                        retryable=False,
                    )
                api_error = decoded.get("error")
                if isinstance(api_error, Mapping):
                    code_value = api_error.get("code")
                    code = code_value if isinstance(code_value, str) else None
                    info = api_error.get("info", "MediaWiki API error")
                    retryable = bool(
                        code in _TRANSIENT_API_CODES
                        or (code and code.startswith("internal_api_error_"))
                    )
                    raised = ClientError(
                        "{}: {}".format(code or "api_error", info),
                        retryable=retryable,
                        code=code,
                    )
                    if retryable and attempt < self.max_attempts:
                        self._backoff(attempt)
                        last_error = raised
                        continue
                    raise raised
                return decoded
            except urllib.error.HTTPError as error:
                error.close()
                retryable = error.code == 429 or 500 <= error.code <= 599
                raised = ClientError(
                    "HTTP {} for {}".format(error.code, self.api_url),
                    retryable=retryable,
                    status=error.code,
                )
                if retryable and attempt < self.max_attempts:
                    self._backoff(attempt, error.headers.get("Retry-After"))
                    last_error = raised
                    continue
                raise raised
            except (urllib.error.URLError, TimeoutError, socket.timeout) as error:
                raised = ClientError(
                    "network error for {}: {}".format(self.api_url, error),
                    retryable=True,
                )
                if attempt < self.max_attempts:
                    self._backoff(attempt)
                    last_error = raised
                    continue
                raise raised

        if last_error is not None:
            raise ClientError(
                "request failed after {} attempts: {}".format(
                    self.max_attempts, last_error
                ),
                retryable=True,
                status=last_error.status,
                code=last_error.code,
            )
        raise ClientError("request failed", retryable=True)

    def list_allpages(
        self, namespace: int, continuation: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        params: Dict[str, Any] = {
            "action": "query",
            "list": "allpages",
            "apnamespace": namespace,
            "aplimit": "max",
        }
        if continuation:
            params["apcontinue"] = continuation
        response = self._api(params)
        query = response.get("query")
        pages = query.get("allpages") if isinstance(query, Mapping) else None
        if not isinstance(pages, list) or not all(
            isinstance(page, dict) for page in pages
        ):
            raise ClientError(
                "allpages response is missing query.allpages",
                retryable=False,
            )
        continuation_data = response.get("continue")
        next_token = (
            continuation_data.get("apcontinue")
            if isinstance(continuation_data, Mapping)
            else None
        )
        if next_token is not None and not isinstance(next_token, str):
            raise ClientError(
                "allpages continuation token must be a string",
                retryable=False,
            )
        return pages, next_token

    def get_page(self, page_id: int) -> Dict[str, Any]:
        response = self._api(
            {
                "action": "query",
                "pageids": page_id,
                "prop": "info|revisions",
                "rvprop": "ids|timestamp|sha1|content|contentmodel",
                "rvslots": "main",
            }
        )
        page = self._first_query_page(response, "page")
        if page.get("missing") is True or not isinstance(
            page.get("revisions"), list
        ):
            raise ClientError(
                "page {} is missing its latest revision".format(page_id),
                retryable=False,
            )
        return page

    def parse_page(self, page_id: int) -> Dict[str, Any]:
        response = self._api(
            {
                "action": "parse",
                "pageid": page_id,
                "prop": "text|links|categories|images|displaytitle|properties",
            }
        )
        parsed = response.get("parse")
        if not isinstance(parsed, dict):
            raise ClientError(
                "parse response is missing parse object", retryable=False
            )
        return parsed

    def get_image_info(self, title: str) -> Dict[str, Any]:
        response = self._api(
            {
                "action": "query",
                "titles": title,
                "prop": "imageinfo",
                "iiprop": "url|size|mime|sha1",
            }
        )
        page = self._first_query_page(response, "image")
        imageinfo = page.get("imageinfo")
        if page.get("missing") is True or not isinstance(
            imageinfo, list
        ) or not imageinfo or not isinstance(imageinfo[0], dict):
            raise ClientError(
                "image {} has no original file metadata".format(title),
                retryable=False,
            )
        result = dict(imageinfo[0])
        result["page_id"] = page.get("pageid")
        result["title"] = page.get("title", title)
        return result

    @staticmethod
    def _first_query_page(
        response: Mapping[str, Any], subject: str
    ) -> Dict[str, Any]:
        query = response.get("query")
        pages = query.get("pages") if isinstance(query, Mapping) else None
        if not isinstance(pages, list) or not pages or not isinstance(
            pages[0], dict
        ):
            raise ClientError(
                "{} response is missing query.pages".format(subject),
                retryable=False,
            )
        return pages[0]

    def download(self, url: str, destination: Path) -> DownloadResult:
        requested_scheme = urllib.parse.urlsplit(url).scheme.lower()
        if self.require_https_downloads and requested_scheme != "https":
            raise ClientError(
                "original image URL must use HTTPS", retryable=False
            )
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)

        for attempt in range(1, self.max_attempts + 1):
            try:
                self._wait_for_rate_limit()
                with self.opener.open(
                    self._request(url, "application/octet-stream,image/*"),
                    timeout=self.timeout,
                ) as response:
                    final_url = response.geturl()
                    if (
                        self.require_https_downloads
                        and urllib.parse.urlsplit(final_url).scheme.lower()
                        != "https"
                    ):
                        raise ClientError(
                            "redirected original image URL must use HTTPS",
                            retryable=False,
                        )
                    digest = hashlib.sha256()
                    byte_size = 0
                    with destination.open("wb") as output:
                        while True:
                            chunk = response.read(64 * 1024)
                            if not chunk:
                                break
                            output.write(chunk)
                            digest.update(chunk)
                            byte_size += len(chunk)
                        output.flush()
                        os.fsync(output.fileno())
                    content_length = response.headers.get("Content-Length")
                    if content_length is not None and int(content_length) != byte_size:
                        raise ClientError(
                            "download size does not match Content-Length",
                            retryable=True,
                        )
                return DownloadResult(
                    final_url=final_url,
                    byte_size=byte_size,
                    sha256=digest.hexdigest(),
                )
            except ClientError as error:
                destination.unlink(missing_ok=True)
                if error.retryable and attempt < self.max_attempts:
                    self._backoff(attempt)
                    continue
                raise
            except urllib.error.HTTPError as error:
                destination.unlink(missing_ok=True)
                error.close()
                retryable = error.code == 429 or 500 <= error.code <= 599
                raised = ClientError(
                    "HTTP {} downloading image".format(error.code),
                    retryable=retryable,
                    status=error.code,
                )
                if retryable and attempt < self.max_attempts:
                    self._backoff(attempt, error.headers.get("Retry-After"))
                    continue
                raise raised
            except (urllib.error.URLError, TimeoutError, socket.timeout, OSError) as error:
                destination.unlink(missing_ok=True)
                raised = ClientError(
                    "image download failed: {}".format(error), retryable=True
                )
                if attempt < self.max_attempts:
                    self._backoff(attempt)
                    continue
                raise raised

        raise ClientError(
            "image download failed after {} attempts".format(
                self.max_attempts
            ),
            retryable=True,
        )
