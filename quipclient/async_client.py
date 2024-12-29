"""Async implementation of Quip client."""

import asyncio
import aiohttp
import logging
from typing import Optional, Dict, Any, List
from .base import BaseQuipClient, QuipError
from .models import ThreadMetadata, FolderMetadata, FolderNode

logger = logging.getLogger(__name__)

class UserQuipClientAsync:
    """Async client for interacting with Quip API with user-focused abstractions"""
    
    def __init__(
        self,
        access_token: str,
        *,
        base_url: str = "https://platform.quip.com",
        request_timeout: int = 30,
        max_concurrent_requests: int = 10,
        cache_dir: Optional[str] = None
    ):
        """Initialize async client
        
        Args:
            access_token: Quip API access token
            base_url: Base URL for API requests
            request_timeout: Default timeout for requests in seconds
            max_concurrent_requests: Maximum concurrent API requests
            cache_dir: Directory for caching responses
        """
        self.access_token = access_token
        self.base_url = base_url
        self.request_timeout = request_timeout
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)
        self._session: Optional[aiohttp.ClientSession] = None
        self._cache_dir = cache_dir
        self._user_id: Optional[str] = None
        
        # Rate limit tracking
        self._rate_limit = None
        self._rate_limit_remaining = None
        self._rate_limit_reset = None
        self._company_rate_limit = None
        self._company_rate_limit_remaining = None
        self._company_rate_limit_reset = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
        
    async def start(self):
        """Start the client session"""
        if not self._session:
            self._session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            # Get user ID for cache keys
            user = await self._fetch_json("users/current")
            self._user_id = user["id"]
            
    async def close(self):
        """Close the client session"""
        if self._session:
            await self._session.close()
            self._session = None
            
    async def _fetch_json(
        self,
        path: str,
        *,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        cache: bool = True,
        cache_ttl: Optional[int] = None
    ) -> Dict[str, Any]:
        """Fetch JSON from API with rate limiting and caching
        
        Args:
            path: API endpoint path
            method: HTTP method
            params: Query parameters
            json_data: JSON body for POST/PUT
            cache: Whether to use caching
            cache_ttl: Cache TTL in seconds
            
        Returns:
            API response data
            
        Raises:
            QuipError: If API request fails
        """
        if not self._session:
            await self.start()
            
        # Construct full URL
        if path.startswith("2/"):
            url = f"{self.base_url}/2/{path[2:]}"
        else:
            url = f"{self.base_url}/1/{path}"
            
        async with self._semaphore:
            try:
                async with self._session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    timeout=self.request_timeout
                ) as response:
                    # Update rate limit tracking
                    self._update_rate_limits(response)
                    
                    if response.status >= 400:
                        error_data = await response.json()
                        raise QuipError(
                            response.status,
                            error_data.get("error_description", "Unknown error"),
                            None
                        )
                        
                    return await response.json()
                    
            except asyncio.TimeoutError as e:
                raise QuipError(408, "Request timeout", e)
            except Exception as e:
                if isinstance(e, QuipError):
                    raise
                raise QuipError(500, str(e), e)
                
    def _update_rate_limits(self, response: aiohttp.ClientResponse):
        """Update rate limit tracking from response headers"""
        self._rate_limit = int(response.headers.get("X-RateLimit-Limit", 0))
        self._rate_limit_remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
        self._rate_limit_reset = float(response.headers.get("X-RateLimit-Reset", 0))
        
        self._company_rate_limit = int(response.headers.get("X-Company-RateLimit-Limit", 0))
        self._company_rate_limit_remaining = int(response.headers.get("X-Company-RateLimit-Remaining", 0))
        self._company_rate_limit_reset = float(response.headers.get("X-Company-RateLimit-Reset", 0))
