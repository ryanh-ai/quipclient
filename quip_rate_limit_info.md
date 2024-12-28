## Per-user Rate Limits
The Automation API is rate limited by number of requests per minute per user - with defaults of:

- 50 requests per minute per user
- 750 requests per hour per user

API responses include a few custom headers to help developers implement backoffs in their code. These headers are:

- X-Ratelimit-Limit: The number of requests per minute/hour the user can make
- X-Ratelimit-Remaining: The number of requests remaining this user can make within the minute/hour. This number changes with each request
- X-Ratelimit-Reset: The UTC timestamp for when the rate limit resets

##Per-company Rate Limit
Quip's APIs are also subject to a per-company rate limit with a default of 600 requests per minute. The API responses include these custom headers to help developers implement backoffs in their code:

- X-Company-RateLimit-Limit: The number of requests per minute that your company can make
- X-Company-RateLimit-Remaining: The number of requests remaining for your company within the minute
- X-Company-RateLimit-Reset: The UTC timestamp for when the rate limit resets
- X-Company-Retry-After: The number of seconds after which your company can make API calls again