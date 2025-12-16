#!/usr/bin/env python3
"""
LinkedIn MCP Server (Session Cookie Version)
Provides LinkedIn functionality to Claude Desktop using session cookies
No LinkedIn Developer app required!
"""

import asyncio
import json
import os
from typing import Any
import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

class LinkedInMCPServer:
    def __init__(self):
        self.server = Server("linkedin-mcp-server")
        self.li_at_cookie = os.getenv("LINKEDIN_SESSION_COOKIE")
        self.session = None
        
        # Register handlers
        self.server.list_tools()(self.list_tools)
        self.server.call_tool()(self.call_tool)
    
    async def list_tools(self) -> list[Tool]:
        """List available LinkedIn tools"""
        return [
            Tool(
                name="get_my_profile",
                description="Get your LinkedIn profile information including name, headline, summary, experience, education, and skills",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="get_profile_by_url",
                description="Get information from any LinkedIn profile by its URL (e.g., linkedin.com/in/username)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "profile_url": {
                            "type": "string",
                            "description": "Full LinkedIn profile URL or username (e.g., 'linkedin.com/in/johndoe' or 'johndoe')"
                        }
                    },
                    "required": ["profile_url"]
                }
            ),
            Tool(
                name="search_profiles",
                description="Search for LinkedIn profiles by name, title, company, or keywords",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (name, job title, company, keywords)"
                        },
                        "limit": {
                            "type": "number",
                            "description": "Number of results to return (default: 10)",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="search_jobs",
                description="Search for job postings on LinkedIn",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "keywords": {
                            "type": "string",
                            "description": "Job search keywords (e.g., 'software engineer', 'data analyst')"
                        },
                        "location": {
                            "type": "string",
                            "description": "Location for job search (e.g., 'San Francisco', 'Remote')",
                            "default": ""
                        },
                        "limit": {
                            "type": "number",
                            "description": "Number of results (default: 10)",
                            "default": 10
                        }
                    },
                    "required": ["keywords"]
                }
            ),
            Tool(
                name="get_my_connections",
                description="Get a list of your LinkedIn connections",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "number",
                            "description": "Number of connections to retrieve (default: 20)",
                            "default": 20
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="get_feed",
                description="Get recent posts from your LinkedIn feed",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "number",
                            "description": "Number of posts to retrieve (default: 10)",
                            "default": 10
                        }
                    },
                    "required": []
                }
            )
        ]
    
    async def call_tool(self, name: str, arguments: Any) -> list[TextContent]:
        """Handle tool calls"""
        if not self.li_at_cookie:
            return [TextContent(
                type="text",
                text="Error: LINKEDIN_SESSION_COOKIE environment variable not set. Please configure your LinkedIn session cookie."
            )]
        
        try:
            if name == "get_my_profile":
                result = await self.get_my_profile()
            elif name == "get_profile_by_url":
                profile_url = arguments["profile_url"]
                result = await self.get_profile_by_url(profile_url)
            elif name == "search_profiles":
                query = arguments["query"]
                limit = arguments.get("limit", 10)
                result = await self.search_profiles(query, limit)
            elif name == "search_jobs":
                keywords = arguments["keywords"]
                location = arguments.get("location", "")
                limit = arguments.get("limit", 10)
                result = await self.search_jobs(keywords, location, limit)
            elif name == "get_my_connections":
                limit = arguments.get("limit", 20)
                result = await self.get_my_connections(limit)
            elif name == "get_feed":
                limit = arguments.get("limit", 10)
                result = await self.get_feed(limit)
            else:
                result = f"Unknown tool: {name}"
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}\n\nMake sure your LinkedIn session cookie is valid and not expired.")]
    
    async def get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with LinkedIn cookies"""
        if self.session is None:
            self.session = httpx.AsyncClient(
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                    "Accept": "application/json",
                    "Accept-Language": "en-US,en;q=0.9",
                    "csrf-token": "ajax:8234567890123456789",
                },
                cookies={
                    "li_at": self.li_at_cookie,
                },
                timeout=30.0,
                follow_redirects=True
            )
        return self.session
    
    async def get_my_profile(self) -> dict:
        """Get the authenticated user's profile"""
        client = await self.get_http_client()
        
        # Get basic profile info
        response = await client.get(
            "https://www.linkedin.com/voyager/api/me"
        )
        response.raise_for_status()
        data = response.json()
        
        # Extract relevant information
        profile = {
            "name": f"{data.get('firstName', '')} {data.get('lastName', '')}",
            "headline": data.get('headline', ''),
            "publicIdentifier": data.get('publicIdentifier', ''),
            "profile_url": f"https://www.linkedin.com/in/{data.get('publicIdentifier', '')}",
        }
        
        # Get detailed profile
        username = data.get('publicIdentifier')
        if username:
            detailed = await self.get_profile_by_url(username)
            profile.update(detailed)
        
        return profile
    
    async def get_profile_by_url(self, profile_url: str) -> dict:
        """Get profile information by URL or username"""
        client = await self.get_http_client()
        
        # Extract username from URL if full URL provided
        username = profile_url.split('/')[-1].split('?')[0]
        if 'linkedin.com' not in username:
            username = profile_url
        
        # Get profile data
        response = await client.get(
            f"https://www.linkedin.com/voyager/api/identity/profiles/{username}/profileView"
        )
        response.raise_for_status()
        data = response.json()
        
        # Parse profile data
        profile_data = data.get('profile', {})
        
        profile = {
            "name": f"{profile_data.get('firstName', '')} {profile_data.get('lastName', '')}",
            "headline": profile_data.get('headline', ''),
            "summary": profile_data.get('summary', ''),
            "location": profile_data.get('locationName', ''),
            "industry": profile_data.get('industryName', ''),
            "profile_url": f"https://www.linkedin.com/in/{username}",
            "experience": [],
            "education": [],
            "skills": []
        }
        
        # Extract experience
        positions = data.get('positionView', {}).get('elements', [])
        for pos in positions:
            experience = {
                "title": pos.get('title', ''),
                "company": pos.get('companyName', ''),
                "description": pos.get('description', ''),
                "location": pos.get('locationName', ''),
            }
            # Parse dates if available
            if 'timePeriod' in pos:
                time_period = pos['timePeriod']
                if 'startDate' in time_period:
                    start = time_period['startDate']
                    experience["start_date"] = f"{start.get('month', '')}/{start.get('year', '')}"
                if 'endDate' in time_period:
                    end = time_period['endDate']
                    experience["end_date"] = f"{end.get('month', '')}/{end.get('year', '')}"
            
            profile["experience"].append(experience)
        
        # Extract education
        schools = data.get('educationView', {}).get('elements', [])
        for school in schools:
            education = {
                "school": school.get('schoolName', ''),
                "degree": school.get('degreeName', ''),
                "field": school.get('fieldOfStudy', ''),
            }
            profile["education"].append(education)
        
        # Extract skills
        skills = data.get('skillView', {}).get('elements', [])
        for skill in skills[:10]:  # Top 10 skills
            profile["skills"].append(skill.get('name', ''))
        
        return profile
    
    async def search_profiles(self, query: str, limit: int = 10) -> dict:
        """Search for profiles"""
        client = await self.get_http_client()
        
        response = await client.get(
            "https://www.linkedin.com/voyager/api/search/blended",
            params={
                "keywords": query,
                "filters": "List(resultType->PEOPLE)",
                "queryContext": "List(spellCorrectionEnabled->true)",
                "count": limit
            }
        )
        response.raise_for_status()
        data = response.json()
        
        results = []
        elements = data.get('elements', [])
        
        for element in elements:
            profile = element.get('hitInfo', {}).get('*profile', {})
            results.append({
                "name": f"{profile.get('firstName', '')} {profile.get('lastName', '')}",
                "headline": profile.get('headline', ''),
                "location": profile.get('geoLocationName', ''),
                "public_id": profile.get('publicIdentifier', ''),
                "profile_url": f"https://www.linkedin.com/in/{profile.get('publicIdentifier', '')}"
            })
        
        return {"count": len(results), "results": results}
    
    async def search_jobs(self, keywords: str, location: str = "", limit: int = 10) -> dict:
        """Search for job postings"""
        client = await self.get_http_client()
        
        params = {
            "keywords": keywords,
            "count": limit,
        }
        if location:
            params["location"] = location
        
        response = await client.get(
            "https://www.linkedin.com/voyager/api/search/blended",
            params={
                **params,
                "filters": "List(resultType->JOBS)",
                "queryContext": "List(spellCorrectionEnabled->true)"
            }
        )
        response.raise_for_status()
        data = response.json()
        
        jobs = []
        elements = data.get('elements', [])
        
        for element in elements:
            job = element.get('hitInfo', {}).get('*jobPosting', {})
            jobs.append({
                "title": job.get('title', ''),
                "company": job.get('companyName', ''),
                "location": job.get('formattedLocation', ''),
                "job_url": f"https://www.linkedin.com/jobs/view/{job.get('jobPostingId', '')}",
                "posted": job.get('listedAt', '')
            })
        
        return {"count": len(jobs), "jobs": jobs}
    
    async def get_my_connections(self, limit: int = 20) -> dict:
        """Get user's connections"""
        client = await self.get_http_client()
        
        response = await client.get(
            "https://www.linkedin.com/voyager/api/relationships/connections",
            params={"count": limit}
        )
        response.raise_for_status()
        data = response.json()
        
        connections = []
        elements = data.get('elements', [])
        
        for element in elements:
            conn = element.get('connectedMember', {})
            connections.append({
                "name": f"{conn.get('firstName', '')} {conn.get('lastName', '')}",
                "headline": conn.get('headline', ''),
                "profile_url": f"https://www.linkedin.com/in/{conn.get('publicIdentifier', '')}"
            })
        
        return {"count": len(connections), "connections": connections}
    
    async def get_feed(self, limit: int = 10) -> dict:
        """Get LinkedIn feed posts"""
        client = await self.get_http_client()
        
        response = await client.get(
            "https://www.linkedin.com/voyager/api/feed/updates",
            params={"count": limit}
        )
        response.raise_for_status()
        data = response.json()
        
        posts = []
        elements = data.get('elements', [])
        
        for element in elements[:limit]:
            post = {
                "text": "",
                "author": "",
                "timestamp": ""
            }
            
            # Extract post content
            if 'value' in element:
                value = element['value']
                if 'com.linkedin.voyager.feed.render.UpdateV2' in value:
                    update = value['com.linkedin.voyager.feed.render.UpdateV2']
                    commentary = update.get('commentary', {})
                    post["text"] = commentary.get('text', {}).get('text', '')
            
            posts.append(post)
        
        return {"count": len(posts), "posts": posts}
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.aclose()

async def main():
    """Main entry point"""
    server_instance = LinkedInMCPServer()
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server_instance.server.run(
                read_stream,
                write_stream,
                server_instance.server.create_initialization_options()
            )
    finally:
        await server_instance.cleanup()

if __name__ == "__main__":
    asyncio.run(main())