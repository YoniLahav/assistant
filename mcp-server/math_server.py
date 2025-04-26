from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
async def add(a: int, b: int) -> int:
    """Add two numbers"""
    print("received " + str(a) + "+" + str(b))
    return a + b

@mcp.tool()
async def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    print("received " + str(a) + "*" + str(b))
    return a * b

if __name__ == "__main__":
    mcp.run(transport="sse")
