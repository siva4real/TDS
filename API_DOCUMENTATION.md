# API Documentation

Complete API reference for the Automated GitHub Pages Deployment API.

## Base URL

```
Production: https://api.yourdomain.com
Development: http://localhost:8000
```

## Authentication

All requests to `/deploy` endpoint require authentication via a secret code.

**Method**: Secret-based authentication  
**Location**: Request body  
**Parameter**: `secret`

Example:

```json
{
  "secret": "your_secret_code",
  ...
}
```

## Endpoints

### Health Check

Check if the API is running.

**Endpoint**: `GET /`  
**Authentication**: None  
**Rate Limit**: None

#### Request

```bash
curl http://localhost:8000/
```

#### Response

**Status**: `200 OK`

```json
{
  "status": "ok",
  "message": "Automated GitHub Pages Deployment API"
}
```

---

### Deploy Task

Create or update a GitHub repository with AI-generated code.

**Endpoint**: `POST /deploy`  
**Authentication**: Required (secret)  
**Rate Limit**: 10 requests/minute per IP  
**Timeout**: 300 seconds

#### Request Body

```json
{
  "email": "string (required)",
  "secret": "string (required)",
  "task": "string (required)",
  "round": "integer (1 or 2, required)",
  "nonce": "string (required)",
  "brief": "string (required)",
  "checks": "array of strings (required)",
  "evaluation_url": "string (required, valid URL)",
  "attachments": "array of attachment objects (optional)"
}
```

##### Field Descriptions

| Field            | Type    | Required | Description                               |
| ---------------- | ------- | -------- | ----------------------------------------- |
| `email`          | string  | Yes      | User's email address                      |
| `secret`         | string  | Yes      | Authentication secret code                |
| `task`           | string  | Yes      | Unique task identifier                    |
| `round`          | integer | Yes      | Round number (1 for create, 2 for update) |
| `nonce`          | string  | Yes      | Unique request identifier                 |
| `brief`          | string  | Yes      | Description of what to build              |
| `checks`         | array   | Yes      | List of requirements/checks               |
| `evaluation_url` | string  | Yes      | URL to receive deployment notification    |
| `attachments`    | array   | No       | Files as data URIs                        |

##### Attachment Object

```json
{
  "name": "string (filename with extension)",
  "url": "string (data URI format)"
}
```

**Data URI Format**: `data:<mime-type>;base64,<encoded-data>`

Example:

```json
{
  "name": "sample.png",
  "url": "data:image/png;base64,iVBORw0KGgoAAAANSUh..."
}
```

#### Round 1: Initial Deployment

Creates a new GitHub repository with generated code.

**Example Request**

```bash
curl -X POST http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer@example.com",
    "secret": "your_secret_code",
    "task": "weather-dashboard-v1",
    "round": 1,
    "nonce": "req-001",
    "brief": "Create a weather dashboard that displays current weather for a city",
    "checks": [
      "Has MIT license",
      "Professional README.md",
      "Displays weather data",
      "Accepts city parameter"
    ],
    "evaluation_url": "https://example.com/callback",
    "attachments": []
  }'
```

**Example Response**

**Status**: `200 OK`

```json
{
  "status": "success",
  "message": "Repository created and deployed",
  "repo_url": "https://github.com/username/weather-dashboard-v1-1697500000",
  "pages_url": "https://username.github.io/weather-dashboard-v1-1697500000/",
  "commit_sha": "abc123def456..."
}
```

#### Round 2: Update Deployment

Updates an existing repository (must complete Round 1 first).

**Example Request**

```bash
curl -X POST http://localhost:8000/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "email": "developer@example.com",
    "secret": "your_secret_code",
    "task": "weather-dashboard-v1",
    "round": 2,
    "nonce": "req-002",
    "brief": "Add forecast for next 7 days and temperature chart",
    "checks": [
      "Shows 7-day forecast",
      "Temperature chart displayed",
      "Updated README"
    ],
    "evaluation_url": "https://example.com/callback",
    "attachments": []
  }'
```

**Example Response**

**Status**: `200 OK`

```json
{
  "status": "success",
  "message": "Repository updated",
  "repo_url": "https://github.com/username/weather-dashboard-v1-1697500000",
  "pages_url": "https://username.github.io/weather-dashboard-v1-1697500000/",
  "commit_sha": "def789ghi012..."
}
```

#### Error Responses

**Invalid Secret**

**Status**: `403 Forbidden`

```json
{
  "detail": "Invalid secret code"
}
```

**Server Configuration Error**

**Status**: `500 Internal Server Error`

```json
{
  "detail": "Server configuration incomplete"
}
```

**Round 2 Without Round 1**

**Status**: `404 Not Found`

```json
{
  "detail": "Repository not found. Must complete round 1 first."
}
```

**Validation Error**

**Status**: `422 Unprocessable Entity`

```json
{
  "detail": [
    {
      "loc": ["body", "round"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

**Server Error**

**Status**: `500 Internal Server Error`

```json
{
  "detail": "Error processing request: <error message>"
}
```

## Evaluation Callback

After processing, the API automatically sends a POST request to `evaluation_url`.

**Callback Request**

```json
{
  "email": "developer@example.com",
  "task": "weather-dashboard-v1",
  "round": 1,
  "nonce": "req-001",
  "repo_url": "https://github.com/username/weather-dashboard-v1-1697500000",
  "commit_sha": "abc123def456...",
  "pages_url": "https://username.github.io/weather-dashboard-v1-1697500000/"
}
```

**Headers**:

```
Content-Type: application/json
```

**Expected Response**: `200 OK` (any body)

## Generated Repository Structure

Each generated repository includes:

```
repository-name/
├── index.html       # Main application (HTML + CSS + JS)
├── README.md        # Professional documentation
└── LICENSE          # MIT License
```

### Generated Files

#### index.html

- Complete, self-contained web application
- Embedded CSS and JavaScript
- No external dependencies
- Responsive design
- Handles URL parameters as specified

#### README.md

Includes:

- Project summary
- Features list
- Setup instructions
- Usage guide
- Code explanation
- License information

#### LICENSE

- MIT License
- Current year
- Ready for public repositories

## Rate Limiting

| Endpoint  | Rate Limit        | Burst |
| --------- | ----------------- | ----- |
| `/`       | Unlimited         | -     |
| `/deploy` | 10 req/min per IP | 5     |

**Response when rate limited**:

**Status**: `429 Too Many Requests`

```json
{
  "detail": "Rate limit exceeded"
}
```

## Timeouts

- **Connection timeout**: 30 seconds
- **Read timeout**: 300 seconds (5 minutes)
- **Write timeout**: 300 seconds

Long timeouts are necessary for:

- OpenAI API code generation (10-30 seconds)
- GitHub repository creation (5-15 seconds)
- GitHub Pages deployment (2-10 seconds)

## Best Practices

### Request Design

1. **Use unique task names**: Include version or iteration

   ```
   ✓ task-name-v1
   ✓ task-name-2024-10-17
   ✗ task-name (may cause conflicts)
   ```

2. **Provide detailed briefs**: More context = better results

   ```
   ✓ "Create a calculator with basic operations (+, -, *, /) and memory functions"
   ✗ "Make a calculator"
   ```

3. **List specific checks**: Clear requirements help AI generation

   ```
   ✓ "Button has hover effect with color change"
   ✗ "Button looks good"
   ```

4. **Use meaningful nonces**: Help with tracking and debugging
   ```
   ✓ "user123-task-round1-20241017"
   ✗ "123"
   ```

### Error Handling

```python
import requests
import time

def deploy_with_retry(data, max_retries=3):
    """Deploy with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://localhost:8000/deploy",
                json=data,
                timeout=300
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limited
                time.sleep(60)  # Wait 1 minute
                continue
            raise
```

### Monitoring Deployments

```python
def check_pages_status(pages_url, max_attempts=10):
    """Check if GitHub Pages is accessible."""
    import time
    for attempt in range(max_attempts):
        try:
            response = requests.get(pages_url, timeout=10)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(30)  # Wait 30 seconds between checks
    return False
```

## SDK Examples

### Python

```python
import requests

class DeploymentAPI:
    def __init__(self, base_url, secret):
        self.base_url = base_url
        self.secret = secret

    def deploy(self, email, task, round_num, nonce, brief, checks,
               evaluation_url, attachments=None):
        """Deploy a task."""
        data = {
            "email": email,
            "secret": self.secret,
            "task": task,
            "round": round_num,
            "nonce": nonce,
            "brief": brief,
            "checks": checks,
            "evaluation_url": evaluation_url,
            "attachments": attachments or []
        }

        response = requests.post(
            f"{self.base_url}/deploy",
            json=data,
            timeout=300
        )
        response.raise_for_status()
        return response.json()

# Usage
api = DeploymentAPI("http://localhost:8000", "your_secret")
result = api.deploy(
    email="dev@example.com",
    task="my-app",
    round_num=1,
    nonce="req-001",
    brief="Create a todo list app",
    checks=["Has add functionality", "Has delete functionality"],
    evaluation_url="https://example.com/callback"
)
print(f"Deployed to: {result['pages_url']}")
```

### JavaScript

```javascript
class DeploymentAPI {
  constructor(baseUrl, secret) {
    this.baseUrl = baseUrl;
    this.secret = secret;
  }

  async deploy({
    email,
    task,
    round,
    nonce,
    brief,
    checks,
    evaluationUrl,
    attachments = [],
  }) {
    const response = await fetch(`${this.baseUrl}/deploy`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        secret: this.secret,
        task,
        round,
        nonce,
        brief,
        checks,
        evaluation_url: evaluationUrl,
        attachments,
      }),
    });

    if (!response.ok) {
      throw new Error(`Deployment failed: ${response.statusText}`);
    }

    return await response.json();
  }
}

// Usage
const api = new DeploymentAPI("http://localhost:8000", "your_secret");
const result = await api.deploy({
  email: "dev@example.com",
  task: "my-app",
  round: 1,
  nonce: "req-001",
  brief: "Create a todo list app",
  checks: ["Has add functionality", "Has delete functionality"],
  evaluationUrl: "https://example.com/callback",
});
console.log(`Deployed to: ${result.pages_url}`);
```

### cURL

```bash
#!/bin/bash

API_URL="http://localhost:8000"
SECRET="your_secret_code"

# Round 1
curl -X POST "$API_URL/deploy" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"dev@example.com\",
    \"secret\": \"$SECRET\",
    \"task\": \"my-app\",
    \"round\": 1,
    \"nonce\": \"req-001\",
    \"brief\": \"Create a todo list app\",
    \"checks\": [\"Has add functionality\", \"Has delete functionality\"],
    \"evaluation_url\": \"https://example.com/callback\",
    \"attachments\": []
  }"
```

## Webhook Setup

To receive evaluation callbacks, your server must:

1. Accept POST requests
2. Handle JSON body
3. Return 200 OK status

**Example Express.js server**:

```javascript
const express = require("express");
const app = express();

app.use(express.json());

app.post("/callback", (req, res) => {
  const { email, task, round, nonce, repo_url, commit_sha, pages_url } =
    req.body;

  console.log(`Deployment complete for ${task} (Round ${round})`);
  console.log(`Repository: ${repo_url}`);
  console.log(`Pages: ${pages_url}`);

  // Process the deployment...

  res.status(200).json({ status: "received" });
});

app.listen(3000, () => console.log("Callback server running on port 3000"));
```

## Testing

### Postman Collection

Import this JSON into Postman:

```json
{
  "info": {
    "name": "Deployment API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/"
      }
    },
    {
      "name": "Deploy Round 1",
      "request": {
        "method": "POST",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "url": "{{base_url}}/deploy",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"email\": \"{{email}}\",\n  \"secret\": \"{{secret}}\",\n  \"task\": \"test-app\",\n  \"round\": 1,\n  \"nonce\": \"test-001\",\n  \"brief\": \"Create a simple hello world page\",\n  \"checks\": [\"Has index.html\"],\n  \"evaluation_url\": \"https://httpbin.org/post\",\n  \"attachments\": []\n}"
        }
      }
    }
  ],
  "variable": [
    { "key": "base_url", "value": "http://localhost:8000" },
    { "key": "secret", "value": "your_secret_here" },
    { "key": "email", "value": "test@example.com" }
  ]
}
```

## Support

For issues or questions:

- GitHub Issues: https://github.com/yourusername/TDS/issues
- Email: support@yourdomain.com

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

This API is licensed under the MIT License. See [LICENSE](LICENSE) for details.
