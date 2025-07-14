# tspy - Tailscale Python Client

A Python client library for the Tailscale API.

> **Note**: This entire library was vibe-coded with Claude Code - no manual typing required! 🤖

## Features

- Complete implementation of Tailscale API v2
- Type-safe with Pydantic models
- Comprehensive error handling
- Support for all major Tailscale resources:
  - Devices
  - Users
  - ACLs
  - DNS
  - Keys
  - Webhooks
  - Audit Logs
  - And more!

## Installation

```bash
pip install tspy
```

## Quick Start

```python
from tspy import TailscaleClient

# Initialize the client with your API key
client = TailscaleClient(
    api_key="your-api-key",
    tailnet="your-tailnet"  # or "-" for the default tailnet
)

# List all devices
devices = client.list_devices()
for device in devices:
    print(f"{device.name} - {device.os}")

# Get device details
device = client.get_device("device-id")
print(f"Device {device.name} last seen: {device.last_seen}")

# List users
users = client.list_users()
for user in users:
    print(f"{user.display_name} ({user.login_name})")
```

## Configuration

### Environment Variables

You can set your API credentials as environment variables:

```bash
export TAILSCALE_API_KEY="tskey-api-xxxx"
export TAILSCALE_TAILNET="example.com"  # Optional, defaults to "-"
```

Then use them in your code:

```python
import os
from tspy import TailscaleClient

client = TailscaleClient(
    api_key=os.environ["TAILSCALE_API_KEY"],
    tailnet=os.environ.get("TAILSCALE_TAILNET", "-")
)
```

## Examples

See the [example.py](example.py) file for a comprehensive example that demonstrates all available API endpoints.

### Managing Devices

```python
# List all devices with details
devices = client.list_devices(fields="all")

# Authorize a device
client.authorize_device("device-id", authorized=True)

# Update device tags
client.update_device_tags("device-id", ["tag:server", "tag:production"])

# Delete a device
client.delete_device("device-id")
```

### Managing Users

```python
# List all users
users = client.list_users()

# Get user details
user = client.get_user("user-id")

# Update user role
client.set_user_role("user-id", "admin")

# Suspend a user
client.suspend_user("user-id")
```

### ACL Management

```python
# Get current ACL
acl = client.get_acl()

# Update ACL
new_acl = {
    "acls": [
        {"action": "accept", "src": ["*"], "dst": ["*:*"]}
    ]
}
client.update_acl(new_acl)
```

### DNS Configuration

```python
# Get DNS configuration
dns_config = client.get_dns_config()

# Update nameservers
client.set_nameservers(["8.8.8.8", "8.8.4.4"])

# Get search paths
search_paths = client.get_searchpaths()
```

### API Keys

```python
# List API keys
keys = client.list_api_keys()

# Create a new API key
key = client.create_api_key(
    capabilities={
        "devices": {
            "create": {"reusable": False, "ephemeral": False},
            "update": ["authorized", "tags"],
            "delete": True
        }
    },
    expiry_seconds=90 * 24 * 60 * 60  # 90 days
)
```

### Webhooks

```python
# List webhooks
webhooks = client.list_webhooks()

# Create a webhook
webhook = client.create_webhook(
    endpoint_url="https://example.com/webhook",
    provider_type="generic",
    subscriptions=["device.created", "device.deleted"]
)
```

### Audit Logs

```python
from datetime import datetime, timedelta

# Get audit logs for the last 24 hours
end_time = datetime.now()
start_time = end_time - timedelta(days=1)

logs = client.get_configuration_audit_logs(
    start=start_time.isoformat() + "Z",
    end=end_time.isoformat() + "Z"
)
```

## Error Handling

The client includes comprehensive error handling:

```python
from tspy.exceptions import TspyAPIError

try:
    device = client.get_device("invalid-id")
except TspyAPIError as e:
    print(f"API Error: {e}")
    print(f"Status Code: {e.status_code}")
    print(f"Response: {e.response_data}")
```

## API Reference

For detailed API documentation, see the [Tailscale API documentation](https://tailscale.com/api).

The OpenAPI specification is available at: https://api.tailscale.com/api/v2?outputOpenapiSchema=true

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/tspy.git
cd tspy

# Install dependencies with uv
uv sync

# Run tests
uv run pytest
```

### Running the Example

```bash
export TAILSCALE_API_KEY="your-api-key"
export TAILSCALE_TAILNET="your-tailnet"
uv run python example.py
```


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This is not an official Tailscale product and is not affiliated with Tailscale Inc.