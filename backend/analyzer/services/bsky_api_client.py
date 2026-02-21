import logging

import requests

from . import types


class UnableToGetProfile(Exception):
    pass


class UnableToGetFeeds(Exception):
    pass


class BskyClient:
    def __init__(self) -> None:
        self.api_base = "https://public.api.bsky.app/xrpc"

    def get_profile(self, handle: str) -> types.ProfileInfo:
        profile_url = f"{self.api_base}/app.bsky.actor.getProfile"
        try:
            profile_res = requests.get(profile_url, params={"actor": handle})
            profile_res.raise_for_status()
            profile_json = profile_res.json()
        except requests.HTTPError as e:
            logging.error(f"Error fetching profile for {handle}: {e}")
            raise UnableToGetProfile

        profile_info = types.ProfileInfo(
            handle=profile_json.get("handle"),
            display_name=profile_json.get("displayName"),
            description=profile_json.get("description", ""),
            avatar=profile_json.get("avatar"),
        )

        return profile_info

    def get_posts(self, handle: str) -> list[types.PostFeed]:
        feed_url = f"{self.api_base}/app.bsky.feed.getAuthorFeed"
        posts = []

        try:
            feed_res = requests.get(feed_url, params={"actor": handle, "limit": 50})
            feed_res.raise_for_status()
            feed_json = feed_res.json()

            feed = feed_json.get("feed", [])
            for item in feed:
                post = item.get("post", {})
                record = post.get("record", {})
                text = record.get("text", "")
                if text:
                    posts.append(types.PostFeed(post=post, record=record, text=text))

        except requests.HTTPError as e:
            logging.error(f"Error fetching feeds for {handle}: {e}")
            raise UnableToGetFeeds

        return posts


def get_bsky_api_client() -> BskyClient:
    # TODO: Read API key from env variables when authentication is needed
    return BskyClient()
