import json
import logging

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .services import bsky_crawler, profile_analyzer

logger = logging.getLogger(__name__)


def search_actors(request: HttpRequest) -> JsonResponse:
    """GET /api/search?q=xxx"""
    q = request.GET.get("q", "")
    if not q:
        return JsonResponse([], safe=False)
    logger.info(f"Searching actors for query: {q}")
    results = bsky_crawler.search_actors(q)
    return JsonResponse(results, safe=False)


@csrf_exempt
def analyze_profile(request: HttpRequest) -> JsonResponse:
    """POST /api/analyze"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        logger.warning("Invalid JSON in request body")
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    handle = data.get("handle")
    lang = data.get("lang", "cn")

    if not handle:
        logger.warning("Analyze request received with no handle")
        return JsonResponse({"error": "No handle provided"}, status=400)

    handle = handle.strip().lower()
    logger.info(f"Analyzing profile for: {handle}")

    try:
        crawler_result = bsky_crawler.get_profile_data(handle)
    except Exception as e:
        logger.error(f"Failed to crawl profile for {handle}: {e}")
        return JsonResponse({"error": "Failed to fetch profile data"}, status=502)

    if not crawler_result:
        logger.warning(f"Profile not found: {handle}")
        return JsonResponse({"error": "Failed to fetch profile or profile not found"}, status=404)

    text_content = crawler_result.full_text_for_analysis
    try:
        analysis_result = profile_analyzer.analyze_personality(text_content, lang=lang)
    except Exception as e:
        logger.error(f"AI analysis failed for {handle}: {e}")
        return JsonResponse({"error": "AI analysis failed"}, status=500)

    response_data = {
        "profile": crawler_result.profile.model_dump(),
        "analysis": analysis_result,
    }

    logger.info(f"Analysis completed for: {handle}")
    return JsonResponse(response_data)
