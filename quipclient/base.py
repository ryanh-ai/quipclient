"""Base client implementation for Quip API."""

import datetime
import json
import logging
import os
import ssl
import sys
import time
import zlib
from diskcache import Cache

PY3 = sys.version_info > (3,)

if PY3:
    import urllib.request
    import urllib.parse
    import urllib.error

    Request = urllib.request.Request
    urlencode = urllib.parse.urlencode
    urlopen = urllib.request.urlopen
    HTTPError = urllib.error.HTTPError

    iteritems = dict.items

else:
    import urllib
    import urllib2

    Request = urllib2.Request
    urlencode = urllib.urlencode
    urlopen = urllib2.urlopen
    HTTPError = urllib2.HTTPError

    iteritems = dict.iteritems


class QuipError(Exception):
    def __init__(self, code, message, http_error):
        Exception.__init__(self, "%d: %s" % (code, message))
        self.code = code
        self.http_error = http_error


class BaseQuipClient:
    """Base class for Quip API clients"""
    
    # Cache TTL constants (in seconds)
    ONE_HOUR = 3600
    ONE_DAY = 86400
    THIRTY_DAYS = 2592000

    # Maximum entities per API request
    MAX_USERS_PER_REQUEST = 100
    MAX_FOLDERS_PER_REQUEST = 100  
    MAX_THREADS_PER_REQUEST = 10

    def __init__(self, access_token=None, client_id=None, client_secret=None,
                 base_url=None, request_timeout=None, cache_dir=None):
        """Initialize the base client.
        
        Args:
            access_token: Quip API access token
            client_id: OAuth client ID
            client_secret: OAuth client secret  
            base_url: Base URL for API requests
            request_timeout: Request timeout in seconds
            cache_dir: Directory for caching responses
        """
        # Rate limit tracking
        self._rate_limit = None  # Requests per minute limit
        self._rate_limit_remaining = None  # Remaining requests this minute
        self._rate_limit_reset = None  # UTC timestamp when limit resets
        self._company_rate_limit = None  # Company requests per minute
        self._company_rate_limit_remaining = None  # Remaining company requests
        self._company_rate_limit_reset = None  # UTC timestamp for company reset
        self._company_retry_after = None  # Seconds until next allowed request

        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url if base_url else "https://platform.quip.com"
        self.request_timeout = request_timeout if request_timeout else 10
        
        if cache_dir is None:
            cache_dir = os.path.join(os.getcwd(), '.cache')
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        self._cache = Cache(cache_dir)
        self._cache.stats(enable=True)
        self._user_id = None

    def _fetch_json(self, path, post_data=None, cache=True, cache_ttl=None, 
                   paginate=False, **args):
        """Fetches JSON from the API, handling pagination if requested.
        
        Args:
            path: API endpoint path
            post_data: Optional POST data
            cache: Whether to use caching
            cache_ttl: Cache TTL in seconds
            paginate: Whether to automatically handle pagination
            **args: Additional URL parameters
            
        Returns:
            Combined results from all pages if paginate=True,
            otherwise returns single page response.
        """
        url = self._url(path, **args)

        # Check if we need to wait for rate limits
        now = time.time()
        if self._rate_limit_reset and now < self._rate_limit_reset and self._rate_limit_remaining == 0:
            sleep_time = self._rate_limit_reset - now
            time.sleep(sleep_time)
        elif (self._company_retry_after and now < self._company_rate_limit_reset and 
              (self._company_rate_limit_remaining == 0 or self._company_rate_limit_remaining is None)):
            sleep_time = self._company_rate_limit_reset - now
            time.sleep(sleep_time)

        # Check cache if enabled and this is a GET request
        if cache and not post_data and cache_ttl:
            cache_key = f"{self._user_id or '_'}:{url}"
            cached_data = self._cache.get(cache_key)
            if cached_data:
                data = json.loads(zlib.decompress(cached_data).decode())
                if isinstance(data, dict) and data.get("error"):
                    raise QuipError(data["code"], data["message"], None)
                return data

        request = Request(url=url)
        if post_data:
            post_data = dict((k, v) for k, v in post_data.items()
                            if v or isinstance(v, int))
            request_data = urlencode(self._clean(**post_data))
            if PY3:
                request.data = request_data.encode()
            else:
                request.data = request_data

        if self.access_token:
            request.add_header("Authorization", "Bearer " + self.access_token)
            
        try:
            response = urlopen(request, timeout=self.request_timeout)
            
            # Update rate limit tracking from response headers
            self._rate_limit = int(response.headers.get('X-RateLimit-Limit')) if 'X-RateLimit-Limit' in response.headers else None
            self._rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining')) if 'X-RateLimit-Remaining' in response.headers else None
            self._rate_limit_reset = float(response.headers.get('X-RateLimit-Reset')) if 'X-RateLimit-Reset' in response.headers else None
            
            self._company_rate_limit = int(response.headers.get('X-Company-RateLimit-Limit')) if 'X-Company-RateLimit-Limit' in response.headers else None
            self._company_rate_limit_remaining = int(response.headers.get('X-Company-RateLimit-Remaining')) if 'X-Company-RateLimit-Remaining' in response.headers else None
            self._company_rate_limit_reset = float(response.headers.get('X-Company-RateLimit-Reset')) if 'X-Company-RateLimit-Reset' in response.headers else None
            self._company_retry_after = int(response.headers.get('X-Company-Retry-After')) if 'X-Company-Retry-After' in response.headers else None
            
            response_data = response.read().decode()
            result = json.loads(response_data)
            
            # Cache successful GET responses if caching is enabled
            if cache and not post_data and cache_ttl:
                cache_key = f"{self._user_id or '_'}:{url}"
                self._cache.set(
                    cache_key,
                    zlib.compress(json.dumps(result).encode()),
                    cache_ttl
                )
            
            # Handle pagination if requested
            if paginate and not post_data:
                if "response_metadata" in result:
                    cursor = result["response_metadata"].get("next_cursor")
                    if cursor and isinstance(cursor, str) and cursor.strip():
                        next_page = self._fetch_json(path, cache=False, cursor=cursor, **args)
                        
                        # Merge the results
                        if "folders" in result and "folders" in next_page:
                            result["folders"].extend(next_page["folders"])
                        elif "html" in result and "html" in next_page:
                            result["html"] += next_page["html"]
                            
                    # Always ensure response_metadata exists with empty cursor
                    if "response_metadata" not in result:
                        result["response_metadata"] = {}
                    result["response_metadata"]["next_cursor"] = ""
                        
            return result

        except HTTPError as error:
            try:
                error_data = error.read().decode()
                if error_data:
                    error_json = json.loads(error_data)
                    message = error_json["error_description"]
                else:
                    message = error.reason
                    
                if cache and not post_data and cache_ttl:
                    cache_key = f"{self._user_id or '_'}:{url}"
                    error_cache = {
                        "error": True,
                        "code": error.code,
                        "message": message
                    }
                    self._cache.set(
                        cache_key,
                        zlib.compress(json.dumps(error_cache).encode()),
                        cache_ttl
                    )
            except Exception:
                raise error
            raise QuipError(error.code, message, error)

    def _cached_get(self, endpoint, ids, cache_ttl=THIRTY_DAYS, batch_size=100, cache=True):
        """Helper method to handle cached bulk entity fetching.
        
        Args:
            endpoint: API endpoint (e.g. "threads", "users", "folders")
            ids: List of entity IDs to fetch
            cache_ttl: Cache TTL in seconds
            batch_size: Number of items to fetch per request
            cache: Whether to use caching (default True)
            
        Returns:
            Dictionary of entity data keyed by ID
        """
        result = {}
        uncached_ids = []
        
        # Check cache for each ID if caching is enabled
        if cache:
            for entity_id in ids:
                cache_key = f"{self._user_id or '_'}:{endpoint}/{entity_id}"
                cached_data = self._cache.get(cache_key)
                if cached_data:
                    try:
                        entity_data = json.loads(zlib.decompress(cached_data).decode())
                        result.update(entity_data)
                    except:
                        uncached_ids.append(entity_id)
                else:
                    uncached_ids.append(entity_id)
        else:
            uncached_ids = ids
        
        # Only make API calls if we have uncached IDs
        if uncached_ids:
            new_data = {}
            # Process uncached IDs in batches
            for i in range(0, len(uncached_ids), batch_size):
                batch = uncached_ids[i:i + batch_size]
                batch_data = self._fetch_json(f"{endpoint}/", ids=",".join(batch))
                new_data.update(batch_data)
            
            # Cache individual responses if caching is enabled
            if cache:
                for entity_id, entity_data in new_data.items():
                    cache_key = f"{self._user_id or '_'}:{endpoint}/{entity_id}"
                    entity_cache = {entity_id: entity_data}
                    self._cache.set(
                        cache_key,
                        zlib.compress(json.dumps(entity_cache).encode()),
                        cache_ttl
                    )
            
            result.update(new_data)
            
        return result

    def _clean(self, **args):
        """Clean and encode parameters for API requests."""
        return dict((k, str(v) if isinstance(v, int) else v.encode("utf-8"))
                    for k, v in args.items() if v or isinstance(v, int))

    def _url(self, path, cursor=None, **args):
        """Construct API URL with parameters."""
        # Handle API version prefix
        if path.startswith("2/"):
            url = self.base_url + "/2/" + path[2:]
        else:
            url = self.base_url + "/1/" + path
        
        # Handle cursor separately to ensure it's included in URL when present
        if cursor:
            args['cursor'] = cursor
            
        args = self._clean(**args)
        if args:
            url += "?" + urlencode(args)
        return url

    def _urlopen(self, request):
        """Internal method to fetch data using the configured urlopen"""
        return urlopen(request, timeout=self.request_timeout)

    def get_blob(self, thread_id, blob_id):
        """Returns a file-like object with the contents of the given blob from
        the given thread.

        The object is described in detail here:
        https://docs.python.org/2/library/urllib2.html#urllib2.urlopen
        """
        request = Request(
            url=self._url("blob/%s/%s" % (thread_id, blob_id)))
        if self.access_token:
            request.add_header("Authorization", "Bearer " + self.access_token)
        try:
            return self._urlopen(request)
        except HTTPError as error:
            try:
                error_data = error.read().decode()
                error_json = json.loads(error_data)
                message = error_json["error_description"]
                
                # Cache 403 errors if caching is enabled
                request_url = request.get_full_url()
                if self._cache and error.code == 403:
                    cache_key = f"{self._user_id or '_'}:{request_url}"
                    self._cache.set(
                        cache_key,
                        zlib.compress(error_data.encode()),
                        self.ONE_HOUR
                    )
            except Exception:
                raise error
            raise QuipError(error.code, message, error)

    def put_blob(self, thread_id, blob, name=None):
        """Uploads an image or other blob to the given Quip thread. Returns an
        ID that can be used to add the image to the document of the thread.

        blob can be any file-like object. Requires the 'requests' module.
        """
        import requests
        url = "blob/" + thread_id
        headers = None
        if self.access_token:
            headers = {"Authorization": "Bearer " + self.access_token}
        if name:
            blob = (name, blob)
        try:
            response = requests.request(
                "post", self._url(url), timeout=self.request_timeout,
                files={"blob": blob}, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            try:
                # Extract the developer-friendly error message from the response
                message = error.response.json()["error_description"]
            except Exception:
                raise error
            raise QuipError(error.response.status_code, message, error)

    def parse_micros(self, usec):
        """Returns a `datetime` for the given microsecond string"""
        return datetime.datetime.utcfromtimestamp(usec / 1000000.0)

    def get_authorization_url(self, redirect_uri, state=None):
        """Returns the URL the user should be redirected to to sign in."""
        return self._url(
            "oauth/login", redirect_uri=redirect_uri, state=state,
            response_type="code", client_id=self.client_id)

    def get_access_token(self, redirect_uri, code,
                         grant_type="authorization_code",
                         refresh_token=None):
        """Exchanges a verification code for an access_token.

        Once the user is redirected back to your server from the URL
        returned by `get_authorization_url`, you can exchange the `code`
        argument with this method.
        """
        return self._fetch_json(
            "oauth/access_token", redirect_uri=redirect_uri, code=code,
            grant_type=grant_type, refresh_token=refresh_token,
            client_id=self.client_id, client_secret=self.client_secret)

    def get_authenticated_user(self, cache=True, cache_ttl=ONE_HOUR):
        """Returns the user corresponding to our access token."""
        return self._fetch_json("users/current", cache=cache, cache_ttl=cache_ttl)
