"""tspy - A Python client for the Tailscale API."""

__version__ = "0.1.0"

from .client import TailscaleClient
from .exceptions import TspyError, TspyAPIError
from .models import (
    Device, User, ACL, DNSConfig, DeviceRoutes, DevicePostureAttributes,
    DeviceInvite, UserInvite, ApiKey, AuthKey, LogEntry, ContactPreference,
    Webhook, TailnetSettings, PostureIntegration
)

__all__ = [
    "TailscaleClient", "TspyError", "TspyAPIError",
    "Device", "User", "ACL", "DNSConfig", "DeviceRoutes", "DevicePostureAttributes",
    "DeviceInvite", "UserInvite", "ApiKey", "AuthKey", "LogEntry", "ContactPreference",
    "Webhook", "TailnetSettings", "PostureIntegration"
]