import requests

from . import bsky_api_client, types


def get_profile_data(handle: str) -> types.ProfileResult:
    """
    Fetches profile and recent posts for a given BlueSky handle using the public API.
    """
    # How to setup logging?
    # Why logging this data?
    print(f"Fetching data for: {handle} ...")

    bsky_client = bsky_api_client.get_bsky_api_client()

    # Implement safe extraction
    profile_info = bsky_client.get_profile(handle=handle)

    try:
        posts = bsky_client.get_posts(handle=handle)
    except bsky_api_client.UnableToGetFeeds:
        # Not critical, can continue with just profile description
        posts = []

    result = types.ProfileResult(
        profile=profile_info,
        posts=posts,
    )

    print(f"Successfully fetched data for {handle}")
    return result


def search_actors(term, limit=5):
    """
    Searches for actors matching the term using searchActorsTypeahead.
    """
    if not term or len(term.strip()) < 1:
        return []

    bsky_client = bsky_api_client.get_bsky_api_client()
    url = f"{bsky_client.api_base}/app.bsky.actor.searchActorsTypeahead"
    try:
        res = requests.get(url, params={"q": term, "limit": limit})
        res.raise_for_status()
        data = res.json()
        return data.get("actors", [])
    except Exception as e:
        print(f"Error searching actors for {term}: {e}")
        return []


# Functional (end-to-end) test cases?
if __name__ == "__main__":
    # Test
    data = get_profile_data("scievents.bsky.social")
    if data:
        print("Test Success:")
        print(data["profile"])
        print(f"Fetched {len(data['posts'])} posts.")
