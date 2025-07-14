#!/usr/bin/env python3
"""Example usage of the tspy client demonstrating all GET/LIST APIs."""

import os
from tspy import TailscaleClient

# Get API key from environment variable
api_key = os.environ.get("TAILSCALE_API_KEY")
tailnet = os.environ.get("TAILSCALE_TAILNET", "-")  # Default to "-" if not set

if not api_key:
    print("Please set TAILSCALE_API_KEY environment variable")
    exit(1)

# Initialize client
client = TailscaleClient(api_key=api_key, tailnet=tailnet)

# List devices
print("=== DEVICES ===")
print("\nListing all devices:")
devices = client.list_devices()
print(f"Found {len(devices)} devices")

if devices:
    # Show first device details
    device = devices[0]
    print(f"\nFirst device: {device.name}")
    print(f"  ID: {device.id}")
    print(f"  Node ID: {device.node_id}")
    print(f"  Hostname: {device.hostname}")
    print(f"  OS: {device.os}")
    print(f"  Authorized: {device.authorized}")
    if device.tailscale_ips:
        print(f"  IPs: {', '.join(device.tailscale_ips)}")
    
    # Get device details
    print(f"\nGetting device details for {device.id}:")
    device_detail = client.get_device(device.id)
    print(f"  Name: {device_detail.name}")
    print(f"  Created: {device_detail.created}")
    print(f"  Last seen: {device_detail.last_seen}")
    
    # Get device routes
    print(f"\nGetting routes for device {device.id}:")
    try:
        routes = client.get_device_routes(device.id)
        print(f"  Advertised routes: {routes.get('advertisedRoutes', [])}")
        print(f"  Enabled routes: {routes.get('enabledRoutes', [])}")
    except Exception as e:
        print(f"  Error getting routes: {e}")
    
    # Get device attributes
    print(f"\nGetting attributes for device {device.id}:")
    try:
        attrs = client.get_device_attributes(device.id)
        print(f"  Attributes: {attrs}")
    except Exception as e:
        print(f"  Error getting attributes: {e}")

# List users
print("\n\n=== USERS ===")
print("\nListing all users:")
users = client.list_users()
print(f"Found {len(users)} users")

if users:
    # Show first user details
    user = users[0]
    print(f"\nFirst user: {user.display_name}")
    print(f"  ID: {user.id}")
    print(f"  Login: {user.login_name}")
    print(f"  Role: {user.role}")
    print(f"  Status: {user.status}")
    
    # Get user details
    print(f"\nGetting user details for {user.id}:")
    try:
        user_detail = client.get_user(user.id)
        print(f"  Display name: {user_detail.display_name}")
        print(f"  Created: {user_detail.created}")
        print(f"  Device count: {user_detail.device_count}")
    except Exception as e:
        print(f"  Error getting user details: {e}")

# List user invites
print("\n\n=== USER INVITES ===")
try:
    invites = client.list_user_invites()
    print(f"Found {len(invites)} user invites")
    for invite in invites[:3]:  # Show first 3
        print(f"  - {invite.get('email')} (Role: {invite.get('role')})")
except Exception as e:
    print(f"Error listing user invites: {e}")

# Get ACL
print("\n\n=== ACL ===")
try:
    acl = client.get_acl()
    print(f"ACL has {len(acl.acls)} rules")
    if acl.groups:
        print(f"Groups defined: {', '.join(acl.groups.keys())}")
    if acl.tag_owners:
        print(f"Tag owners defined: {', '.join(acl.tag_owners.keys())}")
except Exception as e:
    print(f"Error getting ACL: {e}")

# DNS Configuration
print("\n\n=== DNS ===")
print("\nGetting DNS preferences:")
dns = client.get_dns_config()
print(f"  Magic DNS: {dns.magic_dns}")
if dns.domains:
    print(f"  Domains: {', '.join(dns.domains)}")
if dns.nameservers:
    print(f"  Nameservers: {', '.join(dns.nameservers)}")

# Get nameservers
print("\nGetting nameservers:")
try:
    nameservers = client.get_nameservers()
    print(f"  Nameservers: {', '.join(nameservers)}")
except Exception as e:
    print(f"  Error getting nameservers: {e}")

# Get search paths
print("\nGetting search paths:")
try:
    searchpaths = client.get_searchpaths()
    print(f"  Search paths: {', '.join(searchpaths)}")
except Exception as e:
    print(f"  Error getting search paths: {e}")

# Get split DNS
print("\nGetting split DNS configuration:")
try:
    split_dns = client.get_split_dns()
    print(f"  Split DNS: {split_dns}")
except Exception as e:
    print(f"  Error getting split DNS: {e}")

# List API keys
print("\n\n=== KEYS ===")
print("\nListing API keys:")
try:
    api_keys = client.list_api_keys()
    print(f"Found {len(api_keys)} API keys")
    for key in api_keys[:3]:  # Show first 3
        print(f"  - {key.get('id')} ({key.get('description', 'No description')})")
except Exception as e:
    print(f"Error listing API keys: {e}")

# Get tailnet settings
print("\n\n=== TAILNET SETTINGS ===")
try:
    settings = client.get_tailnet_settings()
    print("Tailnet settings:")
    for key, value in settings.items():
        print(f"  {key}: {value}")
except Exception as e:
    print(f"Error getting tailnet settings: {e}")

# Get contacts
print("\n\n=== CONTACTS ===")
try:
    contacts = client.get_contacts()
    print("Contact preferences:")
    for contact_type, email in contacts.items():
        print(f"  {contact_type}: {email}")
except Exception as e:
    print(f"Error getting contacts: {e}")

# List webhooks
print("\n\n=== WEBHOOKS ===")
try:
    webhooks = client.list_webhooks()
    print(f"Found {len(webhooks)} webhooks")
    for webhook in webhooks[:3]:  # Show first 3
        print(f"  - {webhook.get('endpointUrl')} (Type: {webhook.get('providerType')})")
except Exception as e:
    print(f"Error listing webhooks: {e}")

# List posture integrations
print("\n\n=== DEVICE POSTURE INTEGRATIONS ===")
try:
    integrations = client.list_posture_integrations()
    print(f"Found {len(integrations)} posture integrations")
    for integration in integrations[:3]:  # Show first 3
        print(f"  - {integration.get('id')} (Provider: {integration.get('provider')})")
except Exception as e:
    print(f"Error listing posture integrations: {e}")

# Get log configuration
print("\n\n=== LOGGING ===")
print("\nGetting configuration audit logs (last 24 hours):")
try:
    from datetime import datetime, timedelta
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)
    logs = client.get_configuration_audit_logs(
        start=start_time.isoformat() + "Z",
        end=end_time.isoformat() + "Z"
    )
    print(f"  Found {len(logs)} audit log entries")
    if logs:
        print(f"  Latest entry: {logs[0]}")
except Exception as e:
    print(f"  Error getting configuration audit logs: {e}")

# Get network logs (requires logs:network:read OAuth scope)
print("\nGetting network logs (last hour):")
try:
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)
    logs = client.get_network_logs(
        start=start_time.isoformat() + "Z",
        end=end_time.isoformat() + "Z"
    )
    print(f"  Found {len(logs)} log entries")
    if logs:
        print(f"  Latest entry: {logs[0]}")
except Exception as e:
    print(f"  Error getting network logs: {e}")
    print("  Note: This requires logs:network:read OAuth scope")

print("\n\nExample completed!")