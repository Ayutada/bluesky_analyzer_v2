import json
from unittest.mock import MagicMock, patch

from analyzer.services import types
from django.test import Client, TestCase


class SearchActorsViewTests(TestCase):
    """Functional tests for the GET /api/search endpoint."""

    def setUp(self) -> None:
        self.client = Client()

    def test_empty_query_returns_empty_list(self) -> None:
        """Omitting the 'q' parameter should return an empty JSON list."""
        response = self.client.get("/api/search")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_blank_query_returns_empty_list(self) -> None:
        """Passing q='' should return an empty JSON list."""
        response = self.client.get("/api/search", {"q": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    @patch("analyzer.views.bsky_crawler.search_actors")
    def test_valid_query_returns_results(self, mock_search: MagicMock) -> None:
        """A valid query should return serialized ActorBasic objects."""
        mock_search.return_value = [
            types.ActorBasic(
                did="did:plc:abc123",
                handle="alice.bsky.social",
                display_name="Alice",
                avatar="https://example.com/avatar.jpg",
            ),
        ]

        response = self.client.get("/api/search", {"q": "alice"})
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["handle"], "alice.bsky.social")
        self.assertEqual(data[0]["did"], "did:plc:abc123")
        mock_search.assert_called_once_with("alice")

    @patch("analyzer.views.bsky_crawler.search_actors")
    def test_valid_query_returns_multiple_results(self, mock_search: MagicMock) -> None:
        """Multiple matching actors should all be returned."""
        mock_search.return_value = [
            types.ActorBasic(did="did:1", handle="user1.bsky.social"),
            types.ActorBasic(did="did:2", handle="user2.bsky.social"),
            types.ActorBasic(did="did:3", handle="user3.bsky.social"),
        ]

        response = self.client.get("/api/search", {"q": "user"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)


class AnalyzeProfileViewTests(TestCase):
    """Functional tests for the POST /api/analyze endpoint."""

    def setUp(self) -> None:
        self.client = Client()
        self.url = "/api/analyze"

    # ── HTTP method checks ──────────────────────────────────────────

    def test_get_method_not_allowed(self) -> None:
        """GET requests should be rejected with 405."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()["error"], "Method not allowed")

    def test_put_method_not_allowed(self) -> None:
        """PUT requests should also be rejected with 405."""
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, 405)

    # ── Invalid body checks ─────────────────────────────────────────

    def test_invalid_json_body(self) -> None:
        """Malformed JSON body should return 400."""
        response = self.client.post(
            self.url,
            data="this is not json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid JSON")

    def test_empty_body(self) -> None:
        """Empty request body should return 400 (invalid JSON)."""
        response = self.client.post(
            self.url,
            data="",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_missing_handle(self) -> None:
        """Request without 'handle' field should return 400."""
        response = self.client.post(
            self.url,
            data=json.dumps({"lang": "en"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "No handle provided")

    def test_empty_handle(self) -> None:
        """Empty string handle should return 400."""
        response = self.client.post(
            self.url,
            data=json.dumps({"handle": ""}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "No handle provided")

    def test_whitespace_only_handle(self) -> None:
        """Whitespace-only handle should return 400."""
        response = self.client.post(
            self.url,
            data=json.dumps({"handle": "   "}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "No handle provided")

    # ── External service failures ───────────────────────────────────

    @patch("analyzer.views.bsky_crawler.get_profile_data")
    def test_crawl_exception_returns_502(self, mock_crawl: MagicMock) -> None:
        """When the crawler raises an exception, response should be 502."""
        mock_crawl.side_effect = Exception("API timeout")

        response = self.client.post(
            self.url,
            data=json.dumps({"handle": "alice.bsky.social"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["error"], "Failed to fetch profile data")

    @patch("analyzer.views.bsky_crawler.get_profile_data")
    def test_profile_not_found_returns_404(self, mock_crawl: MagicMock) -> None:
        """When the crawler returns None, response should be 404."""
        mock_crawl.return_value = None

        response = self.client.post(
            self.url,
            data=json.dumps({"handle": "nonexistent.bsky.social"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.json()["error"].lower())

    @patch("analyzer.views.profile_analyzer.analyze_personality")
    @patch("analyzer.views.bsky_crawler.get_profile_data")
    def test_ai_analysis_failure_returns_500(self, mock_crawl: MagicMock, mock_analyze: MagicMock) -> None:
        """When AI analysis raises an exception, response should be 500."""
        mock_crawl.return_value = self._make_profile_result()
        mock_analyze.side_effect = Exception("LLM quota exceeded")

        response = self.client.post(
            self.url,
            data=json.dumps({"handle": "alice.bsky.social"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["error"], "AI analysis failed")

    # ── Successful flow ─────────────────────────────────────────────

    @patch("analyzer.views.profile_analyzer.analyze_personality")
    @patch("analyzer.views.bsky_crawler.get_profile_data")
    def test_successful_analysis(self, mock_crawl: MagicMock, mock_analyze: MagicMock) -> None:
        """A complete successful request returns 200 with profile + analysis."""
        profile_result = self._make_profile_result()
        mock_crawl.return_value = profile_result
        mock_analyze.return_value = {
            "mbti": "INTJ",
            "animal": "Black Panther",
            "description": "A strategic thinker...",
        }

        response = self.client.post(
            self.url,
            data=json.dumps({"handle": "Alice.Bsky.Social", "lang": "en"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        # Verify response structure
        self.assertIn("profile", data)
        self.assertIn("analysis", data)
        # Verify profile data
        self.assertEqual(data["profile"]["handle"], "alice.bsky.social")
        # Verify analysis data
        self.assertEqual(data["analysis"]["mbti"], "INTJ")
        self.assertEqual(data["analysis"]["animal"], "Black Panther")

    @patch("analyzer.views.profile_analyzer.analyze_personality")
    @patch("analyzer.views.bsky_crawler.get_profile_data")
    def test_handle_is_normalized(self, mock_crawl: MagicMock, mock_analyze: MagicMock) -> None:
        """Handle should be stripped and lowercased before use."""
        mock_crawl.return_value = self._make_profile_result()
        mock_analyze.return_value = {
            "mbti": "ENFP",
            "animal": "Monkey",
            "description": "...",
        }

        self.client.post(
            self.url,
            data=json.dumps({"handle": "  Alice.BSKY.Social  "}),
            content_type="application/json",
        )
        # The crawler should receive the normalized handle
        mock_crawl.assert_called_once_with("alice.bsky.social")

    @patch("analyzer.views.profile_analyzer.analyze_personality")
    @patch("analyzer.views.bsky_crawler.get_profile_data")
    def test_default_lang_is_cn(self, mock_crawl: MagicMock, mock_analyze: MagicMock) -> None:
        """When lang is not provided, it should default to 'cn'."""
        mock_crawl.return_value = self._make_profile_result()
        mock_analyze.return_value = {
            "mbti": "INFP",
            "animal": "小鹿",
            "description": "...",
        }

        self.client.post(
            self.url,
            data=json.dumps({"handle": "bob.bsky.social"}),
            content_type="application/json",
        )
        # analyze_personality should receive lang="cn"
        mock_analyze.assert_called_once()
        call_args, call_kwargs = mock_analyze.call_args
        lang_value = call_kwargs.get("lang", call_args[1] if len(call_args) > 1 else None)
        self.assertEqual(lang_value, "cn")

    # ── Helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _make_profile_result() -> types.ProfileResult:
        """Create a minimal ProfileResult for mocking."""
        return types.ProfileResult(
            profile=types.ProfileInfo(
                handle="alice.bsky.social",
                display_name="Alice",
                description="Hello world",
                avatar="https://example.com/avatar.jpg",
            ),
            posts=[
                types.PostFeed(
                    post={"uri": "at://did:plc:abc/app.bsky.feed.post/1"},
                    record={"text": "Today is a great day!"},
                    text="Today is a great day!",
                ),
            ],
        )
