import { Actor } from 'apify';
import { ApifyClient } from 'apify-client';
import Anthropic from '@anthropic-ai/sdk';
import express from 'express';
import { spawn } from 'child_process';
import * as fs from 'fs';

// State management
let dataCollectionActive = false;
let collectedRuns = [];
let serverUrl = null;

/**
 * Fetch all actor runs from the account
 */
async function fetchAllActorRuns(client) {
    console.log('Fetching all actor runs...');
    const runs = [];

    try {
        // Get all actors in the account
        const { items: actors } = await client.actors().list();
        console.log(`Found ${actors.length} actors`);

        // For each actor, get recent runs
        for (const actor of actors) {
            try {
                const { items: actorRuns } = await client.actor(actor.id).runs().list({
                    limit: 10,
                    desc: true
                });

                for (const run of actorRuns) {
                    runs.push({
                        actorId: actor.id,
                        actorName: actor.name,
                        runId: run.id,
                        status: run.status,
                        startedAt: run.startedAt,
                        finishedAt: run.finishedAt,
                        stats: run.stats,
                        meta: run.meta
                    });
                }
            } catch (err) {
                console.error(`Error fetching runs for actor ${actor.name}:`, err.message);
            }
        }

        console.log(`Collected ${runs.length} runs total`);
        return runs;
    } catch (error) {
        console.error('Error fetching actors:', error);
        throw error;
    }
}

/**
 * Push data using Claude Agent SDK
 */
async function pushDataViaClaudeAgent(data) {
    console.log('Pushing data via Claude Agent SDK...');

    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
        throw new Error('ANTHROPIC_API_KEY environment variable not set');
    }

    const anthropic = new Anthropic({ apiKey });

    // Format data for the agent
    const dataPayload = {
        timestamp: new Date().toISOString(),
        totalRuns: data.length,
        runs: data,
        summary: {
            byStatus: data.reduce((acc, run) => {
                acc[run.status] = (acc[run.status] || 0) + 1;
                return acc;
            }, {}),
            byActor: data.reduce((acc, run) => {
                acc[run.actorName] = (acc[run.actorName] || 0) + 1;
                return acc;
            }, {})
        }
    };

    // Use Claude to process and potentially export the data
    const message = await anthropic.messages.create({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 1024,
        messages: [{
            role: 'user',
            content: `Data export request. Process this Apify runs data and confirm receipt:\n\n${JSON.stringify(dataPayload, null, 2)}`
        }]
    });

    console.log('Claude Agent response:', message.content[0].text);

    // Store the data locally as well
    await Actor.setValue('latest_export', dataPayload);

    return {
        success: true,
        exportedAt: new Date().toISOString(),
        recordCount: data.length,
        claudeResponse: message.content[0].text
    };
}

/**
 * Start tunnel for public access
 */
async function startTunnel(port, method = 'bore') {
    console.log(`Starting ${method} tunnel on port ${port}...`);

    if (method === 'bore') {
        const boreProcess = spawn('bore', ['local', port.toString(), '--to', 'bore.pub'], {
            stdio: 'pipe'
        });

        return new Promise((resolve, reject) => {
            let output = '';

            boreProcess.stdout.on('data', (data) => {
                output += data.toString();
                console.log(`[bore] ${data}`);

                // Parse the public URL from bore output
                const match = output.match(/listening at (bore\.pub:\d+)/);
                if (match) {
                    const url = `http://${match[1]}`;
                    resolve({ process: boreProcess, url });
                }
            });

            boreProcess.stderr.on('data', (data) => {
                console.error(`[bore error] ${data}`);
            });

            boreProcess.on('error', reject);

            // Timeout after 10 seconds
            setTimeout(() => reject(new Error('Tunnel startup timeout')), 10000);
        });
    } else if (method === 'cloudflare') {
        const cfProcess = spawn('cloudflared', ['tunnel', '--url', `http://localhost:${port}`], {
            stdio: 'pipe'
        });

        return new Promise((resolve, reject) => {
            let output = '';

            cfProcess.stderr.on('data', (data) => {
                output += data.toString();
                console.log(`[cloudflared] ${data}`);

                // Parse the public URL from cloudflared output
                const match = output.match(/https:\/\/[a-z0-9-]+\.trycloudflare\.com/);
                if (match) {
                    resolve({ process: cfProcess, url: match[0] });
                }
            });

            cfProcess.on('error', reject);

            setTimeout(() => reject(new Error('Tunnel startup timeout')), 15000);
        });
    }

    throw new Error(`Unknown tunnel method: ${method}`);
}

/**
 * Open URL locally using xli
 */
function openUrlWithXli(url, authToken = null) {
    console.log(`Opening URL with xli: ${url}`);

    const fullUrl = authToken ? `${url}?auth=${authToken}` : url;

    // Use xli to open the browser
    const xliProcess = spawn('xli', ['open', fullUrl], {
        stdio: 'inherit'
    });

    xliProcess.on('error', (err) => {
        console.error('Failed to open with xli:', err.message);
        console.log('Fallback: Please open manually:', fullUrl);
    });
}

/**
 * Create Express web UI
 */
function createWebUI(apifyClient) {
    const app = express();
    app.use(express.json());
    app.use(express.static('public'));

    // Simple auth token (can be set via env var)
    const authToken = process.env.WEB_UI_AUTH_TOKEN || 'default-token';

    // Auth middleware
    const authenticate = (req, res, next) => {
        const token = req.headers.authorization?.replace('Bearer ', '') || req.query.auth;
        if (token === authToken) {
            next();
        } else {
            res.status(401).json({ error: 'Unauthorized' });
        }
    };

    // Root endpoint
    app.get('/', (req, res) => {
        res.send(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Apify Data Collector</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                    h1 { color: #333; }
                    button { padding: 10px 20px; margin: 5px; font-size: 16px; cursor: pointer; }
                    .start { background: #4CAF50; color: white; border: none; }
                    .stop { background: #f44336; color: white; border: none; }
                    .export { background: #2196F3; color: white; border: none; }
                    .status { padding: 15px; background: #f0f0f0; border-radius: 5px; margin: 20px 0; }
                    .runs { max-height: 400px; overflow-y: auto; background: #fafafa; padding: 10px; }
                    pre { white-space: pre-wrap; word-wrap: break-word; }
                </style>
            </head>
            <body>
                <h1>🚀 Apify Data Collector Control Panel</h1>
                <div class="status" id="status">
                    <strong>Status:</strong> <span id="collection-status">Idle</span><br>
                    <strong>Runs Collected:</strong> <span id="run-count">0</span><br>
                    <strong>Public URL:</strong> <span id="public-url">${serverUrl || 'Not available'}</span>
                </div>
                <div>
                    <button class="start" onclick="startCollection()">Start Collection</button>
                    <button class="stop" onclick="stopCollection()">Stop Collection</button>
                    <button class="export" onclick="exportData()">Export via Claude Agent</button>
                    <button onclick="refreshStatus()">Refresh Status</button>
                </div>
                <h2>Recent Runs</h2>
                <div class="runs" id="runs"></div>

                <script>
                    const authToken = new URLSearchParams(window.location.search).get('auth') || 'default-token';

                    async function apiCall(endpoint, method = 'GET') {
                        const res = await fetch(endpoint, {
                            method,
                            headers: { 'Authorization': 'Bearer ' + authToken }
                        });
                        return res.json();
                    }

                    async function startCollection() {
                        const result = await apiCall('/api/start', 'POST');
                        alert(result.message || 'Collection started');
                        refreshStatus();
                    }

                    async function stopCollection() {
                        const result = await apiCall('/api/stop', 'POST');
                        alert(result.message || 'Collection stopped');
                        refreshStatus();
                    }

                    async function exportData() {
                        const result = await apiCall('/api/export', 'POST');
                        alert('Export result: ' + JSON.stringify(result, null, 2));
                    }

                    async function refreshStatus() {
                        const status = await apiCall('/api/status');
                        document.getElementById('collection-status').textContent = status.active ? 'Active' : 'Idle';
                        document.getElementById('run-count').textContent = status.runCount;

                        if (status.runs && status.runs.length > 0) {
                            document.getElementById('runs').innerHTML = '<pre>' +
                                JSON.stringify(status.runs.slice(0, 20), null, 2) +
                                '</pre>';
                        }
                    }

                    // Auto-refresh every 5 seconds
                    setInterval(refreshStatus, 5000);
                    refreshStatus();
                </script>
            </body>
            </html>
        `);
    });

    // API: Get status
    app.get('/api/status', authenticate, (req, res) => {
        res.json({
            active: dataCollectionActive,
            runCount: collectedRuns.length,
            runs: collectedRuns,
            serverUrl
        });
    });

    // API: Start data collection
    app.post('/api/start', authenticate, async (req, res) => {
        if (dataCollectionActive) {
            return res.json({ message: 'Collection already active' });
        }

        dataCollectionActive = true;

        // Fetch runs in background
        (async () => {
            try {
                collectedRuns = await fetchAllActorRuns(apifyClient);
                console.log(`Collection complete: ${collectedRuns.length} runs`);
            } catch (error) {
                console.error('Collection error:', error);
                dataCollectionActive = false;
            }
        })();

        res.json({ message: 'Data collection started', active: true });
    });

    // API: Stop data collection
    app.post('/api/stop', authenticate, (req, res) => {
        dataCollectionActive = false;
        res.json({ message: 'Data collection stopped', active: false });
    });

    // API: Export data via Claude Agent
    app.post('/api/export', authenticate, async (req, res) => {
        if (collectedRuns.length === 0) {
            return res.status(400).json({ error: 'No data to export' });
        }

        try {
            const result = await pushDataViaClaudeAgent(collectedRuns);
            res.json(result);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    });

    return app;
}

/**
 * Main actor entry point
 */
Actor.main(async () => {
    console.log('🚀 Apify Data Collector Actor starting...');

    // Get input
    const input = await Actor.getInput() || {};
    const {
        tunnelMethod = 'bore', // 'bore' or 'cloudflare'
        webUiPort = 3000,
        autoExport = false,
        openBrowser = true
    } = input;

    // Initialize Apify client
    const apifyClient = new ApifyClient({
        token: process.env.APIFY_TOKEN
    });

    // Create and start web UI
    const app = createWebUI(apifyClient);
    const server = app.listen(webUiPort, () => {
        console.log(`✅ Web UI listening on port ${webUiPort}`);
        console.log(`🔗 Local URL: http://localhost:${webUiPort}`);
    });

    // Start tunnel for public access
    let tunnelProcess = null;
    try {
        const tunnel = await startTunnel(webUiPort, tunnelMethod);
        tunnelProcess = tunnel.process;
        serverUrl = tunnel.url;
        console.log(`✅ Public URL: ${serverUrl}`);

        // Open browser with xli if requested
        if (openBrowser) {
            const authToken = process.env.WEB_UI_AUTH_TOKEN || 'default-token';
            setTimeout(() => {
                openUrlWithXli(serverUrl, authToken);
            }, 2000);
        }
    } catch (error) {
        console.error('⚠️  Tunnel setup failed:', error.message);
        console.log('Continuing with local access only');
    }

    // If auto-export is enabled, collect and export immediately
    if (autoExport) {
        console.log('Auto-export enabled, starting collection...');
        collectedRuns = await fetchAllActorRuns(apifyClient);
        const result = await pushDataViaClaudeAgent(collectedRuns);
        console.log('Auto-export result:', result);
    }

    // Keep the actor running
    console.log('✅ Actor is running. Web UI is accessible.');
    console.log('Press Ctrl+C to stop.');

    // Handle cleanup on exit
    process.on('SIGINT', () => {
        console.log('Shutting down...');
        server.close();
        if (tunnelProcess) {
            tunnelProcess.kill();
        }
        process.exit(0);
    });

    // Keep alive
    await new Promise(() => {});
});
