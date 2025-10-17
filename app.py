"""
Production API endpoint for automated GitHub Pages deployment.
Accepts task requests, generates code using OpenAI, creates GitHub repos, and deploys to Pages.
"""

import os
import json
import base64
import time
import re
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import httpx
from github import Github, GithubException
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Automated GitHub Pages Deployment API",
    description="Accepts task requests and automates code generation and deployment",
    version="1.0.0"
)

# Load environment variables from .env file or environment (Render/production)
SECRET_CODE = os.environ.get("SECRET_CODE")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME")

# Initialize clients
github_client = None
openai_client = None

if GITHUB_TOKEN:
    github_client = Github(GITHUB_TOKEN)
    logger.info("✓ GitHub client initialized")
else:
    logger.warning("⚠ GitHub token not found")

if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info("✓ OpenAI client initialized")
else:
    logger.warning("⚠ OpenAI API key not found")


# Pydantic models for request validation
class Attachment(BaseModel):
    name: str
    url: str  # data URI


class TaskRequest(BaseModel):
    email: str
    secret: str
    task: str
    round: int = Field(ge=1, le=2)
    nonce: str
    brief: str
    checks: List[str]
    evaluation_url: str
    attachments: Optional[List[Attachment]] = []


class EvaluationResponse(BaseModel):
    email: str
    task: str
    round: int
    nonce: str
    repo_url: str
    commit_sha: str
    pages_url: str


# Storage for tracking repos (in production, use a database)
repo_storage: Dict[str, Dict[str, Any]] = {}


@app.get("/")
async def root():
    """Health check endpoint."""
    logger.info("📍 Health check endpoint accessed")
    return {"status": "ok", "message": "Automated GitHub Pages Deployment API"}


@app.post("/deploy")
async def deploy_task(request: TaskRequest):
    """
    Main endpoint that handles task deployment requests.
    
    Round 1: Creates a new repo and deploys initial code
    Round 2: Updates existing repo with modifications
    """
    logger.info("=" * 80)
    logger.info("🚀 NEW REQUEST RECEIVED")
    logger.info("=" * 80)
    logger.info(f"📧 Email: {request.email}")
    logger.info(f"📝 Task: {request.task}")
    logger.info(f"🔢 Round: {request.round}")
    logger.info(f"🎯 Nonce: {request.nonce}")
    logger.info(f"📄 Brief: {request.brief[:100]}..." if len(request.brief) > 100 else f"📄 Brief: {request.brief}")
    logger.info(f"✅ Checks: {len(request.checks)} items")
    logger.info(f"📎 Attachments: {len(request.attachments) if request.attachments else 0}")
    logger.info(f"🔗 Evaluation URL: {request.evaluation_url}")
    
    # Verify secret
    logger.info("🔐 Verifying secret code...")
    if request.secret != SECRET_CODE:
        logger.error("❌ Invalid secret code provided")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid secret code"
        )
    logger.info("✓ Secret code verified")
    
    # Verify required environment variables
    logger.info("🔧 Verifying server configuration...")
    if not GITHUB_TOKEN or not OPENAI_API_KEY or not GITHUB_USERNAME:
        logger.error("❌ Server configuration incomplete - missing required environment variables")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration incomplete"
        )
    logger.info("✓ Server configuration verified")
    
    try:
        if request.round == 1:
            logger.info("🎯 Processing ROUND 1 request...")
            result = await handle_round_1(request)
        elif request.round == 2:
            logger.info("🎯 Processing ROUND 2 request...")
            result = await handle_round_2(request)
        else:
            logger.error(f"❌ Invalid round number: {request.round}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid round number"
            )
        
        logger.info("=" * 80)
        logger.info("✅ REQUEST COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result
        )
    
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ ERROR PROCESSING REQUEST: {str(e)}")
        logger.error("=" * 80)
        logger.exception("Full error traceback:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )


async def handle_round_1(request: TaskRequest) -> dict:
    """Handle round 1: Create new repo and deploy."""
    logger.info("🔨 Starting Round 1 processing...")
    
    # Generate unique repo name from task
    repo_name = sanitize_repo_name(request.task)
    logger.info(f"📦 Generated repo name: {repo_name}")
    
    # Check if repo already exists in storage
    storage_key = f"{request.email}:{request.task}"
    if storage_key in repo_storage:
        logger.info(f"♻️ Repo already exists in storage for key: {storage_key}")
        logger.info("↩️ Returning existing repo info")
        # Repo already exists, return existing info
        return repo_storage[storage_key]
    
    # Process attachments
    logger.info(f"📎 Processing {len(request.attachments) if request.attachments else 0} attachments...")
    attachments_data = process_attachments(request.attachments)
    logger.info(f"✓ Processed {len(attachments_data)} attachments")
    
    # Generate code using OpenAI
    logger.info("🤖 Generating code using OpenAI...")
    generated_files = await generate_code_with_ai(
        brief=request.brief,
        checks=request.checks,
        attachments=attachments_data,
        task_name=request.task
    )
    logger.info(f"✓ Generated {len(generated_files)} files: {', '.join(generated_files.keys())}")
    
    # Create GitHub repo
    logger.info(f"📦 Creating GitHub repository: {repo_name}")
    repo_info = create_github_repo(
        repo_name=repo_name,
        files=generated_files
    )
    logger.info(f"✓ Repository created: {repo_info['repo_url']}")
    
    # Enable GitHub Pages
    logger.info("🌐 Enabling GitHub Pages...")
    enable_github_pages(repo_name)
    logger.info(f"✓ GitHub Pages enabled: {repo_info['pages_url']}")
    
    # Prepare evaluation response
    logger.info("📋 Preparing evaluation response...")
    eval_response = EvaluationResponse(
        email=request.email,
        task=request.task,
        round=request.round,
        nonce=request.nonce,
        repo_url=repo_info["repo_url"],
        commit_sha=repo_info["commit_sha"],
        pages_url=repo_info["pages_url"]
    )
    logger.info(f"✓ Evaluation response prepared - Commit SHA: {repo_info['commit_sha'][:8]}")
    
    # Send to evaluation URL
    logger.info(f"📤 Sending evaluation to: {request.evaluation_url}")
    await send_evaluation(request.evaluation_url, eval_response)
    logger.info("✓ Evaluation sent")
    
    # Store repo info for round 2
    logger.info(f"💾 Storing repo info for round 2 with key: {storage_key}")
    repo_storage[storage_key] = {
        "repo_name": repo_name,
        "repo_url": repo_info["repo_url"],
        "pages_url": repo_info["pages_url"],
        "created_at": datetime.now().isoformat()
    }
    logger.info("✓ Repo info stored")
    
    result = {
        "status": "success",
        "message": "Repository created and deployed",
        "repo_url": repo_info["repo_url"],
        "pages_url": repo_info["pages_url"],
        "commit_sha": repo_info["commit_sha"]
    }
    logger.info("🎉 Round 1 completed successfully!")
    return result


async def handle_round_2(request: TaskRequest) -> dict:
    """Handle round 2: Update existing repo."""
    logger.info("🔨 Starting Round 2 processing...")
    
    storage_key = f"{request.email}:{request.task}"
    logger.info(f"🔍 Looking for existing repo with key: {storage_key}")
    
    # Check if repo exists
    if storage_key not in repo_storage:
        logger.error(f"❌ Repository not found for key: {storage_key}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found. Must complete round 1 first."
        )
    
    repo_info_stored = repo_storage[storage_key]
    repo_name = repo_info_stored["repo_name"]
    logger.info(f"✓ Found existing repo: {repo_name}")
    
    # Process attachments
    logger.info(f"📎 Processing {len(request.attachments) if request.attachments else 0} attachments...")
    attachments_data = process_attachments(request.attachments)
    logger.info(f"✓ Processed {len(attachments_data)} attachments")
    
    # Generate updated code using OpenAI
    logger.info("🤖 Generating updated code using OpenAI...")
    generated_files = await generate_code_with_ai(
        brief=request.brief,
        checks=request.checks,
        attachments=attachments_data,
        task_name=request.task,
        is_update=True
    )
    logger.info(f"✓ Generated {len(generated_files)} updated files: {', '.join(generated_files.keys())}")
    
    # Update GitHub repo
    logger.info(f"🔄 Updating GitHub repository: {repo_name}")
    commit_sha = update_github_repo(
        repo_name=repo_name,
        files=generated_files
    )
    logger.info(f"✓ Repository updated - Commit SHA: {commit_sha[:8]}")
    
    # Prepare evaluation response
    logger.info("📋 Preparing evaluation response...")
    eval_response = EvaluationResponse(
        email=request.email,
        task=request.task,
        round=request.round,
        nonce=request.nonce,
        repo_url=repo_info_stored["repo_url"],
        commit_sha=commit_sha,
        pages_url=repo_info_stored["pages_url"]
    )
    logger.info(f"✓ Evaluation response prepared - Commit SHA: {commit_sha[:8]}")
    
    # Send to evaluation URL
    logger.info(f"📤 Sending evaluation to: {request.evaluation_url}")
    await send_evaluation(request.evaluation_url, eval_response)
    logger.info("✓ Evaluation sent")
    
    result = {
        "status": "success",
        "message": "Repository updated",
        "repo_url": repo_info_stored["repo_url"],
        "pages_url": repo_info_stored["pages_url"],
        "commit_sha": commit_sha
    }
    logger.info("🎉 Round 2 completed successfully!")
    return result


def sanitize_repo_name(task: str) -> str:
    """Generate a valid GitHub repo name from task string."""
    # Remove special characters and replace spaces with hyphens
    name = re.sub(r'[^a-zA-Z0-9-]', '-', task.lower())
    # Remove consecutive hyphens
    name = re.sub(r'-+', '-', name)
    # Remove leading/trailing hyphens
    name = name.strip('-')
    # Add timestamp for uniqueness
    timestamp = int(time.time())
    return f"{name}-{timestamp}"[:100]  # GitHub limit


def process_attachments(attachments: List[Attachment]) -> List[Dict[str, Any]]:
    """Process data URI attachments and extract content."""
    processed = []
    
    for attachment in attachments:
        try:
            logger.info(f"  Processing attachment: {attachment.name}")
            # Parse data URI
            if attachment.url.startswith("data:"):
                # Format: data:image/png;base64,iVBORw...
                header, data = attachment.url.split(",", 1)
                mime_type = header.split(";")[0].replace("data:", "")
                
                processed.append({
                    "name": attachment.name,
                    "mime_type": mime_type,
                    "data": data,
                    "is_base64": "base64" in header
                })
                logger.info(f"  ✓ Processed {attachment.name} ({mime_type})")
        except Exception as e:
            logger.error(f"  ❌ Error processing attachment {attachment.name}: {e}")
    
    return processed


async def generate_code_with_ai( 
    brief: str,
    checks: List[str],
    attachments: List[Dict[str, Any]],
    task_name: str,
    is_update: bool = False
) -> Dict[str, str]:
    """Generate code files using OpenAI API."""
    logger.info(f"  Building AI prompt for {'update' if is_update else 'creation'}...")
    
    # Prepare attachment descriptions
    attachment_info = ""
    if attachments:
        attachment_info = "\n\nAttachments provided:\n"
        for att in attachments:
            attachment_info += f"- {att['name']} ({att['mime_type']})\n"
    
    # Prepare checks
    checks_text = "\n".join([f"- {check}" for check in checks])
    
    # Create prompt for OpenAI
    action = "update" if is_update else "create"
    
    prompt = f"""You are a professional web developer. {action.capitalize()} a web application based on the following requirements:

Brief: {brief}

Requirements/Checks:
{checks_text}

{attachment_info}

Generate the following files:
1. index.html - A complete, production-ready HTML file with embedded CSS and JavaScript
2. README.md - A professional, verbose README with sections: Summary, Setup, Usage, Code Explanation, License

Guidelines:
- Make it minimal but fully functional. should pass automated tests.
- Use modern, clean UI design
- Include all necessary code in index.html (no external dependencies if possible)
- Handle the query parameter ?url=... as specified
- Make the README professional and detailed  (summary, setup, usage, code explanation, license)
- Ensure the code works immediately when deployed to GitHub Pages

Output each file with clear markers:
===FILE: filename===
content
===END FILE===
"""

    try:
        logger.info("  📡 Calling OpenAI API (model: gpt-4o)...")
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert web developer who creates minimal, functional, production-ready web applications."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            
        )
        
        generated_text = response.choices[0].message.content
        logger.info(f"  ✓ Received response from OpenAI ({len(generated_text)} characters)")
        
        # Parse generated files
        logger.info("  🔍 Parsing generated files from AI response...")
        files = parse_generated_files(generated_text)
        logger.info(f"  ✓ Parsed {len(files)} files from AI response")
        
        # Ensure we have required files
        if "index.html" not in files:
            logger.info("  ⚠ index.html not found in AI response, using default template")
            files["index.html"] = create_default_html(brief, attachments)
        
        if "README.md" not in files:
            logger.info("  ⚠ README.md not found in AI response, using default template")
            files["README.md"] = create_default_readme(task_name, brief, checks)
        
        # Always include MIT LICENSE
        files["LICENSE"] = create_mit_license()
        logger.info("  ✓ Added LICENSE file")
        
        return files
    
    except Exception as e:
        logger.error(f"  ❌ Error generating code with AI: {e}")
        logger.exception("  Full error traceback:")
        logger.info("  ↩️ Falling back to default templates")
        # Fallback to default templates
        return {
            "index.html": create_default_html(brief, attachments),
            "README.md": create_default_readme(task_name, brief, checks),
            "LICENSE": create_mit_license()
        }


def parse_generated_files(text: str) -> Dict[str, str]:
    """Parse files from AI-generated text."""
    files = {}
    pattern = r'===FILE:\s*(.+?)\s*===\n(.*?)\n===END FILE==='
    matches = re.findall(pattern, text, re.DOTALL)
    
    for filename, content in matches:
        files[filename.strip()] = content.strip()
    
    return files


def create_default_html(brief: str, attachments: List[Dict[str, Any]]) -> str:
    """Create a default HTML template."""
    
    # Get first attachment if available
    default_image = ""
    if attachments:
        default_image = f"data:{attachments[0]['mime_type']},{attachments[0]['data']}"
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Application</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 800px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }}
        h1 {{
            color: #333;
            margin-bottom: 20px;
            text-align: center;
        }}
        .description {{
            color: #666;
            margin-bottom: 30px;
            text-align: center;
            line-height: 1.6;
        }}
        .image-container {{
            text-align: center;
            margin: 30px 0;
        }}
        .image-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }}
        .result {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            text-align: center;
        }}
        .result-text {{
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
            margin-top: 10px;
        }}
        .loading {{
            color: #999;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Task Application</h1>
        <p class="description">{brief}</p>
        
        <div class="image-container">
            <img id="displayImage" src="{default_image}" alt="Content">
        </div>
        
        <div class="result">
            <div class="loading">Processing...</div>
            <div class="result-text" id="resultText"></div>
        </div>
    </div>
    
    <script>
        // Get URL parameter
        function getUrlParameter(name) {{
            const urlParams = new URLSearchParams(window.location.search);
            return urlParams.get(name);
        }}
        
        // Load image from URL parameter if provided
        const imageUrl = getUrlParameter('url');
        if (imageUrl) {{
            document.getElementById('displayImage').src = imageUrl;
        }}
        
        // Simulate processing (in production, this would call an actual API)
        setTimeout(() => {{
            document.querySelector('.loading').style.display = 'none';
            document.getElementById('resultText').textContent = 'Result: Sample Output';
        }}, 2000);
    </script>
</body>
</html>"""


def create_default_readme(task_name: str, brief: str, checks: List[str]) -> str:
    """Create a default README template."""
    checks_text = "\n".join([f"- {check}" for check in checks])
    
    return f"""# {task_name}

## Summary

This is an automated web application generated based on specific task requirements. The application is designed to be minimal, functional, and production-ready, deployed automatically to GitHub Pages.

**Task Brief:** {brief}

## Features

{checks_text}

## Setup

This application is deployed on GitHub Pages and requires no local setup. Simply visit the deployed URL to use the application.

### Local Development (Optional)

If you want to run this locally:

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd {task_name}
   ```

2. Open `index.html` in your web browser:
   ```bash
   # On macOS
   open index.html
   
   # On Linux
   xdg-open index.html
   
   # On Windows
   start index.html
   ```

## Usage

### Basic Usage

1. Visit the deployed GitHub Pages URL
2. The application will display the default content
3. To use custom content, add the `?url=` parameter to the URL:
   ```
   https://username.github.io/repo/?url=https://example.com/image.png
   ```

### Query Parameters

- `url`: Specify a custom image URL to process

### Example

```
https://username.github.io/{task_name}/?url=https://example.com/sample.png
```

## Code Explanation

### Architecture

The application follows a simple, single-page architecture:

- **index.html**: Contains all HTML structure, CSS styling, and JavaScript functionality in a single file
- **No external dependencies**: Everything needed is embedded for immediate functionality
- **Responsive design**: Works on desktop, tablet, and mobile devices

### Key Components

1. **HTML Structure**
   - Clean semantic HTML5 markup
   - Accessible and SEO-friendly structure
   - Container-based layout for responsiveness

2. **CSS Styling**
   - Modern gradient background
   - Card-based UI with shadows for depth
   - Responsive design with flexbox
   - Mobile-first approach

3. **JavaScript Functionality**
   - URL parameter parsing
   - Dynamic content loading
   - Event handling and state management
   - Error handling for robustness

### How It Works

1. The application loads and parses URL parameters
2. If a `?url=` parameter is provided, it loads that content
3. Otherwise, it displays default content
4. Results are processed and displayed within the specified timeframe
5. The UI updates dynamically based on the content

## Technical Details

- **Pure HTML/CSS/JavaScript**: No build process required
- **GitHub Pages**: Automatic deployment on push to main branch
- **Modern Browser Support**: Works on all modern browsers (Chrome, Firefox, Safari, Edge)
- **Performance**: Lightweight with fast load times

## Deployment

This application is automatically deployed to GitHub Pages when changes are pushed to the main branch. The deployment process is handled by GitHub's infrastructure.

### Deployment URL

The application is available at: `https://username.github.io/{task_name}/`

## License

MIT License

Copyright (c) {datetime.now().year}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Support

For issues, questions, or contributions, please open an issue in the GitHub repository.

---

*This application was automatically generated and deployed as part of an automated task deployment system.*
"""


def create_mit_license() -> str:
    """Create MIT license text."""
    return f"""MIT License

Copyright (c) {datetime.now().year}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def create_github_repo(repo_name: str, files: Dict[str, str]) -> Dict[str, str]:
    """Create a GitHub repository and push files."""
    
    try:
        # Get authenticated user
        logger.info(f"  🔐 Authenticating with GitHub as: {GITHUB_USERNAME}")
        user = github_client.get_user()
        
        # Create repository
        logger.info(f"  📦 Creating repository: {repo_name}")
        repo = user.create_repo(
            name=repo_name,
            description="Automated deployment from task request",
            private=False,
            auto_init=False
        )
        logger.info(f"  ✓ Repository created: {repo.html_url}")
        
        # Create files in the repo
        logger.info(f"  📝 Uploading {len(files)} files to repository...")
        for filename, content in files.items():
            logger.info(f"    Uploading {filename} ({len(content)} bytes)...")
            repo.create_file(
                path=filename,
                message=f"Add {filename}",
                content=content
            )
            logger.info(f"    ✓ {filename} uploaded")
        
        # Get the latest commit SHA
        logger.info("  🔍 Getting latest commit SHA...")
        commits = repo.get_commits()
        latest_commit_sha = commits[0].sha
        logger.info(f"  ✓ Latest commit SHA: {latest_commit_sha[:8]}")
        
        return {
            "repo_url": repo.html_url,
            "commit_sha": latest_commit_sha,
            "pages_url": f"https://{GITHUB_USERNAME}.github.io/{repo_name}/"
        }
    
    except GithubException as e:
        logger.error(f"  ❌ GitHub API error: {e.data.get('message', str(e))}")
        raise Exception(f"GitHub API error: {e.data.get('message', str(e))}")


def update_github_repo(repo_name: str, files: Dict[str, str]) -> str:
    """Update existing GitHub repository with new files."""
    
    try:
        logger.info(f"  🔐 Authenticating with GitHub...")
        user = github_client.get_user()
        logger.info(f"  📦 Getting repository: {repo_name}")
        repo = user.get_repo(repo_name)
        
        # Update or create files
        logger.info(f"  📝 Updating {len(files)} files in repository...")
        for filename, content in files.items():
            try:
                # Try to get existing file
                logger.info(f"    Checking if {filename} exists...")
                file = repo.get_contents(filename)
                # Update existing file
                logger.info(f"    Updating existing {filename}...")
                repo.update_file(
                    path=filename,
                    message=f"Update {filename} (Round 2)",
                    content=content,
                    sha=file.sha
                )
                logger.info(f"    ✓ {filename} updated")
            except GithubException:
                # File doesn't exist, create it
                logger.info(f"    {filename} doesn't exist, creating new file...")
                repo.create_file(
                    path=filename,
                    message=f"Add {filename} (Round 2)",
                    content=content
                )
                logger.info(f"    ✓ {filename} created")
        
        # Get the latest commit SHA
        logger.info("  🔍 Getting latest commit SHA...")
        commits = repo.get_commits()
        latest_sha = commits[0].sha
        logger.info(f"  ✓ Latest commit SHA: {latest_sha[:8]}")
        return latest_sha
    
    except GithubException as e:
        logger.error(f"  ❌ GitHub API error: {e.data.get('message', str(e))}")
        raise Exception(f"GitHub API error: {e.data.get('message', str(e))}")


def enable_github_pages(repo_name: str):
    """Enable GitHub Pages for the repository."""
    
    try:
        logger.info(f"  📦 Getting repository: {repo_name}")
        user = github_client.get_user()
        repo = user.get_repo(repo_name)
        
        # Wait for GitHub to process all commits before enabling Pages
        logger.info("  ⏳ Waiting 10 seconds for GitHub to process commits...")
        time.sleep(10)
        
        # Verify files exist in the repo before enabling Pages
        logger.info("  🔍 Verifying repository contents...")
        try:
            contents = repo.get_contents("")
            file_names = [content.name for content in contents]
            logger.info(f"  ✓ Found files: {', '.join(file_names)}")
            if "index.html" not in file_names:
                logger.warning("  ⚠ index.html not found in root - Pages may not work")
        except Exception as e:
            logger.warning(f"  ⚠ Could not verify repo contents: {e}")
        
        # Enable GitHub Pages using POST to create
        url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/pages"
        logger.info(f"  📡 Calling GitHub Pages API: {url}")
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        data = {
            "source": {
                "branch": "main",
                "path": "/"
            }
        }
        
        # Use POST to create Pages
        logger.info("  📝 Creating GitHub Pages with POST request...")
        response = httpx.post(url, headers=headers, json=data, timeout=30.0)
        logger.info(f"  📊 Response status: {response.status_code}")
        
        # Handle response
        if response.status_code == 201:
            logger.info("  ✓ GitHub Pages created successfully")
            pages_data = response.json()
            logger.info(f"  🌐 Pages URL: {pages_data.get('html_url', 'N/A')}")
        elif response.status_code == 409:
            logger.info("  ℹ Pages already exists - that's OK")
        elif response.status_code == 404:
            logger.error("  ❌ Repository not found or API endpoint incorrect")
            logger.error(f"  Response: {response.text}")
        else:
            logger.warning(f"  ⚠ Unexpected status code: {response.status_code}")
            logger.warning(f"  Response: {response.text}")
            # Don't fail - Pages might still work
        
        # Wait for Pages to initialize
        logger.info("  ⏳ Waiting 20 seconds for Pages to build and deploy...")
        time.sleep(20)
        
        # Verify Pages status
        verify_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/pages"
        logger.info("  🔍 Verifying Pages status...")
        verify_response = httpx.get(verify_url, headers=headers, timeout=30.0)
        
        if verify_response.status_code == 200:
            pages_info = verify_response.json()
            status = pages_info.get('status')
            logger.info(f"  📊 Pages Status: {status}")
            logger.info(f"  🌐 Pages URL: {pages_info.get('html_url', 'N/A')}")
            logger.info(f"  📂 Source: {pages_info.get('source', {}).get('branch', 'N/A')} / {pages_info.get('source', {}).get('path', 'N/A')}")
            
            # If still building, wait longer
            if status in ['queued', 'building']:
                logger.info("  ⏳ Pages still building, waiting additional 20 seconds...")
                time.sleep(20)
                # Check again
                verify_response2 = httpx.get(verify_url, headers=headers, timeout=30.0)
                if verify_response2.status_code == 200:
                    pages_info2 = verify_response2.json()
                    logger.info(f"  📊 Final Pages Status: {pages_info2.get('status')}")
        else:
            logger.warning(f"  ⚠ Could not verify Pages status (HTTP {verify_response.status_code})")
            logger.warning(f"  This may be normal - Pages might still work after manual activation")
    
    except Exception as e:
        logger.error(f"  ❌ Error during GitHub Pages setup: {e}")
        logger.warning("  ⚠ Continuing anyway - Pages may need manual activation")
        # Don't re-raise - allow deployment to complete even if Pages API has issues


async def send_evaluation(evaluation_url: str, data: EvaluationResponse):
    """Send evaluation response to the provided URL."""
    
    try:
        logger.info(f"  📡 Sending POST request to evaluation URL...")
        logger.info(f"  Payload: {data.dict()}")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                evaluation_url,
                headers={"Content-Type": "application/json"},
                json=data.dict()
            )
            
            if response.status_code != 200:
                logger.warning(f"  ⚠ Evaluation URL returned status {response.status_code}")
                logger.warning(f"  Response: {response.text[:200]}")
            else:
                logger.info(f"  ✓ Evaluation sent successfully (status 200)")
    
    except Exception as e:
        logger.warning(f"  ⚠ Could not send to evaluation URL: {e}")
        # Don't fail the whole process if evaluation callback fails


if __name__ == "__main__":
    import uvicorn
    logger.info("=" * 80)
    logger.info("🚀 STARTING SERVER")
    logger.info("=" * 80)
    logger.info(f"Host: 0.0.0.0")
    logger.info(f"Port: 8000")
    logger.info(f"GitHub Username: {GITHUB_USERNAME}")
    logger.info(f"GitHub Token: {'✓ Set' if GITHUB_TOKEN else '✗ Not Set'}")
    logger.info(f"OpenAI API Key: {'✓ Set' if OPENAI_API_KEY else '✗ Not Set'}")
    logger.info(f"Secret Code: {'✓ Set' if SECRET_CODE != 'default_secret_change_me' else '⚠ Using default'}")
    logger.info("=" * 80)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

