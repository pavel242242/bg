# Keboola Integration Implementation Guide

## Recommended Approach: Start with MCP Server

### Phase 1: Basic MCP Server (Week 1-2)

**Goal:** Get a working MCP server with core Keboola capabilities

1. **Setup Project**
   ```bash
   mkdir keboola-mcp-server
   cd keboola-mcp-server
   npm init -y
   npm install @modelcontextprotocol/sdk axios
   npm install -D typescript @types/node
   ```

2. **Implement Core Tools**
   Start with most useful tools:
   - `keboola_list_buckets` - See what buckets exist
   - `keboola_list_tables` - See tables in a bucket
   - `keboola_get_table` - Get table details
   - `keboola_run_component` - Execute a component
   - `keboola_get_job` - Check job status

3. **Test Locally**
   ```bash
   export KEBOOLA_API_TOKEN="your-token"
   export KEBOOLA_STACK_URL="https://connection.keboola.com"
   npm run build
   node build/index.js
   ```

4. **Integrate with Claude Code**
   Add to Claude Code config:
   ```json
   {
     "mcpServers": {
       "keboola": {
         "command": "node",
         "args": ["/path/to/keboola-mcp-server/build/index.js"],
         "env": {
           "KEBOOLA_API_TOKEN": "your-token",
           "KEBOOLA_STACK_URL": "https://connection.keboola.com"
         }
       }
     }
   }
   ```

### Phase 2: Add Documentation Resources (Week 3)

**Goal:** Make Keboola docs accessible to Claude

1. **Clone Keboola Docs**
   ```bash
   git clone https://github.com/keboola/developers-docs.git
   git clone https://github.com/keboola/connection-docs.git
   ```

2. **Implement Resource Handlers**
   - Serve markdown files as MCP resources
   - Index by topic and component
   - Enable full-text search

3. **Test Documentation Access**
   ```bash
   # Claude should be able to read
   keboola://docs/storage/api
   keboola://docs/components/keboola.ex-db-mysql
   ```

### Phase 3: Add Prompt Templates (Week 4)

**Goal:** Provide guided workflows for common tasks

1. **Implement Prompts**
   - Pipeline creation template
   - Data analysis template
   - Troubleshooting template
   - Optimization template

2. **Test Workflows**
   - Create a pipeline from scratch
   - Debug a failed job
   - Analyze table data

### Phase 4: Advanced Features (Week 5-6)

**Goal:** Production-ready server with all capabilities

1. **Add Remaining Tools**
   - Configuration management (CRUD)
   - Orchestration tools
   - Metadata operations
   - Workspace management

2. **Optimize Performance**
   - Cache API responses
   - Implement rate limiting
   - Add connection pooling
   - Error retry logic

3. **Add Monitoring**
   - Log all API calls
   - Track usage metrics
   - Error reporting
   - Health checks

### Phase 5: Skill Development (Week 7-8)

**Goal:** Complement MCP server with offline knowledge

1. **Extract Knowledge**
   - Review Keboola documentation
   - Document best practices
   - Collect common patterns
   - Create example workflows

2. **Structure Skill**
   - Organize by topic
   - Create skill.json
   - Write system prompt
   - Package examples

3. **Integrate with MCP**
   - Skill knows about MCP tools
   - Provides context for tool usage
   - Offers patterns that use tools

## Data Sources

### 1. GitHub Repositories to Clone

```bash
# Official Documentation
git clone https://github.com/keboola/developers-docs.git
git clone https://github.com/keboola/connection-docs.git

# Component Examples
git clone https://github.com/keboola/component-examples.git

# API Client Libraries
git clone https://github.com/keboola/storage-api-python-client.git
git clone https://github.com/keboola/sapi-php-client.git
```

### 2. Documentation URLs to Index

- https://developers.keboola.com/
- https://help.keboola.com/
- https://components.keboola.com/

### 3. API Endpoints to Integrate

- Storage API: https://connection.keboola.com/v2/storage
- Docker Runner API: https://docker-runner.keboola.com/
- Job Queue API: https://queue.keboola.com/

## Testing Strategy

### Unit Tests
```typescript
describe('KeboolaClient', () => {
  it('should list buckets', async () => {
    const client = new KeboolaClient(token, url);
    const buckets = await client.listBuckets();
    expect(buckets).toBeInstanceOf(Array);
  });
});
```

### Integration Tests
```typescript
describe('MCP Tools', () => {
  it('should execute keboola_list_buckets', async () => {
    const result = await mcp.callTool('keboola_list_buckets', {});
    expect(result.content[0].text).toContain('in.c-');
  });
});
```

### End-to-End Tests with Claude Code
```bash
# Test in Claude Code
claude: "List all my Keboola buckets"
# Should use keboola_list_buckets tool

claude: "Show me the schema of table in.c-main.customers"
# Should use keboola_get_table tool

claude: "Run my mysql extractor"
# Should use keboola_run_component tool
```

## Success Metrics

### Phase 1 Success Criteria
- [ ] MCP server runs without errors
- [ ] Can list buckets and tables
- [ ] Can execute components
- [ ] Can check job status
- [ ] Works in Claude Code

### Phase 2 Success Criteria
- [ ] Documentation accessible via resources
- [ ] Can search docs by topic
- [ ] Component docs available
- [ ] API reference integrated

### Phase 3 Success Criteria
- [ ] Prompt templates working
- [ ] Can create pipeline from prompt
- [ ] Can analyze data from prompt
- [ ] Can troubleshoot from prompt

### Final Success Criteria
- [ ] All major APIs covered
- [ ] Documentation fully integrated
- [ ] Skill provides expert guidance
- [ ] End-to-end workflows functional
- [ ] Production-ready performance
- [ ] Comprehensive test coverage

## Maintenance Plan

### Regular Updates
- Sync documentation weekly
- Update component list monthly
- Review API changes quarterly
- Update examples as needed

### Community Feedback
- Gather user feedback
- Track common issues
- Improve based on usage
- Add requested features

## Distribution

### Option 1: npm Package
```bash
npm install -g keboola-mcp-server
keboola-mcp-server --token=TOKEN --url=URL
```

### Option 2: Docker Container
```bash
docker run -e KEBOOLA_API_TOKEN=token keboola/mcp-server
```

### Option 3: Claude Code Marketplace
- Submit to Claude Code skill marketplace
- Users install with one click
- Automatic updates

## Resources

- MCP Specification: https://spec.modelcontextprotocol.io/
- Keboola Storage API: https://developers.keboola.com/integrate/storage/api/
- Keboola Components: https://components.keboola.com/
- Claude Code Docs: https://docs.claude.com/claude-code

## Next Steps

1. **Decide on approach**: MCP server, skill, or both
2. **Set up development environment**
3. **Start with Phase 1**: Basic MCP server
4. **Test with real Keboola project**
5. **Iterate based on feedback**
6. **Expand to additional phases**

## Questions to Answer

Before starting, clarify:
- Which Keboola stack (US, EU, etc.)?
- Which components are most important?
- What are the most common workflows?
- Do you need multi-project support?
- How should credentials be managed?
- What level of caching is acceptable?
