import logging

from . import bsky_api_client, types

logger = logging.getLogger(__name__)


def get_profile_data(handle: str) -> types.ProfileResult:
    """
    Fetches profile and recent posts for a given BlueSky handle using the public API.
    """
    logger.info(f"Fetching data for: {handle} ...")

    bsky_client = bsky_api_client.get_bsky_api_client()

    profile_info = bsky_client.get_profile(handle=handle)

    try:
        posts = bsky_client.get_posts(handle=handle)
    except bsky_api_client.UnableToGetFeeds:
        logger.warning(f"Unable to get feeds for {handle}, continuing with empty posts.")
        posts = []

    result = types.ProfileResult(
        profile=profile_info,
        posts=posts,
    )

    logger.info(f"Successfully fetched data for {handle}")
    return result


def search_actors(term: str, limit: int = 5) -> list[types.ActorBasic]:
    """
    Searches for actors matching the term using searchActorsTypeahead.
    """
    if not term or len(term.strip()) < 1:
        return []

    bsky_client = bsky_api_client.get_bsky_api_client()
    try:
        return bsky_client.search_actors(term, limit)
    except bsky_api_client.UnableToSearchActors as e:
        logger.error(f"Search actors failed: {e}")
        return []
