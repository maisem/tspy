"""Pydantic models for Tailscale API responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator


class Device(BaseModel):
    """Represents a Tailscale device."""
    id: str
    addresses: List[str]
    authorized: bool
    blocked_ports: Optional[List[int]] = Field(None, alias="blockedPorts")
    blocks_incoming_connections: Optional[bool] = Field(None, alias="blocksIncomingConnections")
    client_connectivity: Optional[Dict[str, Any]] = Field(None, alias="clientConnectivity")
    client_version: Optional[str] = Field(None, alias="clientVersion")
    created: Optional[datetime] = None
    expires: Optional[datetime] = None
    hostname: str
    is_external: Optional[bool] = Field(None, alias="isExternal")
    key_expiry_disabled: Optional[bool] = Field(None, alias="keyExpiryDisabled")
    last_seen: Optional[datetime] = Field(None, alias="lastSeen")
    machine_key: Optional[str] = Field(None, alias="machineKey")
    name: str
    node_id: Optional[str] = Field(None, alias="nodeId")
    node_key: Optional[str] = Field(None, alias="nodeKey")
    os: str
    tags: Optional[List[str]] = None
    tailnet_lock_error: Optional[str] = Field(None, alias="tailnetLockError")
    tailnet_lock_key: Optional[str] = Field(None, alias="tailnetLockKey")
    tailscale_ips: Optional[List[str]] = Field(None, alias="tailscaleIPs")
    update_available: Optional[bool] = Field(None, alias="updateAvailable")
    user: str
    
    @field_validator('created', 'expires', 'last_seen', mode='before')
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        return v


class User(BaseModel):
    """Represents a Tailscale user."""
    id: str
    login_name: str = Field(alias="loginName")
    display_name: str = Field(alias="displayName")
    profile_pic_url: Optional[str] = Field(None, alias="profilePicUrl")
    tailnet_id: Optional[str] = Field(None, alias="tailnetId")
    created: Optional[datetime] = None
    type: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    device_count: Optional[int] = Field(None, alias="deviceCount")
    last_seen: Optional[datetime] = Field(None, alias="lastSeen")
    currently_connected: Optional[bool] = Field(None, alias="currentlyConnected")
    
    @field_validator('created', 'last_seen', mode='before')
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        return v


class ACL(BaseModel):
    """Represents Tailscale ACL configuration."""
    acls: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    groups: Optional[Dict[str, List[str]]] = None
    hosts: Optional[Dict[str, str]] = None
    tag_owners: Optional[Dict[str, List[str]]] = Field(None, alias="tagOwners")
    tests: Optional[List[Dict[str, Any]]] = None
    ssh: Optional[List[Dict[str, Any]]] = None
    node_attrs: Optional[List[Dict[str, Any]]] = Field(None, alias="nodeAttrs")


class DNSConfig(BaseModel):
    """Represents DNS configuration."""
    domains: Optional[List[str]] = Field(default_factory=list)
    magic_dns: bool = Field(alias="magicDNS")
    nameservers: Optional[List[str]] = Field(default_factory=list)
    override_local_dns: Optional[bool] = Field(None, alias="overrideLocalDNS")
    routes: Optional[Dict[str, List[str]]] = None


class DeviceRoutes(BaseModel):
    """Represents device routes configuration."""
    advertised_routes: List[str] = Field(alias="advertisedRoutes")
    enabled_routes: List[str] = Field(alias="enabledRoutes")


class DevicePostureAttributes(BaseModel):
    """Device posture attributes."""
    attributes: Dict[str, Union[str, int, bool]]


class DeviceInvite(BaseModel):
    """Represents a device share invite."""
    id: str
    created: datetime
    email: Optional[str] = None
    multi_use: bool = Field(alias="multiUse")
    allow_exit_node: bool = Field(alias="allowExitNode")
    used: bool
    device_id: str = Field(alias="deviceId")
    expires: Optional[datetime] = None


class UserInvite(BaseModel):
    """Represents a user invite."""
    id: str
    email: str
    role: str
    created_at: datetime = Field(alias="createdAt")
    expires_at: datetime = Field(alias="expiresAt")
    accepted: bool
    sent_at: Optional[datetime] = Field(None, alias="sentAt")


class ApiKey(BaseModel):
    """Represents an API key."""
    id: str
    description: Optional[str] = None
    capabilities: Dict[str, Any]
    created: datetime
    expires: datetime
    revoked: Optional[datetime] = None


class AuthKey(BaseModel):
    """Represents an auth key."""
    id: str
    description: Optional[str] = None
    created: datetime
    expires: datetime
    capabilities: Dict[str, Any]
    revoked: Optional[datetime] = None


class LogEntry(BaseModel):
    """Represents a log entry."""
    timestamp: datetime
    type: str
    message: str
    data: Optional[Dict[str, Any]] = None


class ContactPreference(BaseModel):
    """Represents contact preferences."""
    security: Optional[str] = None
    support: Optional[str] = None
    billing: Optional[str] = None


class Webhook(BaseModel):
    """Represents a webhook endpoint."""
    endpoint_id: str = Field(alias="endpointId")
    endpoint_url: str = Field(alias="endpointUrl")
    provider_type: str = Field(alias="providerType")
    subscriptions: List[str]
    created: datetime
    last_triggered: Optional[datetime] = Field(None, alias="lastTriggered")
    secret: Optional[str] = None


class TailnetSettings(BaseModel):
    """Represents tailnet settings."""
    devices_approval_on: Optional[bool] = Field(None, alias="devicesApprovalOn")
    devices_auto_updates_on: Optional[bool] = Field(None, alias="devicesAutoUpdatesOn")
    devices_key_duration_days: Optional[int] = Field(None, alias="devicesKeyDurationDays")
    network_flow_logging_on: Optional[bool] = Field(None, alias="networkFlowLoggingOn")
    regional_routing_on: Optional[bool] = Field(None, alias="regionalRoutingOn")
    route_all_on: Optional[bool] = Field(None, alias="routeAllOn")
    magic_dns_enabled: Optional[bool] = Field(None, alias="magicDNSEnabled")
    enhanced_security_features_on: Optional[bool] = Field(None, alias="enhancedSecurityFeaturesOn")


class PostureIntegration(BaseModel):
    """Represents a device posture integration."""
    id: str
    provider: str
    created_at: datetime = Field(alias="createdAt")
    config: Dict[str, Any]