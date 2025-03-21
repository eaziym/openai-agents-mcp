"""
Example demonstrating how to use an agent with MCP servers.

This example shows how to:
1. Load MCP servers from the config file automatically
2. Create an agent that specifies which MCP servers to use
3. Run the agent to dynamically load and use tools from the specified MCP servers

To use this example:
1. Create an mcp_agent.config.yaml file in this directory or a parent directory
2. Configure your MCP servers in that file
3. Run this example
"""

import asyncio
import os
import sys
from typing import TYPE_CHECKING, Any
from dotenv import load_dotenv

if TYPE_CHECKING:
    from mcp_agent.config import MCPSettings

# Add the src directory to the path for imports to work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables from .env file
load_dotenv()

from agents import Agent, Runner, function_tool, enable_verbose_stdout_logging

# Configure OpenAI API key
# Method 1: Set it directly in the code
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"  # Replace with your actual API key

# Method 2: Load from environment (preferred)
# Make sure you have set the OPENAI_API_KEY environment variable before running:
# export OPENAI_API_KEY="your-api-key-here"

if "OPENAI_API_KEY" not in os.environ:
    print("Error: OPENAI_API_KEY environment variable is not set.")
    print("Set it with: export OPENAI_API_KEY='your-api-key-here'")
    sys.exit(1)

enable_verbose_stdout_logging()


# Define a simple local tool to demonstrate combining local and MCP tools
@function_tool
def get_current_weather(location: str) -> str:
    """
    Get the current weather for a location.

    Args:
        location: The city and state, e.g. "San Francisco, CA"

    Returns:
        The current weather for the requested location
    """
    return f"The weather in {location} is currently sunny and 72 degrees Fahrenheit."


# Create a simple context class that can be extended with MCP server registry
class AgentContext:
    def __init__(self, mcp_config: "MCPSettings" = None, mcp_config_path: str = None):
        """
        Initialize the context.

        Args:
            mcp_config: Optional MCPSettings object containing the server configurations
                If unspecified, the MCP settings are loaded from the mcp_config_path
            mcp_config_path: Optional path to the mcp_agent.config.yaml file
                If both mcp_config and mcp_config_path are unspecified,
                the default discovery process will look for the config file matching
                "mcp_agent.config.yaml" recursively up from the current working directory.
        """
        self.mcp_config_path = mcp_config_path
        self.mcp_config = mcp_config


async def main():
    # Specify a custom config path if needed, or set to None to use default discovery
    mcp_config_path = None  # Set to a file path if needed

    # Alternatively, define MCP config programmatically
    mcp_config = None
    # mcp_config = MCPSettings(
    #     servers={
    #         "fetch": MCPServerSettings(
    #             command="uvx",
    #             args=["mcp-server-fetch"],
    #         ),
    #         "filesystem": MCPServerSettings(
    #             command="npx",
    #             args=["-y", "@modelcontextprotocol/server-filesystem", "."],
    #         ),
    #     }
    # ),

    # Create a context object containing MCP settings
    context = AgentContext(mcp_config_path=mcp_config_path, mcp_config=mcp_config)

    # Create an agent with specific MCP servers you want to use
    # These must be defined in your mcp_agent.config.yaml file
    agent = Agent(
        name="MCP Assistant",
        instructions="""You are a helpful assistant with access to both local tools 
            and tools from MCP servers. Use these tools to help the user.""",
        tools=[get_current_weather],  # Local tools
    )

    # Set the MCP servers to use
    agent.mcp_servers = ["fetch", "filesystem"]  # Specify which MCP servers to use

    # Run the agent - tools from the specified MCP servers will be automatically loaded
    result = await Runner.run(
        starting_agent=agent,
        input="What's the weather like in Miami?",
        context=context,
    )

    # Print the agent's response
    print("\nAgent response:")
    print(result.final_output)

    result = await Runner.run(
        starting_agent=agent,
        input="Print the first paragraph of https://openai.github.io/openai-agents-python/",
        context=context,
    )

    # Print the agent's response
    print("\nAgent response:")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
