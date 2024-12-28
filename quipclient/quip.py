# Copyright 2014 Quip
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""A Quip API client library.

For full API documentation, visit https://quip.com/api/.

Typical usage:

    client = quip.QuipClient(access_token=...)
    user = client.get_authenticated_user()
    starred = client.get_folder(user["starred_folder_id"])
    print "There are", len(starred["children"]), "items in your starred folder"

In addition to standard getters and setters, we provide a few convenience
methods for document editing. For example, you can use `add_to_first_list`
to append items (in Markdown) to the first bulleted or checklist in a
given document, which is useful for automating a task list.
"""

import datetime
import json
import logging
import os
import ssl
import sys
import time
import xml.etree.cElementTree
from diskcache import Cache
import zlib

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


# Python 3 uses UTF-8 by default
pass

try:
    ssl.PROTOCOL_TLSv1_1
except AttributeError:
    raise Exception(
        "Using the Quip API requires an SSL library that supports TLS versions "
        ">= 1.1; your Python + OpenSSL installation must be upgraded.")
# After 2017-02, the Quip API HTTPS endpoint requires TLS version 1.1 or later;
# TLS version 1.0 is disabled due to extensive security vulnerabilities.
#
# - macOS: At this time of this writing, macOS ships with Python 2.7 and
#   OpenSSL, but the version of OpenSSL is outdated and only supports TLS 1.0.
#   (This is even true of the most recent version of macOS (Sierra) with all
#   security patches installed; see
#   https://eclecticlight.co/2016/03/23/the-tls-mess-in-os-x-el-capitan/ .)
#
#   To use this module on a macOS system, you will need to install your own
#   copy of Python and OpenSSL. Simple suggestions:
#
#   1) Install Homebrew from http://brew.sh; run "brew install openssl python"
#   2) Install Miniconda from https://conda.io/miniconda.html
#
# - Google App Engine (GAE): Per App Engine's documentation, you must request
#   version 2.7.11 of the "ssl" library in your app.yaml file. See:
#   https://cloud.google.com/appengine/docs/python/sockets/ssl_support


class QuipError(Exception):
    def __init__(self, code, message, http_error):
        Exception.__init__(self, "%d: %s" % (code, message))
        self.code = code
        self.http_error = http_error


class QuipClient(object):
    """A Quip API client"""
    # Cache TTL constants (in seconds)
    ONE_HOUR = 3600
    ONE_DAY = 86400
    THIRTY_DAYS = 2592000

    # Maximum entities per API request
    MAX_USERS_PER_REQUEST = 100
    MAX_FOLDERS_PER_REQUEST = 100  
    MAX_THREADS_PER_REQUEST = 10

    # Edit operations
    APPEND, \
        PREPEND, \
        AFTER_SECTION, \
        BEFORE_SECTION, \
        REPLACE_SECTION, \
        DELETE_SECTION = range(6)

    # Folder colors
    MANILA, \
        RED, \
        ORANGE, \
        GREEN, \
        BLUE = range(5)

    def __init__(self, access_token=None, client_id=None, client_secret=None,
                 base_url=None, request_timeout=None, cache_dir=None):
        """Constructs a Quip API client.
        If `access_token` is given, all of the API methods in the client
        will work to read and modify Quip documents.

        Otherwise, only `get_authorization_url` and `get_access_token`
        work, and we assume the client is for a server using the Quip API's
        OAuth endpoint.
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
        if self.access_token:
            try:
                self._user_id = self.get_authenticated_user()["id"]
            except:
                pass

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

    def get_user(self, id, cache=True, cache_ttl=ONE_HOUR):
        """Returns the user with the given ID."""
        return self._fetch_json("users/" + id, cache=cache, cache_ttl=cache_ttl)

    def get_users(self, ids, cache=True, cache_ttl=THIRTY_DAYS):
        """Returns a dictionary of users for the given IDs.
        
        Uses caching to optimize repeated requests for the same users.
        """
        return self._cached_get("users", ids, None if not cache else cache_ttl, 
                              batch_size=self.MAX_USERS_PER_REQUEST, cache=cache)

    def update_user(self, user_id, picture_url=None):
        return self._fetch_json("users/update", post_data={
            "user_id": user_id,
            "picture_url": picture_url,
        })

    def get_contacts(self):
        """Returns a list of the users in the authenticated user's contacts."""
        return self._fetch_json("users/contacts")

    def get_folder(self, id, cache=True, cache_ttl=THIRTY_DAYS):
        """Returns the folder with the given ID."""
        return self._fetch_json("folders/" + id, cache=cache, cache_ttl=cache_ttl)

    def get_folders(self, ids, cache=True, cache_ttl=THIRTY_DAYS):
        """Returns a dictionary of folders for the given IDs.
        
        Uses caching to optimize repeated requests for the same folders.
        """
        return self._cached_get("folders", ids, None if not cache else cache_ttl,
                              batch_size=self.MAX_FOLDERS_PER_REQUEST, cache=cache)

    def new_folder(self, title, parent_id=None, color=None, member_ids=[]):
        return self._fetch_json("folders/new", post_data={
            "title": title,
            "parent_id": parent_id,
            "color": color,
            "member_ids": ",".join(member_ids),
        })

    def update_folder(self, folder_id, color=None, title=None):
        return self._fetch_json("folders/update", post_data={
            "folder_id": folder_id,
            "color": color,
            "title": title,
        })

    def add_folder_members(self, folder_id, member_ids):
        """Adds the given users to the given folder."""
        return self._fetch_json("folders/add-members", post_data={
            "folder_id": folder_id,
            "member_ids": ",".join(member_ids),
        })

    def remove_folder_members(self, folder_id, member_ids):
        """Removes the given users from the given folder."""
        return self._fetch_json("folders/remove-members", post_data={
            "folder_id": folder_id,
            "member_ids": ",".join(member_ids),
        })

    def get_teams(self):
        """Returns the teams for the user corresponding to our access token."""
        return self._fetch_json("teams/current")

    def get_messages(self, thread_id, max_created_usec=None, count=None):
        """Returns the most recent messages for the given thread.

        To page through the messages, use max_created_usec, which is the
        sort order for the returned messages.

        count should be an integer indicating the number of messages you
        want returned. The maximum is 100.
        """
        return self._fetch_json(
            "messages/" + thread_id, max_created_usec=max_created_usec,
            count=count, cache=False)

    def new_message(self, thread_id, content=None, **kwargs):
        """Sends a message on the given thread.

        `content` is plain text, not HTML.
        """
        args = {
            "thread_id": thread_id,
            "content": content,
        }
        args.update(kwargs)
        return self._fetch_json("messages/new", post_data=args, cache=False)

    def get_thread(self, id, cache=True, cache_ttl=THIRTY_DAYS):
        """Returns the thread with the given ID using v1 API."""
        return self._fetch_json("threads/" + id, cache=cache, cache_ttl=cache_ttl)

    def get_thread_v2(self, thread_id_or_path, cache=True, cache_ttl=None):
        """Returns thread information using v2 API.
        
        Args:
            thread_id_or_path: Thread ID or secret path from thread URL
            cache: Whether to cache the response
            cache_ttl: Cache TTL in seconds
        """
        return self._fetch_json(f"2/threads/{thread_id_or_path}", 
                              cache=cache, cache_ttl=cache_ttl)

    def get_threads_v2(self, ids, cache=True, cache_ttl=None):
        """Returns information about multiple threads using v2 API.
        
        Args:
            ids: List of thread IDs or secret paths
            cache: Whether to cache the response
            cache_ttl: Cache TTL in seconds
        """
        return self._cached_get("2/threads", ids, None if not cache else cache_ttl,
                              batch_size=self.MAX_THREADS_PER_REQUEST, cache=cache)

    def get_thread_folders_v2(self, thread_id_or_path, timeout=30, cursor=None):
        """Returns complete list of folders containing the thread using v2 API.
        
        Args:
            thread_id_or_path: Thread ID or secret path
            timeout: Request timeout in seconds (default 30)
            
        Returns:
            Combined results from all pages of folder data.
            
        Raises:
            QuipError: If the API request fails
            TimeoutError: If the request times out
        """
        try:
            return self._fetch_json(
                f"2/threads/{thread_id_or_path}/folders",
                paginate=True, 
                cache=False,
                timeout=timeout
            )
        except Exception as e:
            if isinstance(e, QuipError):
                raise
            raise TimeoutError(f"Request timed out after {timeout} seconds") from e

    def get_thread_html_v2(self, thread_id_or_path, cache=True, cache_ttl=None):
        """Returns complete thread HTML content using v2 API.
        
        Args:
            thread_id_or_path: Thread ID or secret path
            cache: Whether to cache the response (default False)
            cache_ttl: Cache TTL in seconds (default 1 hour)
            
        Returns:
            Combined results from all pages of HTML content.
        """
        # Try to get complete result from cache first
        if cache:
            url = self._url(f"2/threads/{thread_id_or_path}/html")
            cache_key = f"{self._user_id or '_'}:{url}"
            cached_data = self._cache.get(cache_key)
            if cached_data:
                return json.loads(zlib.decompress(cached_data).decode())
        
        # If not cached or cache disabled, fetch all pages
        result = {"html": "", "response_metadata": {"next_cursor": ""}}
        cursor = None
        
        while True:
            page = self._fetch_json(f"2/threads/{thread_id_or_path}/html",
                                  cursor=cursor, cache=False)
            
            if "html" in page:
                result["html"] += page["html"]
            
            cursor = page.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        
        # Cache the complete result if caching is enabled
        if cache:
            url = self._url(f"2/threads/{thread_id_or_path}/html")
            cache_key = f"{self._user_id or '_'}:{url}"
            self._cache.set(
                cache_key,
                zlib.compress(json.dumps(result).encode()),
                cache_ttl
            )
                
        return result

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

    def get_threads(self, ids, cache=True, cache_ttl=THIRTY_DAYS):
        """Returns a dictionary of threads for the given IDs.
        
        Uses caching to optimize repeated requests for the same threads.
        """
        return self._cached_get("threads", ids, None if not cache else cache_ttl,
                              batch_size=self.MAX_THREADS_PER_REQUEST, cache=cache)

    def get_recent_threads(self, max_updated_usec=None, count=None, **kwargs):
        """Returns the recently updated threads for a given user."""
        return self._fetch_json(
            "threads/recent", max_updated_usec=max_updated_usec,
            count=count, cache=False, **kwargs)

    def get_matching_threads(
            self, query, count=None, only_match_titles=False, **kwargs):
        """Returns the recently updated threads for a given user."""
        return self._fetch_json("threads/search", query=query, count=count,
            only_match_titles=only_match_titles, **kwargs)

    def add_thread_members(self, thread_id, member_ids):
        """Adds the given folder or user IDs to the given thread."""
        return self._fetch_json("threads/add-members", post_data={
            "thread_id": thread_id,
            "member_ids": ",".join(member_ids),
        }, cache=False)

    def delete_thread(self, thread_id):
        """Deletes the thread with the given thread id or secret"""
        return self._fetch_json("threads/delete", post_data={
            "thread_id": thread_id,
        })

    def remove_thread_members(self, thread_id, member_ids):
        """Removes the given folder or user IDs from the given thread."""
        return self._fetch_json("threads/remove-members", post_data={
            "thread_id": thread_id,
            "member_ids": ",".join(member_ids),
        }, cache=False)

    def move_thread(self, thread_id, source_folder_id, destination_folder_id):
        """Moves the given thread from the source folder to the destination one.
        """
        self.add_thread_members(thread_id, [destination_folder_id])
        self.remove_thread_members(thread_id, [source_folder_id])

    def new_chat(self, message, title=None, member_ids=[]):
        """Creates a chat with the given title and members, and send the
        initial message."""
        return self._fetch_json("threads/new-chat", post_data={
            "message": message,
            "title": title,
            "member_ids": ",".join(member_ids),
        }, cache=False)

    def new_document(self, content, format="html", title=None, member_ids=[]):
        """Creates a new document from the given content.

        To create a document in a folder, include the folder ID in the list
        of member_ids, e.g.,

            client = quip.QuipClient(...)
            user = client.get_authenticated_user()
            client.new_document(..., member_ids=[user["archive_folder_id"]])

        """
        return self._fetch_json("threads/new-document", post_data={
            "content": content,
            "format": format,
            "title": title,
            "member_ids": ",".join(member_ids),
        }, cache=False)

    def copy_document(self, thread_id, folder_ids=None, member_ids=None,
            title=None, values=None, **kwargs):
        """Copies the given document, optionally replaces template variables
           in the document with values in 'values' arg. The values argument
           must be a dictionary that contains string keys and values that
           are either strings, numbers or dictionaries.
        """

        args = {"thread_id": thread_id}
        if folder_ids:
            args["folder_ids"] = ",".join(folder_ids)
        if member_ids:
            args["member_ids"] = ",".join(member_ids)
        if title:
            args["title"] = title
        if values:
            args["values"] = json.dumps(values)
        args.update(kwargs)
        return self._fetch_json("threads/copy-document", post_data=args, cache=False)

    def merge_comments(self, original_id, children_ids, ignore_user_ids=[]):
        """Given an original document and a set of exact duplicates, copies
        all comments and messages on the duplicates to the original.

        Impersonates the commentors if the access token used has
        permission, but does not add them to the thread.
        """
        import re
        threads = self.get_threads(children_ids + [original_id])
        original_section_ids = re.findall(r" id='([a-zA-Z0-9]{11})'",
                                          threads[original_id]["html"])
        for thread_id in children_ids:
            thread = threads[thread_id]
            child_section_ids = re.findall(r" id='([a-zA-Z0-9]{11})'",
                                           thread["html"])
            parent_map = dict(zip(child_section_ids, original_section_ids))
            messages = self.get_messages(thread_id)
            for message in reversed(messages):
                if message["author_id"] in ignore_user_ids:
                    continue
                kwargs = {
                    "user_id": message["author_id"],
                    "frame": "bubble",
                    "service_id": message["id"],
                }
                if "parts" in message:
                    kwargs["parts"] = json.dumps(message["parts"])
                else:
                    kwargs["content"] = message["text"]
                if "annotation" in message:
                    section_id = None
                    if "highlight_section_ids" in message["annotation"]:
                        section_id = message["annotation"][
                            "highlight_section_ids"][0]
                    else:
                        anno_loc = thread["html"].find(
                            '<annotation id="%s"' % message["annotation"]["id"])
                        loc = thread["html"].rfind("id=", 0, anno_loc)
                        if anno_loc >= 0 and loc >= 0:
                            section_id = thread["html"][loc + 4:loc + 15]
                    if section_id and section_id in parent_map:
                        kwargs["section_id"] = parent_map[section_id]
                if "files" in message:
                    attachments = []
                    for blob_info in message["files"]:
                        blob = self.get_blob(thread_id, blob_info["hash"])
                        new_blob = self.put_blob(
                            original_id, blob, name=blob_info["name"])
                        attachments.append(new_blob["id"])
                    if attachments:
                        kwargs["attachments"] = ",".join(attachments)
                self.new_message(original_id, **kwargs)

    def edit_document(self, thread_id, content, operation=APPEND, format="html",
                      section_id=None, **kwargs):
        """Edits the given document, adding the given content.

        `operation` should be one of the constants described above. If
        `operation` is relative to another section of the document, you must
        also specify the `section_id`.
        """

        # Since our cell ids in 10x contain ';', which is a valid cgi
        # parameter separator, we are replacing them with '_' in 10x cell
        # sections. This should be no op for all other sections.
        section_id = None if not section_id else section_id.replace(";", "_")

        args = {
            "thread_id": thread_id,
            "content": content,
            "location": operation,
            "format": format,
            "section_id": section_id
        }
        args.update(kwargs)
        return self._fetch_json("threads/edit-document", post_data=args, cache=False)

    def add_to_first_list(self, thread_id, *items, **kwargs):
        """Adds the given items to the first list in the given document.

            client = quip.QuipClient(...)
            client.add_to_first_list(thread_id, "Try the Quip API")

        """
        items = [item.replace("\n", " ") for item in items]
        args = {
            "thread_id": thread_id,
            "content": "\n\n".join(items),
            "format": "markdown",
            "operation": self.AFTER_SECTION
        }
        args.update(kwargs)
        if "section_id" not in args:
            first_list = self.get_first_list(
                thread_id, kwargs.pop("document_html", None))
            if first_list:
                args["section_id"] = self.get_last_list_item_id(first_list)
        if not args.get("section_id"):
            args["operation"] = self.APPEND
            args["content"] = "\n\n".join(["    * %s" % i for i in items])
        return self.edit_document(**args)

    def add_to_spreadsheet(self, thread_id, *rows, **kwargs):
        """Adds the given rows to the named (or first) spreadsheet in the
        given document.

            client = quip.QuipClient(...)
            client.add_to_spreadsheet(thread_id, ["5/1/2014", 2.24])

        """
        content = "".join(["<tr>%s</tr>" % "".join(
            ["<td>%s</td>" % cell for cell in row]) for row in rows])
        if kwargs.get("name"):
            spreadsheet = self.get_named_spreadsheet(kwargs["name"], thread_id)
        else:
            spreadsheet = self.get_first_spreadsheet(thread_id)
        if kwargs.get("add_to_top"):
            section_id = self.get_first_row_item_id(spreadsheet)
            operation = self.BEFORE_SECTION
        else:
            section_id = self.get_last_row_item_id(spreadsheet)
            operation = self.AFTER_SECTION
        return self.edit_document(
            thread_id=thread_id,
            content=content,
            section_id=section_id,
            operation=operation)

    def update_spreadsheet_row(self, thread_id, header, value, updates, **args):
        """Finds the row where the given header column is the given value, and
        applies the given updates. Updates is a dict from header to
        new value. In both cases headers can either be a string that matches, or
        "A", "B", "C", 1, 2, 3 etc. If no row is found, adds a new one.

            client = quip.QuipClient(...)
            client.update_spreadsheet_row(
                thread_id, "customer", "Acme", {"Billed": "6/24/2015"})

        """
        response = None
        if args.get("name"):
            spreadsheet = self.get_named_spreadsheet(args["name"], thread_id)
        else:
            spreadsheet = self.get_first_spreadsheet(thread_id)
        headers = self.get_spreadsheet_header_items(spreadsheet)
        row = self.find_row_from_header(spreadsheet, header, value)
        if row:
            ids = self.get_row_ids(row)
            for head, val in iteritems(updates):
                index = self.get_index_of_header(headers, head)
                if not index or index >= len(ids) or not ids[index]:
                    continue
                response = self.edit_document(
                    thread_id=thread_id,
                    content=val,
                    format="markdown",
                    section_id=ids[index],
                    operation=self.REPLACE_SECTION,
                    **args)
        else:
            updates[header] = value
            response = self.add_spreadsheet_row(
                thread_id, spreadsheet, updates, headers=headers, **args)
        return response

    def add_spreadsheet_row(
            self, thread_id, spreadsheet, updates, headers=None, **args):
        if not headers:
            headers = self.get_spreadsheet_header_items(spreadsheet)
        indexed_items = {}
        extra_items = []
        for head, val in iteritems(updates):
            index = self.get_index_of_header(
                headers, head, default=None)
            if index is None or index in indexed_items:
                extra_items.append(val)
            else:
                indexed_items[index] = val
        cells = []
        if indexed_items:
            for i in range(max(indexed_items.keys()) + 1):
                if i in indexed_items:
                    cells.append(indexed_items[i])
                elif len(extra_items):
                    cells.append(extra_items.pop(0))
                else:
                    cells.append("")
        cells.extend(extra_items)
        content = "<tr>%s</tr>" % "".join(
            ["<td>%s</td>" % cell for cell in cells])
        section_id = self.get_last_row_item_id(spreadsheet)
        response = self.edit_document(
            thread_id=thread_id,
            content=content,
            section_id=section_id,
            operation=self.AFTER_SECTION,
            **args)
        return response

    def toggle_checkmark(self, thread_id, item, checked=True):
        """Sets the checked state of the given list item to the given state.

            client = quip.QuipClient(...)
            list = client.get_first_list(thread_id)
            client.toggle_checkmark(thread_id, list[0])

        """
        if checked:
            item.attrib["class"] = "checked"
        else:
            item.attrib["class"] = ""
        return self.edit_document(thread_id=thread_id,
                                  content=xml.etree.cElementTree.tostring(item),
                                  section_id=item.attrib["id"],
                                  operation=self.REPLACE_SECTION)

    def get_first_list(self, thread_id=None, document_html=None):
        """Returns the `ElementTree` of the first list in the document.

        The list can be any type (bulleted, numbered, or checklist).
        If `thread_id` is given, we download the document. If you have
        already downloaded the document, you can specify `document_html`
        directly.
        """
        return self._get_container(thread_id, document_html, "ul", 0)

    def get_last_list(self, thread_id=None, document_html=None):
        """Like `get_first_list`, but the last list in the document."""
        return self._get_container(thread_id, document_html, "ul", -1)

    def get_section(self, section_id, thread_id=None, document_html=None):
        if not document_html:
            document_html = self.get_thread(thread_id).get("html")
            if not document_html:
                return None
        tree = self.parse_document_html(document_html)
        element = list(tree.iterfind(".//*[@id='%s']" % section_id))
        if not element:
            return None
        return element[0]

    def get_named_spreadsheet(self, name, thread_id=None, document_html=None):
        if not document_html:
            document_html = self.get_thread(thread_id).get("html")
            if not document_html:
                return None
        tree = self.parse_document_html(document_html)
        element = list(tree.iterfind(".//*[@title='%s']" % name))
        if not element:
            return None
        return element[0]

    def _get_container(self, thread_id, document_html, container, index):
        if not document_html:
            document_html = self.get_thread(thread_id).get("html")
            if not document_html:
                return None
        tree = self.parse_document_html(document_html)
        lists = list(tree.iter(container))
        if not lists:
            return None
        try:
            return lists[index]
        except IndexError:
            return None

    def get_last_list_item_id(self, list_tree):
        """Returns the last item in the given list `ElementTree`."""
        items = list(list_tree.iter("li"))
        return items[-1].attrib["id"] if items else None

    def get_first_list_item_id(self, list_tree):
        """Like `get_last_list_item_id`, but the first item in the list."""
        for item in list_tree.iter("li"):
            return item.attrib["id"]
        return None

    def get_first_spreadsheet(self, thread_id=None, document_html=None):
        """Returns the `ElementTree` of the first spreadsheet in the document.

        If `thread_id` is given, we download the document. If you have
        already downloaded the document, you can specify `document_html`
        directly.
        """
        return self._get_container(thread_id, document_html, "table", 0)

    def get_last_spreadsheet(self, thread_id=None, document_html=None):
        """Like `get_first_spreadsheet`, but the last spreadsheet."""
        return self._get_container(thread_id, document_html, "table", -1)

    def get_last_row_item_id(self, spreadsheet_tree):
        """Returns the last row in the given spreadsheet `ElementTree`."""
        items = list(spreadsheet_tree.iter("tr"))
        return items[-1].attrib["id"] if items else None

    def get_first_row_item_id(self, spreadsheet_tree):
        """Returns the last row in the given spreadsheet `ElementTree`."""
        items = list(spreadsheet_tree.iter("tr"))
        return items[1].attrib["id"] if items else None

    def get_row_items(self, row_tree):
        """Returns the text of items in the given row `ElementTree`."""
        return [(list(x.itertext()) or [None])[0] for x in row_tree]

    def get_row_ids(self, row_tree):
        """Returns the ids of items in the given row `ElementTree`."""
        return [x.attrib["id"] for x in row_tree]

    def get_spreadsheet_header_items(self, spreadsheet_tree):
        """Returns the header row in the given spreadsheet `ElementTree`."""
        return self.get_row_items(list(spreadsheet_tree.iterfind(".//tr"))[0])

    def get_index_of_header(self, header_items, header, default=0):
        """Find the index of the given header in the items"""
        if header:
            header = str(header)
            lower_headers = [str(h).lower() for h in header_items]
            if header in header_items:
                return header_items.index(header)
            elif header.lower() in lower_headers:
                return lower_headers.index(header.lower())
            elif header.isdigit():
                return int(header)
            elif len(header) == 1:
                char = ord(header.upper())
                if ord('A') < char < ord('Z'):
                    return char - ord('A') + 1
            else:
                pass
        return default

    def find_row_from_header(self, spreadsheet_tree, header, value):
        """Find the row in the given spreadsheet `ElementTree` where header is
        value.
        """
        headers = self.get_spreadsheet_header_items(spreadsheet_tree)
        index = self.get_index_of_header(headers, header)
        for row in spreadsheet_tree.iterfind(".//tr"):
            if len(row) <= index:
                continue
            cell = row[index]
            if cell.tag != "td":
                continue
            if list(cell.itertext())[0].lower() == value.lower():
                return row

    def parse_spreadsheet_contents(self, spreadsheet_tree):
        """Returns a python-friendly representation of the given spreadsheet
        `ElementTree`
        """
        import collections
        spreadsheet = {
            "id": spreadsheet_tree.attrib.get("id"),
            "headers": self.get_spreadsheet_header_items(spreadsheet_tree),
            "rows": [],
        }
        for row in spreadsheet_tree.iterfind(".//tr"):
            value = {
                "id": row.attrib.get("id"),
                "cells": collections.OrderedDict(),
            }
            for i, cell in enumerate(row):
                if cell.tag != "td":
                    continue
                data = {
                    "id": cell.attrib.get("id"),
                }
                images = list(cell.iter("img"))
                if images:
                    data["content"] = images[0].attrib.get("src")
                else:
                    data["content"] = list(cell.itertext())[0].replace(
                        u"\u200b", "")
                style = cell.attrib.get("style")
                if style and "background-color:#" in style:
                    sharp = style.find("#")
                    data["color"] = style[sharp + 1:sharp + 7]
                value["cells"][spreadsheet["headers"][i]] = data
            if len(value["cells"]):
                spreadsheet["rows"].append(value)
        return spreadsheet

    def parse_document_html(self, document_html):
        """Returns an `ElementTree` for the given Quip document HTML"""
        document_xml = "<html>" + document_html + "</html>"
        return xml.etree.cElementTree.fromstring(document_xml.encode("utf-8"))

    def parse_micros(self, usec):
        """Returns a `datetime` for the given microsecond string"""
        return datetime.datetime.utcfromtimestamp(usec / 1000000.0)

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
            return urlopen(request, timeout=self.request_timeout)
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

    def new_websocket(self, **kwargs):
        """Gets a websocket URL to connect to.
        """
        return self._fetch_json("websockets/new", cache=False, **kwargs)

    def _fetch_json(self, path, post_data=None, cache=True, cache_ttl=None, paginate=False, **args):
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
            cache_key = f"{self._user_id or "_"}:{url}"
            cached_data, expiry_time = self._cache.get(cache_key, expire_time=True)
            if cached_data:  # Check if we have actual data
                data = json.loads(zlib.decompress(cached_data).decode())
                if isinstance(data, dict) and data.get("error"):
                    # Reconstruct the error from cache
                    raise QuipError(data["code"], data["message"], None)
                return data

        # TODO: add support for post data as part of cache_key
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
            self._rate_limit = int(response.headers.get('X-RateLimit-Limit', 0))
            self._rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            self._rate_limit_reset = float(response.headers.get('X-RateLimit-Reset', 0))
            
            self._company_rate_limit = int(response.headers.get('X-Company-RateLimit-Limit', 0))
            self._company_rate_limit_remaining = int(response.headers.get('X-Company-RateLimit-Remaining', 0))
            self._company_rate_limit_reset = float(response.headers.get('X-Company-RateLimit-Reset', 0))
            self._company_retry_after = int(response.headers.get('X-Company-Retry-After', 0))
            
            response_data = response.read().decode()
            result = json.loads(response_data)
            
            # Cache successful GET responses if caching is enabled
            if cache and not post_data and cache_ttl:
                cache_key = f"{self._user_id or '_'}:{url}"
                self._cache.set(cache_key, zlib.compress(response_data.encode()), cache_ttl)
            
            # Handle pagination if requested
            if paginate and not post_data:
                if "response_metadata" in result:
                    cursor = result["response_metadata"].get("next_cursor")
                    # Only paginate if cursor exists and is not empty
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
                # Extract the developer-friendly error message from the response
                error_data = error.read().decode()
                if error_data:
                    error_json = json.loads(error_data)
                    message = error_json["error_description"]
                else:
                    message = error.reason
                # Cache error responses if caching is enabled
                if cache and not post_data and cache_ttl:
                    cache_key = f"{self._user_id or '_'}:{url}"
                    error_cache = {
                        "error": True,
                        "code": error.code,
                        "message": message
                    }
                    self._cache.set(cache_key, zlib.compress(json.dumps(error_cache).encode()), cache_ttl)
            except Exception:
                raise error
            raise QuipError(error.code, message, error)

    def _clean(self, **args):
        return dict((k, str(v) if isinstance(v, int) else v.encode("utf-8"))
                    for k, v in args.items() if v or isinstance(v, int))

    def _url(self, path, cursor=None, **args):
        # Handle API version prefix
        if path.startswith("2/"):
            url = self.base_url + "/2/" + path[2:]  # Remove "2/" and re-add it with leading slash
        else:
            url = self.base_url + "/1/" + path
        
        # Handle cursor separately to ensure it's included in URL when present
        if cursor:
            args['cursor'] = cursor
            
        args = self._clean(**args)
        if args:
            url += "?" + urlencode(args)
        return url
