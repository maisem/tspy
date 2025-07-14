"""Tests for the Tailscale client."""

import pytest
import requests.exceptions
from unittest.mock import Mock, patch
from tspy import TailscaleClient, TspyAPIError


class TestTailscaleClient:
    @pytest.fixture
    def client(self):
        return TailscaleClient(api_key="test-key", tailnet="test.com")
    
    @pytest.fixture
    def mock_response(self):
        mock = Mock()
        mock.json.return_value = {}
        mock.content = b'{"test": "data"}'
        mock.raise_for_status.return_value = None
        return mock
    
    def test_client_initialization(self, client):
        assert client.api_key == "test-key"
        assert client.tailnet == "test.com"
        assert client.base_url == "https://api.tailscale.com/api/v2"
    
    @patch('requests.Session.request')
    def test_list_devices(self, mock_request, client, mock_response):
        mock_response.json.return_value = {
            "devices": [
                {
                    "id": "device1",
                    "addresses": ["100.64.0.1"],
                    "authorized": True,
                    "created": "2024-01-01T00:00:00Z",
                    "expires": "2024-12-31T23:59:59Z",
                    "hostname": "test-device",
                    "name": "test-device",
                    "os": "linux",
                    "user": "user@test.com"
                }
            ]
        }
        mock_request.return_value = mock_response
        
        devices = client.list_devices()
        
        assert len(devices) == 1
        assert devices[0].id == "device1"
        assert devices[0].hostname == "test-device"
        mock_request.assert_called_once_with(
            "GET",
            "https://api.tailscale.com/api/v2/tailnet/test.com/devices"
        )
    
    @patch('requests.Session.request')
    def test_api_error_handling(self, mock_request, client):
        mock_response = Mock()
        mock_error = requests.exceptions.HTTPError("API Error")
        mock_error.response = Mock()
        mock_error.response.status_code = 404
        mock_error.response.json.side_effect = Exception("No JSON")
        mock_response.raise_for_status.side_effect = mock_error
        mock_request.return_value = mock_response
        
        with pytest.raises(TspyAPIError) as exc_info:
            client.list_devices()
        
        assert exc_info.value.status_code == 404