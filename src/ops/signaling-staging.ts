/**
 * WebRTC Signaling Server Deployment Script for IF.swarm (Staging)
 *
 * Purpose:
 * - Deploy WebSocket signaling server with PM2 or systemd
 * - Auto-scaling configuration (1-5 instances)
 * - Load balancer setup (nginx)
 * - Health monitoring and auto-recovery
 *
 * Philosophy:
 * - IF.ground: Reproducible deployment (Docker + process management)
 * - IF.witness: All deployment events logged
 * - IF.TTT: Transparent deployment process
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import { writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import * as path from 'path';

const execAsync = promisify(exec);

/**
 * Signaling Server Configuration
 */
export interface SignalingConfig {
  port: number;
  host: string;
  instances: number;
  maxInstances: number;
  minInstances: number;
  redisUrl?: string;
  witnessLoggerUrl?: string;
  tlsCertPath?: string;
  tlsKeyPath?: string;
}

/**
 * PM2 Process Manager Configuration
 */
export interface PM2Config {
  name: string;
  script: string;
  instances: number | 'max';
  execMode: 'cluster' | 'fork';
  autorestart: boolean;
  maxMemoryRestart: string;
  env: Record<string, string>;
}

/**
 * Nginx Load Balancer Configuration
 */
export interface NginxConfig {
  upstreamName: string;
  serverName: string;
  listenPort: number;
  listenPortSSL: number;
  backends: Array<{ host: string; port: number }>;
  sslCertPath?: string;
  sslKeyPath?: string;
}

/**
 * Deployment Configuration
 */
export interface DeploymentConfig {
  environment: 'staging' | 'production';
  signalingConfig: SignalingConfig;
  processManager: 'pm2' | 'systemd' | 'docker';
  autoScaling: boolean;
  loadBalancer: boolean;
  nginxConfig?: NginxConfig;
  healthCheckInterval: number; // ms
  witnessLogger?: (event: WitnessEvent) => Promise<void>;
}

/**
 * IF.witness Event
 */
interface WitnessEvent {
  event: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

/**
 * Signaling Server Deployment Manager
 */
export class SignalingDeployment {
  private config: DeploymentConfig;
  private healthCheckTimer?: NodeJS.Timeout;
  private witnessLogger?: (event: WitnessEvent) => Promise<void>;

  constructor(config: DeploymentConfig) {
    this.config = config;
    this.witnessLogger = config.witnessLogger;
  }

  /**
   * Deploy signaling server
   */
  async deploy(): Promise<void> {
    await this.logToWitness({
      event: 'signaling_deployment_started',
      timestamp: new Date().toISOString(),
      metadata: {
        environment: this.config.environment,
        processManager: this.config.processManager,
        instances: this.config.signalingConfig.instances
      }
    });

    try {
      // 1. Generate configuration files
      await this.generateConfigurations();

      // 2. Deploy based on process manager
      switch (this.config.processManager) {
        case 'pm2':
          await this.deployWithPM2();
          break;
        case 'systemd':
          await this.deployWithSystemd();
          break;
        case 'docker':
          await this.deployWithDocker();
          break;
        default:
          throw new Error(`Unsupported process manager: ${this.config.processManager}`);
      }

      // 3. Setup load balancer if enabled
      if (this.config.loadBalancer && this.config.nginxConfig) {
        await this.setupNginxLoadBalancer();
      }

      // 4. Verify deployment
      await this.verifyDeployment();

      // 5. Start health checks
      this.startHealthChecks();

      await this.logToWitness({
        event: 'signaling_deployment_completed',
        timestamp: new Date().toISOString(),
        metadata: {
          port: this.config.signalingConfig.port,
          instances: this.config.signalingConfig.instances
        }
      });

      console.log(`✓ Signaling server deployed successfully`);
      console.log(`  Port: ${this.config.signalingConfig.port}`);
      console.log(`  Instances: ${this.config.signalingConfig.instances}`);
      console.log(`  Process Manager: ${this.config.processManager}`);
    } catch (error) {
      await this.logToWitness({
        event: 'signaling_deployment_failed',
        timestamp: new Date().toISOString(),
        metadata: {
          error: String(error)
        }
      });
      throw error;
    }
  }

  /**
   * Generate configuration files
   */
  private async generateConfigurations(): Promise<void> {
    const configDir = path.join(process.cwd(), 'deploy', 'staging');
    if (!existsSync(configDir)) {
      await mkdir(configDir, { recursive: true });
    }

    // Generate .env file
    await this.generateEnvFile(configDir);

    // Generate PM2 ecosystem file
    if (this.config.processManager === 'pm2') {
      await this.generatePM2Config(configDir);
    }

    // Generate systemd service file
    if (this.config.processManager === 'systemd') {
      await this.generateSystemdConfig(configDir);
    }

    console.log(`✓ Configuration files generated`);
  }

  /**
   * Generate .env file
   */
  private async generateEnvFile(configDir: string): Promise<void> {
    const cfg = this.config.signalingConfig;

    const envContent = [
      '# Signaling Server Environment Configuration',
      `# Generated: ${new Date().toISOString()}`,
      '',
      `PORT=${cfg.port}`,
      `HOST=${cfg.host}`,
      `NODE_ENV=${this.config.environment}`,
      '',
      '# Redis (for multi-instance state sharing)',
      `REDIS_URL=${cfg.redisUrl || 'redis://localhost:6379'}`,
      '',
      '# IF.witness logging',
      `WITNESS_LOGGER_URL=${cfg.witnessLoggerUrl || ''}`,
      '',
      '# TLS/SSL',
      `TLS_CERT_PATH=${cfg.tlsCertPath || ''}`,
      `TLS_KEY_PATH=${cfg.tlsKeyPath || ''}`,
      ''
    ].join('\n');

    await writeFile(path.join(configDir, '.env.signaling'), envContent);
  }

  /**
   * Generate PM2 ecosystem configuration
   */
  private async generatePM2Config(configDir: string): Promise<void> {
    const cfg = this.config.signalingConfig;

    const pm2Config: { apps: PM2Config[] } = {
      apps: [{
        name: 'ifswarm-signaling-staging',
        script: 'dist/communication/webrtc-signaling-server.js',
        instances: this.config.autoScaling ? 'max' : cfg.instances,
        execMode: 'cluster',
        autorestart: true,
        maxMemoryRestart: '500M',
        env: {
          NODE_ENV: this.config.environment,
          PORT: String(cfg.port),
          HOST: cfg.host,
          REDIS_URL: cfg.redisUrl || 'redis://localhost:6379'
        }
      }]
    };

    await writeFile(
      path.join(configDir, 'ecosystem.config.js'),
      `module.exports = ${JSON.stringify(pm2Config, null, 2)};`
    );

    console.log(`✓ PM2 ecosystem config generated`);
  }

  /**
   * Generate systemd service configuration
   */
  private async generateSystemdConfig(configDir: string): Promise<void> {
    const cfg = this.config.signalingConfig;
    const projectDir = process.cwd();

    const serviceContent = [
      '[Unit]',
      'Description=IF.swarm WebRTC Signaling Server (Staging)',
      'After=network.target redis.service',
      '',
      '[Service]',
      'Type=simple',
      'User=ifswarm',
      'Group=ifswarm',
      `WorkingDirectory=${projectDir}`,
      `EnvironmentFile=${configDir}/.env.signaling`,
      `ExecStart=/usr/bin/node ${projectDir}/dist/communication/webrtc-signaling-server.js`,
      'Restart=always',
      'RestartSec=10',
      'StandardOutput=journal',
      'StandardError=journal',
      'SyslogIdentifier=ifswarm-signaling',
      '',
      '[Install]',
      'WantedBy=multi-user.target'
    ].join('\n');

    await writeFile(path.join(configDir, 'ifswarm-signaling.service'), serviceContent);

    console.log(`✓ systemd service config generated`);
    console.log(`  Copy to: /etc/systemd/system/ifswarm-signaling@.service`);
    console.log(`  Then run: systemctl daemon-reload`);
  }

  /**
   * Deploy with PM2
   */
  private async deployWithPM2(): Promise<void> {
    console.log('Deploying with PM2...');

    const configPath = path.join(process.cwd(), 'deploy', 'staging', 'ecosystem.config.js');

    try {
      // Check if PM2 is installed
      await execAsync('pm2 --version');
    } catch {
      throw new Error('PM2 not installed. Install with: npm install -g pm2');
    }

    try {
      // Stop existing processes
      await execAsync('pm2 stop ifswarm-signaling-staging').catch(() => {});
      await execAsync('pm2 delete ifswarm-signaling-staging').catch(() => {});

      // Start with ecosystem config
      const { stdout } = await execAsync(`pm2 start ${configPath}`);
      console.log(stdout);

      // Save PM2 process list
      await execAsync('pm2 save');

      console.log(`✓ Deployed with PM2`);
    } catch (error) {
      throw new Error(`PM2 deployment failed: ${error}`);
    }
  }

  /**
   * Deploy with systemd
   */
  private async deployWithSystemd(): Promise<void> {
    console.log('Deploying with systemd...');

    const cfg = this.config.signalingConfig;
    const serviceFile = path.join(process.cwd(), 'deploy', 'staging', 'ifswarm-signaling.service');

    try {
      // Copy service file
      await execAsync(`sudo cp ${serviceFile} /etc/systemd/system/ifswarm-signaling@.service`);

      // Reload systemd
      await execAsync('sudo systemctl daemon-reload');

      // Stop existing instances
      for (let i = 1; i <= cfg.instances; i++) {
        await execAsync(`sudo systemctl stop ifswarm-signaling@${i}.service`).catch(() => {});
      }

      // Start instances
      for (let i = 1; i <= cfg.instances; i++) {
        await execAsync(`sudo systemctl start ifswarm-signaling@${i}.service`);
        await execAsync(`sudo systemctl enable ifswarm-signaling@${i}.service`);
      }

      console.log(`✓ Deployed with systemd (${cfg.instances} instances)`);
    } catch (error) {
      throw new Error(`systemd deployment failed: ${error}`);
    }
  }

  /**
   * Deploy with Docker
   */
  private async deployWithDocker(): Promise<void> {
    console.log('Deploying with Docker...');

    const cfg = this.config.signalingConfig;
    const containerName = 'ifswarm-signaling-staging';

    try {
      // Stop existing container
      await execAsync(`docker stop ${containerName}`).catch(() => {});
      await execAsync(`docker rm ${containerName}`).catch(() => {});

      // Build image (assumes Dockerfile exists)
      await execAsync('docker build -t ifswarm-signaling:staging .');

      // Run container
      const dockerCmd = [
        'docker run -d',
        `--name ${containerName}`,
        `--restart unless-stopped`,
        `-p ${cfg.port}:${cfg.port}`,
        `--env-file deploy/staging/.env.signaling`,
        'ifswarm-signaling:staging'
      ].join(' ');

      const { stdout } = await execAsync(dockerCmd);
      console.log(stdout);

      console.log(`✓ Deployed with Docker`);
    } catch (error) {
      throw new Error(`Docker deployment failed: ${error}`);
    }
  }

  /**
   * Setup Nginx load balancer
   */
  private async setupNginxLoadBalancer(): Promise<void> {
    if (!this.config.nginxConfig) {
      return;
    }

    console.log('Setting up Nginx load balancer...');

    const nginxConf = this.generateNginxConfig();
    const configPath = path.join(process.cwd(), 'deploy', 'staging', 'nginx-signaling.conf');

    await writeFile(configPath, nginxConf);

    console.log(`✓ Nginx configuration generated: ${configPath}`);
    console.log(`  Copy to: /etc/nginx/sites-available/ifswarm-signaling`);
    console.log(`  Then run: sudo nginx -t && sudo systemctl reload nginx`);
  }

  /**
   * Generate Nginx configuration
   */
  private generateNginxConfig(): string {
    const cfg = this.config.nginxConfig!;

    const upstreamServers = cfg.backends
      .map(backend => `    server ${backend.host}:${backend.port};`)
      .join('\n');

    const lines = [
      '# Nginx Load Balancer for IF.swarm WebRTC Signaling',
      `# Generated: ${new Date().toISOString()}`,
      '',
      `upstream ${cfg.upstreamName} {`,
      '    # Least connections load balancing',
      '    least_conn;',
      '',
      upstreamServers,
      '',
      '    # Health checks',
      '    # keepalive 32;',
      '}',
      '',
      '# WebSocket upgrade configuration',
      'map $http_upgrade $connection_upgrade {',
      '    default upgrade;',
      '    \'\' close;',
      '}',
      '',
      'server {',
      `    listen ${cfg.listenPort};`,
      `    server_name ${cfg.serverName};`,
      '',
      '    # WebSocket proxying',
      '    location / {',
      `        proxy_pass http://${cfg.upstreamName};`,
      '        proxy_http_version 1.1;',
      '        proxy_set_header Upgrade $http_upgrade;',
      '        proxy_set_header Connection $connection_upgrade;',
      '        proxy_set_header Host $host;',
      '        proxy_set_header X-Real-IP $remote_addr;',
      '        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;',
      '        proxy_set_header X-Forwarded-Proto $scheme;',
      '',
      '        # Timeouts for WebSocket',
      '        proxy_read_timeout 300s;',
      '        proxy_send_timeout 300s;',
      '    }',
      '',
      '    # Health check endpoint',
      '    location /health {',
      `        proxy_pass http://${cfg.upstreamName}/health;`,
      '        access_log off;',
      '    }',
      '}',
      ''
    ];

    // Add SSL configuration if certificates provided
    if (cfg.sslCertPath && cfg.sslKeyPath) {
      lines.push('');
      lines.push('# SSL/TLS Configuration');
      lines.push('server {');
      lines.push(`    listen ${cfg.listenPortSSL} ssl http2;`);
      lines.push(`    server_name ${cfg.serverName};`);
      lines.push('');
      lines.push(`    ssl_certificate ${cfg.sslCertPath};`);
      lines.push(`    ssl_certificate_key ${cfg.sslKeyPath};`);
      lines.push('    ssl_protocols TLSv1.2 TLSv1.3;');
      lines.push('    ssl_ciphers HIGH:!aNULL:!MD5;');
      lines.push('    ssl_prefer_server_ciphers on;');
      lines.push('');
      lines.push('    # WebSocket proxying (same as above)');
      lines.push('    location / {');
      lines.push(`        proxy_pass http://${cfg.upstreamName};`);
      lines.push('        proxy_http_version 1.1;');
      lines.push('        proxy_set_header Upgrade $http_upgrade;');
      lines.push('        proxy_set_header Connection $connection_upgrade;');
      lines.push('        proxy_set_header Host $host;');
      lines.push('        proxy_set_header X-Real-IP $remote_addr;');
      lines.push('        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;');
      lines.push('        proxy_set_header X-Forwarded-Proto $scheme;');
      lines.push('        proxy_read_timeout 300s;');
      lines.push('        proxy_send_timeout 300s;');
      lines.push('    }');
      lines.push('}');
    }

    return lines.join('\n');
  }

  /**
   * Verify deployment
   */
  private async verifyDeployment(): Promise<void> {
    console.log('Verifying deployment...');

    // Wait for services to start
    await new Promise(resolve => setTimeout(resolve, 3000));

    // Verify based on process manager
    switch (this.config.processManager) {
      case 'pm2':
        await this.verifyPM2();
        break;
      case 'systemd':
        await this.verifySystemd();
        break;
      case 'docker':
        await this.verifyDocker();
        break;
    }

    console.log(`✓ Deployment verified`);
  }

  /**
   * Verify PM2 deployment
   */
  private async verifyPM2(): Promise<void> {
    const { stdout } = await execAsync('pm2 list');
    console.log(stdout);

    if (!stdout.includes('ifswarm-signaling-staging')) {
      throw new Error('PM2 process not found');
    }
  }

  /**
   * Verify systemd deployment
   */
  private async verifySystemd(): Promise<void> {
    const { stdout } = await execAsync('sudo systemctl status ifswarm-signaling@1.service');
    console.log(stdout);

    if (!stdout.includes('active (running)')) {
      throw new Error('systemd service not running');
    }
  }

  /**
   * Verify Docker deployment
   */
  private async verifyDocker(): Promise<void> {
    const { stdout } = await execAsync('docker ps --filter name=ifswarm-signaling-staging');
    console.log(stdout);

    if (!stdout.includes('ifswarm-signaling-staging')) {
      throw new Error('Docker container not running');
    }
  }

  /**
   * Start health checks
   */
  private startHealthChecks(): void {
    this.healthCheckTimer = setInterval(async () => {
      await this.performHealthCheck();
    }, this.config.healthCheckInterval);

    console.log(`✓ Health checks started (interval: ${this.config.healthCheckInterval}ms)`);
  }

  /**
   * Perform health check
   */
  private async performHealthCheck(): Promise<void> {
    try {
      // Check based on process manager
      let healthy = false;

      switch (this.config.processManager) {
        case 'pm2':
          const { stdout: pm2Status } = await execAsync('pm2 jlist');
          const processes = JSON.parse(pm2Status);
          healthy = processes.some((p: any) =>
            p.name === 'ifswarm-signaling-staging' && p.pm2_env.status === 'online'
          );
          break;

        case 'systemd':
          const { stdout: systemdStatus } = await execAsync('sudo systemctl is-active ifswarm-signaling@1.service');
          healthy = systemdStatus.trim() === 'active';
          break;

        case 'docker':
          const { stdout: dockerStatus } = await execAsync('docker ps --filter name=ifswarm-signaling-staging --format "{{.Status}}"');
          healthy = dockerStatus.includes('Up');
          break;
      }

      if (!healthy) {
        await this.logToWitness({
          event: 'signaling_health_check_failed',
          timestamp: new Date().toISOString(),
          metadata: {
            processManager: this.config.processManager
          }
        });
      }
    } catch (error) {
      console.error(`Health check error: ${error}`);
    }
  }

  /**
   * Stop health checks
   */
  stopHealthChecks(): void {
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
      this.healthCheckTimer = undefined;
    }
  }

  /**
   * Stop signaling server
   */
  async stop(): Promise<void> {
    this.stopHealthChecks();

    switch (this.config.processManager) {
      case 'pm2':
        await execAsync('pm2 stop ifswarm-signaling-staging').catch(() => {});
        await execAsync('pm2 delete ifswarm-signaling-staging').catch(() => {});
        break;

      case 'systemd':
        const cfg = this.config.signalingConfig;
        for (let i = 1; i <= cfg.instances; i++) {
          await execAsync(`sudo systemctl stop ifswarm-signaling@${i}.service`).catch(() => {});
        }
        break;

      case 'docker':
        await execAsync('docker stop ifswarm-signaling-staging').catch(() => {});
        await execAsync('docker rm ifswarm-signaling-staging').catch(() => {});
        break;
    }

    await this.logToWitness({
      event: 'signaling_stopped',
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Scale instances (PM2 only)
   */
  async scale(instances: number): Promise<void> {
    if (this.config.processManager !== 'pm2') {
      throw new Error('Auto-scaling only supported with PM2');
    }

    if (instances < this.config.signalingConfig.minInstances) {
      instances = this.config.signalingConfig.minInstances;
    }

    if (instances > this.config.signalingConfig.maxInstances) {
      instances = this.config.signalingConfig.maxInstances;
    }

    await execAsync(`pm2 scale ifswarm-signaling-staging ${instances}`);

    await this.logToWitness({
      event: 'signaling_scaled',
      timestamp: new Date().toISOString(),
      metadata: {
        instances
      }
    });

    console.log(`✓ Scaled to ${instances} instances`);
  }

  /**
   * Get status
   */
  async getStatus(): Promise<{
    running: boolean;
    instances: number;
    details: string;
  }> {
    try {
      switch (this.config.processManager) {
        case 'pm2': {
          const { stdout } = await execAsync('pm2 jlist');
          const processes = JSON.parse(stdout);
          const signalingProcesses = processes.filter((p: any) => p.name === 'ifswarm-signaling-staging');
          return {
            running: signalingProcesses.length > 0,
            instances: signalingProcesses.length,
            details: JSON.stringify(signalingProcesses, null, 2)
          };
        }

        case 'systemd': {
          const { stdout } = await execAsync('sudo systemctl status ifswarm-signaling@*.service --no-pager');
          return {
            running: stdout.includes('active (running)'),
            instances: (stdout.match(/active \(running\)/g) || []).length,
            details: stdout
          };
        }

        case 'docker': {
          const { stdout } = await execAsync('docker ps --filter name=ifswarm-signaling-staging');
          return {
            running: stdout.includes('ifswarm-signaling-staging'),
            instances: 1,
            details: stdout
          };
        }

        default:
          return {
            running: false,
            instances: 0,
            details: 'Unknown process manager'
          };
      }
    } catch (error) {
      return {
        running: false,
        instances: 0,
        details: String(error)
      };
    }
  }

  /**
   * Log to IF.witness
   */
  private async logToWitness(event: WitnessEvent): Promise<void> {
    if (this.witnessLogger) {
      await this.witnessLogger(event);
    } else {
      console.log(`[IF.witness] ${event.event}:`, event.metadata || {});
    }
  }
}

/**
 * Main entry point (if run directly)
 */
if (import.meta.url === `file://${process.argv[1]}`) {
  // Default staging configuration
  const stagingConfig: DeploymentConfig = {
    environment: 'staging',
    processManager: 'pm2', // or 'systemd' or 'docker'
    autoScaling: true,
    loadBalancer: true,
    healthCheckInterval: 30000, // 30 seconds
    signalingConfig: {
      port: 8443,
      host: '0.0.0.0',
      instances: 2,
      minInstances: 1,
      maxInstances: 5,
      redisUrl: process.env.REDIS_URL || 'redis://localhost:6379',
      witnessLoggerUrl: process.env.WITNESS_LOGGER_URL,
      tlsCertPath: process.env.TLS_CERT_PATH,
      tlsKeyPath: process.env.TLS_KEY_PATH
    },
    nginxConfig: {
      upstreamName: 'ifswarm_signaling',
      serverName: 'signaling.ifswarm.staging',
      listenPort: 80,
      listenPortSSL: 443,
      backends: [
        { host: 'localhost', port: 8443 },
        { host: 'localhost', port: 8444 }
      ],
      sslCertPath: process.env.SSL_CERT_PATH,
      sslKeyPath: process.env.SSL_KEY_PATH
    }
  };

  const deployment = new SignalingDeployment(stagingConfig);

  deployment.deploy().catch((error) => {
    console.error('Deployment failed:', error);
    process.exit(1);
  });

  // Graceful shutdown
  process.on('SIGINT', async () => {
    console.log('\nShutting down...');
    await deployment.stop();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    console.log('\nShutting down...');
    await deployment.stop();
    process.exit(0);
  });
}
