"""Comprehensive Tailscale API v2 client implementation."""

from typing import Any, Dict, List, Optional, Literal
import requests
from requests.auth import HTTPBasicAuth

from .models import Device, User, ACL, DNSConfig
from .exceptions import TspyAPIError


class TailscaleClient:
    """Client for interacting with the Tailscale API v2."""
    
    def __init__(self, api_key: str, tailnet: str = "-", base_url: str = "https://api.tailscale.com/api/v2"):
        """
        Initialize the Tailscale client.
        
        Args:
            api_key: Your Tailscale API key
            tailnet: Your tailnet name (default: "-" for the default tailnet)
            base_url: Base URL for the API (default: https://api.tailscale.com/api/v2)
        """
        self.api_key = api_key
        self.tailnet = tailnet
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(api_key, "")
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
    
    def _request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """Make an HTTP request to the Tailscale API."""
        url = f"{self.base_url}{endpoint}"
        if params:
            kwargs['params'] = params
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return None
            
        except requests.exceptions.HTTPError as e:
            error_data = None
            try:
                error_data = e.response.json()
            except Exception:
                pass
            
            raise TspyAPIError(
                f"API request failed: {e}",
                status_code=e.response.status_code,
                response_data=error_data
            )
        except requests.exceptions.RequestException as e:
            raise TspyAPIError(f"Request failed: {e}")
    
    # Device endpoints
    def list_devices(self, fields: Optional[Literal["all", "default"]] = "all") -> List[Device]:
        """List all devices in the tailnet.
        
        Args:
            fields: Control which fields are returned. "all" returns all fields,
                   "default" returns a limited set. If not specified, default is used.
        """
        params = {"fields": fields} if fields else None
        data = self._request("GET", f"/tailnet/{self.tailnet}/devices", params=params)
        return [Device(**device) for device in data.get("devices", [])]
    
    def get_device(self, device_id: str, fields: Optional[Literal["all", "default"]] = "all") -> Device:
        """Get details of a specific device.
        
        Args:
            device_id: ID of the device (nodeId preferred, numeric id also works)
            fields: Control which fields are returned
        """
        params = {"fields": fields} if fields else None
        data = self._request("GET", f"/device/{device_id}", params=params)
        return Device(**data)
    
    def delete_device(self, device_id: str) -> None:
        """Delete a device from the tailnet."""
        self._request("DELETE", f"/device/{device_id}")
    
    def authorize_device(self, device_id: str, authorized: bool = True) -> None:
        """Authorize or deauthorize a device."""
        self._request("POST", f"/device/{device_id}/authorized", json={"authorized": authorized})
    
    def update_device_tags(self, device_id: str, tags: List[str]) -> None:
        """Update tags for a device."""
        self._request("POST", f"/device/{device_id}/tags", json={"tags": tags})
    
    def expire_device_key(self, device_id: str) -> None:
        """Mark a device's node key as expired, requiring re-authentication."""
        self._request("POST", f"/device/{device_id}/expire")
    
    def get_device_routes(self, device_id: str) -> Dict[str, Any]:
        """Get the list of subnet routes for a device."""
        return self._request("GET", f"/device/{device_id}/routes")
    
    def set_device_routes(self, device_id: str, routes: List[str]) -> Dict[str, Any]:
        """Set enabled subnet routes for a device."""
        return self._request("POST", f"/device/{device_id}/routes", json={"routes": routes})
    
    def set_device_name(self, device_id: str, name: str) -> None:
        """Set device name. Can be FQDN or just the base name."""
        self._request("POST", f"/device/{device_id}/name", json={"name": name})
    
    def update_device_key(self, device_id: str, key_expiry_disabled: bool) -> None:
        """Enable or disable key expiry for a device."""
        self._request("POST", f"/device/{device_id}/key", json={"keyExpiryDisabled": key_expiry_disabled})
    
    def set_device_ipv4(self, device_id: str, ipv4: str) -> None:
        """Set a specific IPv4 address for a device. This will break existing connections."""
        self._request("POST", f"/device/{device_id}/ip", json={"ipv4": ipv4})
    
    def get_device_attributes(self, device_id: str) -> Dict[str, Any]:
        """Get all posture attributes for a device."""
        return self._request("GET", f"/device/{device_id}/attributes")
    
    def set_device_attribute(self, device_id: str, attribute_key: str, value: Any, 
                           expiry: Optional[str] = None, comment: Optional[str] = None) -> Dict[str, Any]:
        """Set a custom posture attribute on a device. Key must be prefixed with 'custom:'."""
        body = {"value": value}
        if expiry:
            body["expiry"] = expiry
        if comment:
            body["comment"] = comment
        return self._request("POST", f"/device/{device_id}/attributes/{attribute_key}", json=body)
    
    def delete_device_attribute(self, device_id: str, attribute_key: str) -> None:
        """Delete a custom posture attribute from a device."""
        self._request("DELETE", f"/device/{device_id}/attributes/{attribute_key}")
    
    # Device invites
    def list_device_invites(self, device_id: str) -> List[Dict[str, Any]]:
        """List all share invites for a device."""
        data = self._request("GET", f"/device/{device_id}/device-invites")
        return data.get("invites", [])
    
    def create_device_invite(self, device_id: str, multiUse: bool = False, 
                           allowExitNode: bool = False, email: Optional[str] = None) -> Dict[str, Any]:
        """Create a device share invite."""
        body = {"multiUse": multiUse, "allowExitNode": allowExitNode}
        if email:
            body["email"] = email
        return self._request("POST", f"/device/{device_id}/device-invites", json=body)
    
    def get_device_invite(self, invite_id: str) -> Dict[str, Any]:
        """Get details of a device invite."""
        return self._request("GET", f"/device-invites/{invite_id}")
    
    def delete_device_invite(self, invite_id: str) -> None:
        """Delete a device invite."""
        self._request("DELETE", f"/device-invites/{invite_id}")
    
    def resend_device_invite(self, invite_id: str) -> None:
        """Resend a device invite email."""
        self._request("POST", f"/device-invites/{invite_id}/resend")
    
    def accept_device_invite(self, code: str) -> None:
        """Accept a device share invite."""
        self._request("POST", "/device-invites/-/accept", json={"code": code})
    
    # User endpoints
    def list_users(self) -> List[User]:
        """List all users in the tailnet."""
        data = self._request("GET", f"/tailnet/{self.tailnet}/users")
        return [User(**user) for user in data.get("users", [])]
    
    def get_user(self, user_id: str) -> User:
        """Get details of a specific user."""
        data = self._request("GET", f"/tailnet/{self.tailnet}/users/{user_id}")
        return User(**data)
    
    def delete_user(self, user_id: str) -> None:
        """Delete a user from the tailnet."""
        self._request("DELETE", f"/tailnet/{self.tailnet}/users/{user_id}")
    
    def approve_user(self, user_id: str) -> None:
        """Approve a user."""
        self._request("POST", f"/users/{user_id}/approve")
    
    def suspend_user(self, user_id: str) -> None:
        """Suspend a user."""
        self._request("POST", f"/users/{user_id}/suspend")
    
    def restore_user(self, user_id: str) -> None:
        """Restore a suspended user."""
        self._request("POST", f"/users/{user_id}/restore")
    
    def delete_user_v2(self, user_id: str) -> None:
        """Delete a user (v2 endpoint)."""
        self._request("POST", f"/users/{user_id}/delete")
    
    def set_user_role(self, user_id: str, role: str) -> None:
        """Set user role. Valid roles: member, admin, billing, auditor, it-admin"""
        self._request("POST", f"/users/{user_id}/role", json={"role": role})
    
    # User invites
    def list_user_invites(self) -> List[Dict[str, Any]]:
        """List all user invites."""
        data = self._request("GET", f"/tailnet/{self.tailnet}/user-invites")
        return data.get("invites", []) if data else []
    
    def create_user_invite(self, email: str, role: str = "member") -> Dict[str, Any]:
        """Create a user invite."""
        return self._request("POST", f"/tailnet/{self.tailnet}/user-invites", json={"email": email, "role": role})
    
    def get_user_invite(self, invite_id: str) -> Dict[str, Any]:
        """Get details of a user invite."""
        return self._request("GET", f"/user-invites/{invite_id}")
    
    def delete_user_invite(self, invite_id: str) -> None:
        """Delete a user invite."""
        self._request("DELETE", f"/user-invites/{invite_id}")
    
    def resend_user_invite(self, invite_id: str) -> None:
        """Resend a user invite email."""
        self._request("POST", f"/user-invites/{invite_id}/resend")
    
    # ACL endpoints
    def get_acl(self) -> ACL:
        """Get the current ACL configuration."""
        data = self._request("GET", f"/tailnet/{self.tailnet}/acl")
        return ACL(**data)
    
    def update_acl(self, acl: Dict[str, Any], if_unmodified_since: Optional[str] = None) -> ACL:
        """Update the ACL configuration."""
        headers = {"If-Unmodified-Since": if_unmodified_since} if if_unmodified_since else None
        data = self._request("POST", f"/tailnet/{self.tailnet}/acl", json=acl, headers=headers)
        return ACL(**data)
    
    def preview_acl(self, acl: Dict[str, Any]) -> Dict[str, Any]:
        """Preview ACL changes without applying them."""
        return self._request("POST", f"/tailnet/{self.tailnet}/acl/preview", json=acl)
    
    def validate_acl(self, acl: Dict[str, Any]) -> Dict[str, Any]:
        """Validate an ACL configuration without applying it."""
        return self._request("POST", f"/tailnet/{self.tailnet}/acl/validate", json=acl)
    
    # DNS endpoints
    def get_dns_config(self) -> DNSConfig:
        """Get the current DNS configuration."""
        data = self._request("GET", f"/tailnet/{self.tailnet}/dns/preferences")
        return DNSConfig(**data)
    
    def update_dns_config(self, config: Dict[str, Any]) -> DNSConfig:
        """Update the DNS configuration."""
        data = self._request("POST", f"/tailnet/{self.tailnet}/dns/preferences", json=config)
        return DNSConfig(**data)
    
    def get_nameservers(self) -> List[str]:
        """Get the list of DNS nameservers."""
        data = self._request("GET", f"/tailnet/{self.tailnet}/dns/nameservers")
        return data.get("dns", [])
    
    def set_nameservers(self, nameservers: List[str]) -> None:
        """Set the DNS nameservers."""
        self._request("POST", f"/tailnet/{self.tailnet}/dns/nameservers", json={"dns": nameservers})
    
    def get_searchpaths(self) -> List[str]:
        """Get the list of DNS search paths."""
        data = self._request("GET", f"/tailnet/{self.tailnet}/dns/searchpaths")
        return data.get("searchPaths", [])
    
    def set_searchpaths(self, searchpaths: List[str]) -> None:
        """Set the DNS search paths."""
        self._request("POST", f"/tailnet/{self.tailnet}/dns/searchpaths", json={"searchPaths": searchpaths})
    
    def get_split_dns(self) -> Dict[str, Any]:
        """Get split DNS configuration."""
        return self._request("GET", f"/tailnet/{self.tailnet}/dns/split-dns")
    
    def update_split_dns(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update split DNS configuration."""
        return self._request("PATCH", f"/tailnet/{self.tailnet}/dns/split-dns", json=config)
    
    # Key endpoints
    def list_api_keys(self) -> List[Dict[str, Any]]:
        """List all API keys for the tailnet."""
        data = self._request("GET", f"/tailnet/{self.tailnet}/keys")
        return data.get("keys", [])
    
    def create_api_key(self, capabilities: Dict[str, Any], expiry_seconds: int = 90 * 24 * 60 * 60,
                      description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new API key."""
        body = {"capabilities": capabilities, "expirySeconds": expiry_seconds}
        if description:
            body["description"] = description
        return self._request("POST", f"/tailnet/{self.tailnet}/keys", json=body)
    
    def get_api_key(self, key_id: str) -> Dict[str, Any]:
        """Get details of an API key."""
        return self._request("GET", f"/tailnet/{self.tailnet}/keys/{key_id}")
    
    def delete_api_key(self, key_id: str) -> None:
        """Delete an API key."""
        self._request("DELETE", f"/tailnet/{self.tailnet}/keys/{key_id}")
    
    # Auth keys
    def list_auth_keys(self) -> List[Dict[str, Any]]:
        """List all auth keys for the tailnet."""
        data = self._request("GET", f"/tailnet/{self.tailnet}/keys")
        return data.get("keys", [])
    
    def create_auth_key(self, ephemeral: bool = False, reusable: bool = False, 
                       expiry_seconds: int = 90 * 24 * 60 * 60, 
                       description: Optional[str] = None,
                       tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new auth key."""
        body = {
            "capabilities": {
                "devices": {
                    "create": {
                        "ephemeral": ephemeral,
                        "reusable": reusable,
                        "tags": tags or []
                    }
                }
            },
            "expirySeconds": expiry_seconds
        }
        if description:
            body["description"] = description
        return self._request("POST", f"/tailnet/{self.tailnet}/keys", json=body)
    
    # Logging endpoints
    def get_configuration_audit_logs(self, start: str, end: Optional[str] = None,
                                    actor: Optional[str] = None, target: Optional[str] = None,
                                    event: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get configuration audit logs.
        
        Args:
            start: Start time in RFC 3339 format (required)
            end: End time in RFC 3339 format
            actor: Filter by actor
            target: Filter by target
            event: Filter by event type
        """
        params = {"start": start}
        if end:
            params["end"] = end
        if actor:
            params["actor"] = actor
        if target:
            params["target"] = target
        if event:
            params["event"] = event
        data = self._request("GET", f"/tailnet/{self.tailnet}/logging/configuration", params=params)
        logs = data.get("logs") if data else None
        return logs if logs is not None else []
    
    
    def get_network_logs(self, start: Optional[str] = None, end: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get network logs."""
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        data = self._request("GET", f"/tailnet/{self.tailnet}/logging/network", params=params)
        return data.get("logs", [])
    
    def get_log_stream_status(self, log_type: str) -> Dict[str, Any]:
        """Get log streaming status. Log types: configuration, network, audit"""
        return self._request("GET", f"/tailnet/{self.tailnet}/logging/{log_type}/stream/status")
    
    def set_log_stream(self, log_type: str, destination: str, enabled: bool = True) -> None:
        """Configure log streaming. Log types: configuration, network, audit"""
        body = {"destination": destination, "enabled": enabled}
        self._request("POST", f"/tailnet/{self.tailnet}/logging/{log_type}/stream", json=body)
    
    def delete_log_stream(self, log_type: str) -> None:
        """Delete log streaming configuration."""
        self._request("DELETE", f"/tailnet/{self.tailnet}/logging/{log_type}/stream")
    
    # Contacts endpoints
    def get_contacts(self) -> Dict[str, Any]:
        """Get contact preferences."""
        return self._request("GET", f"/tailnet/{self.tailnet}/contacts")
    
    def update_contact(self, contact_type: str, email: str) -> Dict[str, Any]:
        """Update contact email. Contact types: security, support, billing"""
        return self._request("PATCH", f"/tailnet/{self.tailnet}/contacts/{contact_type}", 
                           json={"email": email})
    
    def resend_contact_verification(self, contact_type: str) -> None:
        """Resend contact verification email."""
        self._request("POST", f"/tailnet/{self.tailnet}/contacts/{contact_type}/resend-verification-email")
    
    # Webhook endpoints
    def list_webhooks(self) -> List[Dict[str, Any]]:
        """List all webhook endpoints."""
        data = self._request("GET", f"/tailnet/{self.tailnet}/webhooks")
        webhooks = data.get("webhooks") if data else None
        return webhooks if webhooks is not None else []
    
    def create_webhook(self, endpoint_url: str, provider_type: str = "generic",
                      subscriptions: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a webhook endpoint."""
        body = {"endpointUrl": endpoint_url, "providerType": provider_type}
        if subscriptions:
            body["subscriptions"] = subscriptions
        return self._request("POST", f"/tailnet/{self.tailnet}/webhooks", json=body)
    
    def get_webhook(self, endpoint_id: str) -> Dict[str, Any]:
        """Get webhook endpoint details."""
        return self._request("GET", f"/webhooks/{endpoint_id}")
    
    def update_webhook(self, endpoint_id: str, subscriptions: List[str]) -> Dict[str, Any]:
        """Update webhook subscriptions."""
        return self._request("PATCH", f"/webhooks/{endpoint_id}", 
                           json={"subscriptions": subscriptions})
    
    def delete_webhook(self, endpoint_id: str) -> None:
        """Delete a webhook endpoint."""
        self._request("DELETE", f"/webhooks/{endpoint_id}")
    
    def test_webhook(self, endpoint_id: str) -> None:
        """Send a test event to webhook endpoint."""
        self._request("POST", f"/webhooks/{endpoint_id}/test")
    
    def rotate_webhook_secret(self, endpoint_id: str) -> Dict[str, Any]:
        """Rotate webhook signing secret."""
        return self._request("POST", f"/webhooks/{endpoint_id}/rotate")
    
    # Tailnet settings
    def get_tailnet_settings(self) -> Dict[str, Any]:
        """Get tailnet settings."""
        return self._request("GET", f"/tailnet/{self.tailnet}/settings")
    
    def update_tailnet_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update tailnet settings."""
        return self._request("PATCH", f"/tailnet/{self.tailnet}/settings", json=settings)
    
    # Device posture integrations
    def list_posture_integrations(self) -> List[Dict[str, Any]]:
        """List device posture integrations."""
        data = self._request("GET", f"/tailnet/{self.tailnet}/posture/integrations")
        return data.get("integrations", [])
    
    def create_posture_integration(self, provider: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a device posture integration."""
        return self._request("POST", f"/tailnet/{self.tailnet}/posture/integrations",
                           json={"provider": provider, "config": config})
    
    def get_posture_integration(self, integration_id: str) -> Dict[str, Any]:
        """Get device posture integration details."""
        return self._request("GET", f"/tailnet/{self.tailnet}/posture/integrations/{integration_id}")
    
    def update_posture_integration(self, integration_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update device posture integration."""
        return self._request("PATCH", f"/tailnet/{self.tailnet}/posture/integrations/{integration_id}",
                           json={"config": config})
    
    def delete_posture_integration(self, integration_id: str) -> None:
        """Delete device posture integration."""
        self._request("DELETE", f"/tailnet/{self.tailnet}/posture/integrations/{integration_id}")