from fastmcp import FastMCP

# Initialize the FastMCP server
mcp = FastMCP(name="PythonCommitServer")

# We don't know what tools the client expects yet,
# so we won't define any for now.
# @mcp.tool()
# def some_commit_tool(args...):
#    ...

if __name__ == "__main__":
    # Run the server using the default stdio transport
    mcp.run() 