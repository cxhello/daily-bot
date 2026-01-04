"""Tests for history data source"""
import pytest
from unittest.mock import patch, AsyncMock
from data_sources.history import get_history_today_events, format_history_message


@pytest.mark.anyio
async def test_get_history_today_events_success():
    """Test successful API call and event filtering"""
    mock_response = {
        "events": [
            {"year": 2020, "text": "Event in 2020"},
            {"year": 2010, "text": "Event in 2010"},
            {"year": 2000, "text": "Event in 2000"},
            {"year": 1995, "text": "Event in 1995"},
            {"year": 1990, "text": "Event in 1990"},
            {"year": 1985, "text": "Event in 1985"},  # Should be filtered out
            {"year": 1980, "text": "Event in 1980"},  # Should be filtered out
        ]
    }

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)

        result = await get_history_today_events(birth_year=1989)

        assert result is not None
        assert "events" in result
        assert len(result["events"]) == 5
        assert result["count"] == 5

        # Verify all events are after birth year
        for event in result["events"]:
            assert event["year"] >= 1989
            assert "age" in event
            assert event["age"] == event["year"] - 1989


@pytest.mark.anyio
async def test_get_history_today_events_api_failure():
    """Test API failure returns None"""
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 500

        result = await get_history_today_events(birth_year=1989)

        assert result is None


@pytest.mark.anyio
async def test_get_history_today_events_few_events():
    """Test when fewer than 5 events available"""
    mock_response = {
        "events": [
            {"year": 2020, "text": "Event in 2020"},
            {"year": 2010, "text": "Event in 2010"},
        ]
    }

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)

        result = await get_history_today_events(birth_year=1989)

        assert result is not None
        assert len(result["events"]) == 2
        assert result["count"] == 2


def test_format_history_message_success():
    """Test formatting history message with valid data"""
    history_data = {
        "events": [
            {"year": 2020, "text": "重大事件", "age": 31},
            {"year": 2010, "text": "另一个事件", "age": 21},
        ],
        "count": 2
    }

    result = format_history_message(history_data)

    assert "📜 历史上的今天" in result
    assert "2020年 - 重大事件 (那年我 31 岁)" in result
    assert "2010年 - 另一个事件 (那年我 21 岁)" in result


def test_format_history_message_empty():
    """Test formatting with empty data returns empty string"""
    assert format_history_message(None) == ""
    assert format_history_message({}) == ""
    assert format_history_message({"events": []}) == ""
