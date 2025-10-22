# Keboola Integration for Claude Code

This experiment explores creating a comprehensive Keboola integration for Claude Code using MCP servers and skills.

## Approaches

### 1. MCP Server (Recommended for Live API Access)

An MCP server provides Claude Code with direct access to Keboola APIs and capabilities.

**Advantages:**
- Real-time API interactions
- Execute jobs and monitor status
- Access live data and metadata
- Full CRUD operations on components
- Programmatic orchestration

**See:** `mcp-server/` directory

### 2. Skill Definition (For Knowledge & Best Practices)

A skill embeds Keboola expertise and common patterns into Claude Code.

**Advantages:**
- Offline knowledge access
- Best practices and patterns
- Architecture guidance
- No API credentials needed for docs
- Faster responses for common questions

**See:** `skill/` directory

### 3. Hybrid Approach (Best of Both)

Combine MCP server for operations + skill for expertise:
- Use MCP tools for live data and operations
- Use skill knowledge for guidance and best practices
- Skill can leverage MCP tools when available

## Getting Started

1. Review the MCP server implementation in `mcp-server/`
2. Check the skill structure in `skill/`
3. Follow setup instructions in each directory
4. Test with example workflows in `examples/`

## Resources

- Keboola Developer Documentation: https://developers.keboola.com/
- MCP Protocol Spec: https://spec.modelcontextprotocol.io/
- Claude Code Documentation: https://docs.claude.com/claude-code
