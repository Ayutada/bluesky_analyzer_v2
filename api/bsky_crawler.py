import requests

BSKY_API_BASE = "https://public.api.bsky.app/xrpc"

def get_profile_data(handle):
    """
    Fetches profile and recent posts for a given BlueSky handle using the public API.
    """
    print(f"Fetching data for: {handle} ...")
    
    # 1. Get Profile
    profile_url = f"{BSKY_API_BASE}/app.bsky.actor.getProfile"
    try:
        profile_res = requests.get(profile_url, params={"actor": handle})
        profile_res.raise_for_status()
        profile_json = profile_res.json()
    except Exception as e:
        print(f"Error fetching profile for {handle}: {e}")
        return None

    # Implement safe extraction
    profile_info = {
        "handle": profile_json.get("handle"),
        "displayName": profile_json.get("displayName"),
        "description": profile_json.get("description", ""),
        "avatar": profile_json.get("avatar"),
    }

    # 2. Get Recent Posts (Author Feed)
    feed_url = f"{BSKY_API_BASE}/app.bsky.feed.getAuthorFeed"
    posts_text = []
    
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
                posts_text.append(text)
                
    except Exception as e:
        print(f"Error fetching feed for {handle}: {e}")
        # Not critical, can continue with just profile description

    result = {
        "profile": profile_info,
        "posts": posts_text,
        "full_text_for_analysis": f"User Description:\n{profile_info['description']}\n\nRecent Posts:\n" + "\n".join(posts_text)
    }
    
    print(f"Successfully fetched data for {handle}")
    return result

def search_actors(term, limit=5):
    """
    Searches for actors matching the term using searchActorsTypeahead.
    """
    if not term or len(term.strip()) < 1:
        return []
        
    url = f"{BSKY_API_BASE}/app.bsky.actor.searchActorsTypeahead"
    try:
        res = requests.get(url, params={"q": term, "limit": limit})
        res.raise_for_status()
        data = res.json()
        return data.get("actors", [])
    except Exception as e:
        print(f"Error searching actors for {term}: {e}")
        return []

if __name__ == "__main__":
    # Test
    data = get_profile_data("scievents.bsky.social")
    if data:
        print("Test Success:")
        print(data["profile"])
        print(f"Fetched {len(data['posts'])} posts.")
