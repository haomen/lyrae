#!/usr/bin/env python3
"""
Minimum MCP Server with OpenAI Integration
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
import openai
from mcp import ClientSession, StdioServerParameters
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
    LoggingLevel,
)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class OpenAIMCPServer:
    def __init__(self):
        self.server = Server("openai-tools")
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="chat_completion",
                        description="Send a message to OpenAI's chat completion API",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "message": {
                                    "type": "string",
                                    "description": "The message to send to OpenAI"
                                },
                                "model": {
                                    "type": "string",
                                    "description": "The OpenAI model to use (default: gpt-3.5-turbo)",
                                    "default": "gpt-3.5-turbo"
                                },
                                "max_tokens": {
                                    "type": "integer",
                                    "description": "Maximum tokens to generate",
                                    "default": 1000
                                }
                            },
                            "required": ["message"]
                        }
                    ),
                    Tool(
                        name="generate_image",
                        description="Generate an image using OpenAI's DALL-E API",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "prompt": {
                                    "type": "string",
                                    "description": "The prompt for image generation"
                                },
                                "size": {
                                    "type": "string",
                                    "description": "Image size (1024x1024, 1792x1024, 1024x1792)",
                                    "default": "1024x1024"
                                },
                                "quality": {
                                    "type": "string",
                                    "description": "Image quality (standard, hd)",
                                    "default": "standard"
                                }
                            },
                            "required": ["prompt"]
                        }
                    ),
                    Tool(
                        name="analyze_text",
                        description="Analyze text using OpenAI's API",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "text": {
                                    "type": "string",
                                    "description": "The text to analyze"
                                },
                                "analysis_type": {
                                    "type": "string",
                                    "description": "Type of analysis (sentiment, summary, keywords)",
                                    "default": "summary"
                                }
                            },
                            "required": ["text"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            
            if name == "chat_completion":
                return await self.handle_chat_completion(arguments)
            elif name == "generate_image":
                return await self.handle_generate_image(arguments)
            elif name == "analyze_text":
                return await self.handle_analyze_text(arguments)
            else:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Unknown tool: {name}"
                        )
                    ],
                    isError=True
                )
    
    async def handle_chat_completion(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle chat completion requests"""
        try:
            message = arguments.get("message", "")
            model = arguments.get("model", "gpt-3.5-turbo")
            max_tokens = arguments.get("max_tokens", 1000)
            
            response = openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": message}],
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=content
                    )
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error in chat completion: {str(e)}"
                    )
                ],
                isError=True
            )
    
    async def handle_generate_image(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle image generation requests"""
        try:
            prompt = arguments.get("prompt", "")
            size = arguments.get("size", "1024x1024")
            quality = arguments.get("quality", "standard")
            
            response = openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=1
            )
            
            image_url = response.data[0].url
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Generated image: {image_url}"
                    )
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error generating image: {str(e)}"
                    )
                ],
                isError=True
            )
    
    async def handle_analyze_text(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle text analysis requests"""
        try:
            text = arguments.get("text", "")
            analysis_type = arguments.get("analysis_type", "summary")
            
            if analysis_type == "sentiment":
                prompt = f"Analyze the sentiment of this text: {text}"
            elif analysis_type == "keywords":
                prompt = f"Extract key keywords from this text: {text}"
            else:  # summary
                prompt = f"Provide a brief summary of this text: {text}"
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=content
                    )
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error analyzing text: {str(e)}"
                    )
                ],
                isError=True
            )

async def main():
    """Main function to run the MCP server"""
    server = OpenAIMCPServer()
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set")
        print("Please set your OpenAI API key in the .env file or environment")
        sys.exit(1)
    
    print("Starting OpenAI MCP Server...")
    print("Available tools:")
    print("- chat_completion: Send messages to OpenAI's chat completion API")
    print("- generate_image: Generate images using DALL-E")
    print("- analyze_text: Analyze text for sentiment, summary, or keywords")
    
    async with stdio_server() as (read_stream, write_stream):
        # Create basic notification options
        notification_options = type('NotificationOptions', (), {
            'tools_changed': False,
            'resources_changed': False,
            'prompts_changed': False,
            'roots_changed': False
        })()
        
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="openai-tools",
                server_version="1.0.0",
                capabilities=server.server.get_capabilities(
                    notification_options=notification_options,
                    experimental_capabilities={}
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 