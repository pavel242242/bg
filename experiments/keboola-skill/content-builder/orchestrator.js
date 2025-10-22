#!/usr/bin/env node
/**
 * Content Builder Orchestrator
 *
 * Spawns Haiku agents to build curated content for the Keboola skill.
 */

import { Task } from '@anthropic/sdk';
import PROMPTS from './prompts.js';
import fs from 'fs/promises';
import path from 'path';

class ContentOrchestrator {
  constructor() {
    this.skillDir = path.join(__dirname, '../skill');
    this.results = [];
  }

  /**
   * Build content for a specific component
   */
  async buildComponent(componentName, docUrls) {
    console.log(`\nBuilding content for: ${componentName}`);
    console.log('Spawning 3 agents in parallel...');

    const [guide, examples, troubleshooting] = await Promise.all([
      this.spawnAgent('guide-writer', {
        prompt: PROMPTS.componentGuide(componentName, docUrls),
        description: `Writing guide for ${componentName}`
      }),

      this.spawnAgent('example-creator', {
        prompt: PROMPTS.exampleCreator(componentName, 'basic and incremental'),
        description: `Creating examples for ${componentName}`
      }),

      this.spawnAgent('troubleshooter', {
        prompt: PROMPTS.troubleshootingGuide(componentName),
        description: `Writing troubleshooting for ${componentName}`
      })
    ]);

    // Save results
    await this.saveContent(componentName, {
      guide,
      examples,
      troubleshooting
    });

    console.log(`✓ Content built for ${componentName}`);
    return { guide, examples, troubleshooting };
  }

  /**
   * Build all database extractors
   */
  async buildDatabaseExtractors() {
    const extractors = [
      {
        name: 'MySQL',
        docs: [
          'https://help.keboola.com/components/extractors/database/mysql/',
          'https://developers.keboola.com/extend/component/'
        ]
      },
      {
        name: 'PostgreSQL',
        docs: [
          'https://help.keboola.com/components/extractors/database/postgresql/',
        ]
      },
      {
        name: 'SQL Server',
        docs: [
          'https://help.keboola.com/components/extractors/database/sqlserver/',
        ]
      },
      {
        name: 'Snowflake',
        docs: [
          'https://help.keboola.com/components/extractors/database/snowflake/',
        ]
      }
    ];

    console.log('\n🚀 Building Database Extractors Content');
    console.log(`Processing ${extractors.length} extractors in parallel...`);

    const results = await Promise.all(
      extractors.map(ext => this.buildComponent(ext.name, ext.docs))
    );

    console.log('\n✅ All database extractors completed!');
    return results;
  }

  /**
   * Build common patterns
   */
  async buildPatterns() {
    const patterns = [
      {
        name: 'Incremental Loading',
        context: 'Loading only new or changed data instead of full table refreshes'
      },
      {
        name: 'Change Data Capture',
        context: 'Tracking changes in source systems and replicating to warehouse'
      },
      {
        name: 'Slowly Changing Dimensions',
        context: 'Handling dimensional data that changes over time (SCD Type 1, 2, 3)'
      },
      {
        name: 'Star Schema',
        context: 'Organizing data into fact and dimension tables for analytics'
      },
      {
        name: 'Data Quality Checks',
        context: 'Validating data quality before loading to destination'
      }
    ];

    console.log('\n🚀 Building Pattern Documentation');
    console.log(`Processing ${patterns.length} patterns in parallel...`);

    const results = await Promise.all(
      patterns.map(pattern =>
        this.spawnAgent('pattern-extractor', {
          prompt: PROMPTS.patternExtractor(pattern.name, pattern.context),
          description: `Documenting ${pattern.name} pattern`
        })
      )
    );

    // Save patterns
    for (let i = 0; i < patterns.length; i++) {
      const filename = patterns[i].name.toLowerCase().replace(/\s+/g, '-');
      await fs.writeFile(
        path.join(this.skillDir, 'patterns', `${filename}.md`),
        results[i]
      );
    }

    console.log('\n✅ All patterns documented!');
    return results;
  }

  /**
   * Build best practices guides
   */
  async buildBestPractices() {
    const topics = [
      'Naming Conventions',
      'Security',
      'Performance Optimization',
      'Cost Optimization',
      'Monitoring and Alerting',
      'Testing Data Pipelines',
      'Team Collaboration'
    ];

    console.log('\n🚀 Building Best Practices Guides');
    console.log(`Processing ${topics.length} topics in parallel...`);

    const results = await Promise.all(
      topics.map(topic =>
        this.spawnAgent('best-practices', {
          prompt: PROMPTS.bestPractices(topic),
          description: `Writing best practices for ${topic}`
        })
      )
    );

    // Save best practices
    for (let i = 0; i < topics.length; i++) {
      const filename = topics[i].toLowerCase().replace(/\s+/g, '-');
      await fs.writeFile(
        path.join(this.skillDir, 'best-practices', `${filename}.md`),
        results[i]
      );
    }

    console.log('\n✅ All best practices guides completed!');
    return results;
  }

  /**
   * Spawn a Haiku agent to perform a task
   */
  async spawnAgent(type, { prompt, description }) {
    console.log(`  ⚡ Spawning ${type} agent...`);

    try {
      // Use Task tool to spawn Haiku agent
      const result = await Task({
        subagent_type: 'general-purpose',
        description: description,
        prompt: prompt
      });

      console.log(`  ✓ ${type} completed`);
      return result;

    } catch (error) {
      console.error(`  ✗ ${type} failed:`, error.message);
      throw error;
    }
  }

  /**
   * Save content to skill directory
   */
  async saveContent(componentName, { guide, examples, troubleshooting }) {
    const baseName = componentName.toLowerCase().replace(/\s+/g, '-');

    // Ensure directories exist
    await fs.mkdir(path.join(this.skillDir, 'components'), { recursive: true });
    await fs.mkdir(path.join(this.skillDir, 'examples'), { recursive: true });
    await fs.mkdir(path.join(this.skillDir, 'troubleshooting'), { recursive: true });

    // Save guide
    if (guide) {
      await fs.writeFile(
        path.join(this.skillDir, 'components', `${baseName}.md`),
        guide
      );
    }

    // Save examples
    if (examples) {
      await fs.writeFile(
        path.join(this.skillDir, 'examples', `${baseName}-examples.md`),
        examples
      );
    }

    // Save troubleshooting
    if (troubleshooting) {
      await fs.writeFile(
        path.join(this.skillDir, 'troubleshooting', `${baseName}.md`),
        troubleshooting
      );
    }
  }

  /**
   * Build everything
   */
  async buildAll() {
    console.log('🚀 Building Complete Keboola Skill Knowledge Base');
    console.log('This will spawn multiple Haiku agents in parallel...\n');

    const startTime = Date.now();

    try {
      // Run all builds in parallel
      await Promise.all([
        this.buildDatabaseExtractors(),
        this.buildPatterns(),
        this.buildBestPractices()
      ]);

      const duration = ((Date.now() - startTime) / 1000).toFixed(2);
      console.log(`\n✅ All content built in ${duration}s`);
      console.log(`📁 Content saved to: ${this.skillDir}`);

    } catch (error) {
      console.error('\n❌ Build failed:', error);
      throw error;
    }
  }
}

// CLI
const command = process.argv[2];
const orchestrator = new ContentOrchestrator();

switch (command) {
  case 'component':
    const name = process.argv[3];
    const urls = process.argv.slice(4);
    orchestrator.buildComponent(name, urls);
    break;

  case 'extractors':
    orchestrator.buildDatabaseExtractors();
    break;

  case 'patterns':
    orchestrator.buildPatterns();
    break;

  case 'best-practices':
    orchestrator.buildBestPractices();
    break;

  case 'all':
    orchestrator.buildAll();
    break;

  default:
    console.log(`
Usage:
  node orchestrator.js component <name> <doc-url> [<doc-url>...]
  node orchestrator.js extractors
  node orchestrator.js patterns
  node orchestrator.js best-practices
  node orchestrator.js all

Examples:
  node orchestrator.js component MySQL https://help.keboola.com/...
  node orchestrator.js extractors
  node orchestrator.js all
`);
}
