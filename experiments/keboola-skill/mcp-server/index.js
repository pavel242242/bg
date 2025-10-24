#!/usr/bin/env node
/**
 * Keboola MCP Server
 *
 * Simple wrapper around Keboola's existing APIs.
 * Exposes Keboola functionality to Claude Code without reimplementing anything.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const KEBOOLA_TOKEN = process.env.KEBOOLA_API_TOKEN;
const KEBOOLA_URL = process.env.KEBOOLA_STACK_URL || 'https://connection.keboola.com';

if (!KEBOOLA_TOKEN) {
  console.error('Error: KEBOOLA_API_TOKEN environment variable is required');
  process.exit(1);
}

// Load documentation index
let docsIndex = { documents: [], components: {}, topics: {} };
try {
  const indexPath = path.join(__dirname, '../docs/index.json');
  const indexData = await fs.readFile(indexPath, 'utf-8');
  docsIndex = JSON.parse(indexData);
  console.error(`Loaded ${docsIndex.documents.length} documentation files`);
} catch (error) {
  console.error('Warning: Could not load documentation index. Run: npm run index-docs');
}

// Initialize MCP server
const server = new Server(
  {
    name: 'keboola',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
      resources: {},
    },
  }
);

// Helper: Call Keboola Storage API
async function callKeboolaAPI(endpoint, method = 'GET', data = null, params = null) {
  try {
    const response = await axios({
      method,
      url: `${KEBOOLA_URL}/v2/storage/${endpoint}`,
      headers: {
        'X-StorageApi-Token': KEBOOLA_TOKEN,
        'Content-Type': 'application/json',
      },
      data,
      params,
    });
    return response.data;
  } catch (error) {
    throw new Error(`Keboola API error: ${error.response?.data?.message || error.message}`);
  }
}

// Register MCP Tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'keboola_storage_api',
      description: 'Call Keboola Storage API directly. Use this to list buckets, get table info, export/import data, etc.',
      inputSchema: {
        type: 'object',
        properties: {
          endpoint: {
            type: 'string',
            description: 'API endpoint path (e.g., "buckets", "tables/in.c-main.customers")',
          },
          method: {
            type: 'string',
            enum: ['GET', 'POST', 'PUT', 'DELETE'],
            default: 'GET',
            description: 'HTTP method',
          },
          data: {
            type: 'object',
            description: 'Request body for POST/PUT requests',
          },
          params: {
            type: 'object',
            description: 'Query parameters',
          },
        },
        required: ['endpoint'],
      },
    },
    {
      name: 'keboola_list_buckets',
      description: 'List all storage buckets in the Keboola project',
      inputSchema: {
        type: 'object',
        properties: {},
      },
    },
    {
      name: 'keboola_list_tables',
      description: 'List all tables in a specific bucket',
      inputSchema: {
        type: 'object',
        properties: {
          bucketId: {
            type: 'string',
            description: 'Bucket ID (e.g., "in.c-main")',
          },
        },
        required: ['bucketId'],
      },
    },
    {
      name: 'keboola_get_table',
      description: 'Get detailed information about a specific table',
      inputSchema: {
        type: 'object',
        properties: {
          tableId: {
            type: 'string',
            description: 'Table ID (e.g., "in.c-main.customers")',
          },
        },
        required: ['tableId'],
      },
    },
    {
      name: 'keboola_search_docs',
      description: 'Search Keboola documentation for specific topics, components, or concepts',
      inputSchema: {
        type: 'object',
        properties: {
          query: {
            type: 'string',
            description: 'Search query (e.g., "mysql extractor", "incremental loading")',
          },
          limit: {
            type: 'number',
            default: 5,
            description: 'Maximum number of results',
          },
        },
        required: ['query'],
      },
    },
  ],
}));

// Handle Tool Calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'keboola_storage_api': {
        const result = await callKeboolaAPI(
          args.endpoint,
          args.method || 'GET',
          args.data,
          args.params
        );
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'keboola_list_buckets': {
        const buckets = await callKeboolaAPI('buckets');
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(buckets, null, 2),
            },
          ],
        };
      }

      case 'keboola_list_tables': {
        const tables = await callKeboolaAPI(`buckets/${args.bucketId}/tables`);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(tables, null, 2),
            },
          ],
        };
      }

      case 'keboola_get_table': {
        const table = await callKeboolaAPI(`tables/${args.tableId}`);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(table, null, 2),
            },
          ],
        };
      }

      case 'keboola_search_docs': {
        const query = args.query.toLowerCase();
        const limit = args.limit || 5;

        const results = docsIndex.documents
          .filter(doc =>
            doc.content.toLowerCase().includes(query) ||
            doc.path.toLowerCase().includes(query)
          )
          .slice(0, limit)
          .map(doc => ({
            path: doc.path,
            repo: doc.repo,
            url: doc.url,
            excerpt: extractExcerpt(doc.content, query),
          }));

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(results, null, 2),
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

// Expose documentation as resources
server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: docsIndex.documents.slice(0, 100).map(doc => ({
    uri: `keboola://docs/${doc.path}`,
    name: doc.path,
    description: `Documentation from ${doc.repo}`,
    mimeType: 'text/markdown',
  })),
}));

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const docPath = request.params.uri.replace('keboola://docs/', '');
  const doc = docsIndex.documents.find(d => d.path === docPath);

  if (!doc) {
    return {
      contents: [
        {
          uri: request.params.uri,
          mimeType: 'text/plain',
          text: 'Documentation not found',
        },
      ],
    };
  }

  return {
    contents: [
      {
        uri: request.params.uri,
        mimeType: 'text/markdown',
        text: doc.content,
      },
    ],
  };
});

// Helper: Extract relevant excerpt from document
function extractExcerpt(content, query, contextLength = 200) {
  const lowerContent = content.toLowerCase();
  const index = lowerContent.indexOf(query.toLowerCase());

  if (index === -1) {
    return content.substring(0, contextLength) + '...';
  }

  const start = Math.max(0, index - contextLength / 2);
  const end = Math.min(content.length, index + query.length + contextLength / 2);

  let excerpt = content.substring(start, end);
  if (start > 0) excerpt = '...' + excerpt;
  if (end < content.length) excerpt = excerpt + '...';

  return excerpt;
}

// Start the MCP server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Keboola MCP Server running on stdio');
}

main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
