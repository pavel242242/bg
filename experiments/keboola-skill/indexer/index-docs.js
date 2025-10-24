#!/usr/bin/env node
/**
 * Documentation Indexer for Keboola
 *
 * This script clones Keboola's documentation from GitHub and creates
 * a searchable index for the Claude Code skill.
 */

import { Octokit } from '@octokit/rest';
import fs from 'fs/promises';
import path from 'path';

const REPOS = [
  { owner: 'keboola', repo: 'developers-docs', branch: 'main' },
  { owner: 'keboola', repo: 'connection-docs', branch: 'main' },
];

const OUTPUT_DIR = './docs';

async function indexDocs() {
  console.log('Starting documentation indexing...\n');

  const octokit = new Octokit({
    // No auth needed for public repos
  });

  const index = {
    indexed_at: new Date().toISOString(),
    documents: [],
    components: {},
    topics: {},
  };

  for (const { owner, repo, branch } of REPOS) {
    console.log(`Indexing ${owner}/${repo}...`);

    try {
      // Get repository tree
      const { data: tree } = await octokit.rest.git.getTree({
        owner,
        repo,
        tree_sha: branch,
        recursive: '1',
      });

      // Filter for markdown files
      const mdFiles = tree.tree.filter(
        file => file.path.endsWith('.md') && file.type === 'blob'
      );

      console.log(`  Found ${mdFiles.length} markdown files`);

      // Process each markdown file (limit to first 50 to avoid rate limits)
      for (const file of mdFiles.slice(0, 50)) {
        try {
          const { data: content } = await octokit.rest.repos.getContent({
            owner,
            repo,
            path: file.path,
          });

          if (content.type === 'file' && content.content) {
            const markdown = Buffer.from(content.content, 'base64').toString('utf-8');

            const doc = {
              path: file.path,
              repo: `${owner}/${repo}`,
              url: `https://github.com/${owner}/${repo}/blob/${branch}/${file.path}`,
              size: content.size,
              content: markdown,
            };

            index.documents.push(doc);

            // Extract component info if it's a component doc
            if (file.path.includes('component')) {
              const componentId = extractComponentId(file.path, markdown);
              if (componentId) {
                index.components[componentId] = doc;
              }
            }

            // Categorize by topic
            const topic = extractTopic(file.path);
            if (topic) {
              if (!index.topics[topic]) {
                index.topics[topic] = [];
              }
              index.topics[topic].push(file.path);
            }

            // Small delay to avoid rate limiting
            await new Promise(resolve => setTimeout(resolve, 100));
          }
        } catch (error) {
          console.error(`  Error processing ${file.path}:`, error.message);
        }
      }

      console.log(`  Indexed ${index.documents.length} documents so far\n`);
    } catch (error) {
      console.error(`Error indexing ${owner}/${repo}:`, error.message);
    }
  }

  // Save index
  await fs.mkdir(OUTPUT_DIR, { recursive: true });
  await fs.writeFile(
    path.join(OUTPUT_DIR, 'index.json'),
    JSON.stringify(index, null, 2)
  );

  console.log('\n✓ Documentation indexing complete!');
  console.log(`  Total documents: ${index.documents.length}`);
  console.log(`  Components found: ${Object.keys(index.components).length}`);
  console.log(`  Topics: ${Object.keys(index.topics).join(', ')}`);
  console.log(`  Output: ${OUTPUT_DIR}/index.json`);
}

function extractComponentId(filePath, content) {
  // Try to extract component ID from path
  const pathMatch = filePath.match(/components?\/([a-z0-9\-\.]+)/i);
  if (pathMatch) return pathMatch[1];

  // Try to extract from content
  const contentMatch = content.match(/component[:\s]+([a-z0-9\-\.]+)/i);
  if (contentMatch) return contentMatch[1];

  return null;
}

function extractTopic(filePath) {
  const parts = filePath.split('/');
  if (parts.length > 1) {
    return parts[0]; // First directory is the topic
  }
  return 'general';
}

// Run indexer
indexDocs().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
