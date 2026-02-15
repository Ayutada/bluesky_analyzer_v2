import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import bsky_crawler, profile_analyzer


def search_actors(request):
    """GET /api/search?q=xxx"""
    q = request.GET.get("q", "")
    if not q:
        return JsonResponse([], safe=False)
    results = bsky_crawler.search_actors(q)
    return JsonResponse(results, safe=False)


@csrf_exempt
def analyze_profile(request):
    """POST /api/analyze"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data = json.loads(request.body)
    handle = data.get("handle")
    lang = data.get("lang", "cn")

    if not handle:
        return JsonResponse({"error": "No handle provided"}, status=400)

    # Normalize handle: trim spaces and convert to lowercase
    handle = handle.strip().lower()

    # 1. Crawl data
    print(f"Received request for: {handle}")
    crawler_result = bsky_crawler.get_profile_data(handle)

    if not crawler_result:
        return JsonResponse({"error": "Failed to fetch profile or profile not found"}, status=404)

    # 2. AI analysis
    text_content = crawler_result["full_text_for_analysis"]
    analysis_result = profile_analyzer.analyze_personality(text_content, lang=lang)

    # 3. Construct response
    response_data = {
        "profile": crawler_result["profile"],
        "analysis": analysis_result,
    }

    return JsonResponse(response_data)