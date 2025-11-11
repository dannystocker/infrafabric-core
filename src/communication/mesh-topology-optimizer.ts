/**
 * Mesh Topology Optimizer for IF.swarm
 *
 * Purpose:
 * - Build partial mesh topologies (k-neighbors) for large agent swarms
 * - Analyze graph properties (diameter, clustering coefficient)
 * - Optimize routing paths (shortest path)
 * - Balance connection load across agents
 *
 * Philosophy:
 * - Scalability: O(N*k) connections instead of O(N²)
 * - Efficiency: Minimize routing hops while maintaining connectivity
 * - Fairness: Balanced connection load across agents
 *
 * Topology Types:
 * 1. Full Mesh: N*(N-1)/2 connections - only practical for small N (<10)
 * 2. Partial Mesh (k-neighbors): Each agent connects to k random peers
 * 3. Hub-Spoke: Central hub with spoke connections
 * 4. Ring: Circular topology with neighbor connections
 */

/**
 * Graph edge representation
 */
export interface GraphEdge {
  from: string;
  to: string;
  weight?: number; // Optional weight for routing optimization
}

/**
 * Topology configuration
 */
export interface TopologyConfig {
  agentIds: string[];
  topologyType: 'full-mesh' | 'partial-mesh' | 'hub-spoke' | 'ring';
  k?: number; // Number of neighbors for partial mesh (default: 20)
  hubId?: string; // Hub agent ID for hub-spoke topology
  bidirectional?: boolean; // Whether connections are bidirectional (default: true)
}

/**
 * Graph properties analysis
 */
export interface GraphProperties {
  nodeCount: number;
  edgeCount: number;
  avgDegree: number; // Average connections per node
  diameter: number; // Maximum shortest path length
  avgPathLength: number; // Average shortest path length
  clusteringCoefficient: number; // Measure of how clustered the graph is
  isConnected: boolean; // Whether graph is fully connected
  components: string[][]; // Connected components
}

/**
 * Routing table entry
 */
export interface RoutingEntry {
  destination: string;
  nextHop: string;
  hopCount: number;
  path: string[]; // Full path from source to destination
}

/**
 * Mesh Topology Optimizer
 *
 * Implements algorithms for building and analyzing mesh topologies:
 * - K-neighbors partial mesh construction
 * - Graph analysis (diameter, clustering, connectivity)
 * - Shortest path routing
 * - Load balancing optimization
 */
export class MeshTopologyOptimizer {
  private agentIds: string[];
  private adjacencyList: Map<string, Set<string>>; // Agent ID -> Set of neighbor IDs
  private edges: GraphEdge[];

  constructor() {
    this.agentIds = [];
    this.adjacencyList = new Map();
    this.edges = [];
  }

  /**
   * Build topology based on configuration
   */
  buildTopology(config: TopologyConfig): GraphEdge[] {
    this.agentIds = config.agentIds;
    this.adjacencyList.clear();
    this.edges = [];

    // Initialize adjacency list
    for (const agentId of this.agentIds) {
      this.adjacencyList.set(agentId, new Set());
    }

    switch (config.topologyType) {
      case 'full-mesh':
        this.buildFullMesh();
        break;
      case 'partial-mesh':
        this.buildPartialMesh(config.k || 20);
        break;
      case 'hub-spoke':
        this.buildHubSpoke(config.hubId);
        break;
      case 'ring':
        this.buildRing();
        break;
      default:
        throw new Error(`Unknown topology type: ${config.topologyType}`);
    }

    return this.edges;
  }

  /**
   * Build full mesh topology
   * Connections: N*(N-1)/2
   */
  private buildFullMesh(): void {
    for (let i = 0; i < this.agentIds.length; i++) {
      for (let j = i + 1; j < this.agentIds.length; j++) {
        this.addEdge(this.agentIds[i], this.agentIds[j]);
      }
    }
  }

  /**
   * Build partial mesh topology (k-neighbors)
   * Each agent connects to k random peers
   * Ensures connectivity while minimizing connections
   */
  private buildPartialMesh(k: number): void {
    const n = this.agentIds.length;

    // Ensure k is reasonable
    if (k >= n) {
      // If k >= n, just build full mesh
      this.buildFullMesh();
      return;
    }

    // Ensure minimum connectivity: k >= 2
    const minK = Math.max(2, Math.min(k, n - 1));

    for (let i = 0; i < n; i++) {
      const agentId = this.agentIds[i];
      const neighbors = this.adjacencyList.get(agentId)!;

      // Calculate how many more connections this agent needs
      const needConnections = minK - neighbors.size;

      if (needConnections <= 0) {
        continue; // Agent already has enough connections
      }

      // Get list of potential peers (not self, not already connected)
      const potentialPeers = this.agentIds.filter(
        (peerId, peerIdx) =>
          peerIdx !== i &&
          !neighbors.has(peerId) &&
          this.adjacencyList.get(peerId)!.size < minK
      );

      // Shuffle potential peers for randomness
      this.shuffle(potentialPeers);

      // Connect to random peers
      for (let j = 0; j < Math.min(needConnections, potentialPeers.length); j++) {
        this.addEdge(agentId, potentialPeers[j]);
      }
    }

    // Second pass: ensure all agents have at least minK connections
    for (let i = 0; i < n; i++) {
      const agentId = this.agentIds[i];
      const neighbors = this.adjacencyList.get(agentId)!;

      if (neighbors.size < minK) {
        // Find any available peers
        const availablePeers = this.agentIds.filter(
          (peerId, peerIdx) => peerIdx !== i && !neighbors.has(peerId)
        );

        this.shuffle(availablePeers);

        for (
          let j = 0;
          j < Math.min(minK - neighbors.size, availablePeers.length);
          j++
        ) {
          this.addEdge(agentId, availablePeers[j]);
        }
      }
    }
  }

  /**
   * Build hub-spoke topology
   * One central hub connected to all agents
   */
  private buildHubSpoke(hubId?: string): void {
    if (!hubId) {
      // Use first agent as hub
      hubId = this.agentIds[0];
    }

    if (!this.agentIds.includes(hubId)) {
      throw new Error(`Hub agent ${hubId} not found in agent list`);
    }

    for (const agentId of this.agentIds) {
      if (agentId !== hubId) {
        this.addEdge(hubId, agentId);
      }
    }
  }

  /**
   * Build ring topology
   * Each agent connects to its neighbors in a circle
   */
  private buildRing(): void {
    const n = this.agentIds.length;

    for (let i = 0; i < n; i++) {
      const nextIdx = (i + 1) % n;
      this.addEdge(this.agentIds[i], this.agentIds[nextIdx]);
    }
  }

  /**
   * Add bidirectional edge between two agents
   */
  private addEdge(from: string, to: string): void {
    // Add to adjacency list (bidirectional)
    this.adjacencyList.get(from)!.add(to);
    this.adjacencyList.get(to)!.add(from);

    // Add to edges list (store once)
    this.edges.push({ from, to });
  }

  /**
   * Fisher-Yates shuffle algorithm
   */
  private shuffle<T>(array: T[]): void {
    for (let i = array.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
    }
  }

  /**
   * Analyze graph properties
   */
  analyzeGraph(): GraphProperties {
    const nodeCount = this.agentIds.length;
    const edgeCount = this.edges.length;
    const avgDegree = nodeCount > 0 ? (2 * edgeCount) / nodeCount : 0;

    // Find connected components using DFS
    const visited = new Set<string>();
    const components: string[][] = [];

    for (const agentId of this.agentIds) {
      if (!visited.has(agentId)) {
        const component = this.dfs(agentId, visited);
        components.push(component);
      }
    }

    const isConnected = components.length === 1;

    // Calculate diameter and average path length
    let diameter = 0;
    let totalPathLength = 0;
    let pathCount = 0;

    if (isConnected) {
      for (const source of this.agentIds) {
        const distances = this.bfs(source);
        for (const [target, distance] of distances.entries()) {
          if (source !== target && distance !== Infinity) {
            diameter = Math.max(diameter, distance);
            totalPathLength += distance;
            pathCount++;
          }
        }
      }
    }

    const avgPathLength = pathCount > 0 ? totalPathLength / pathCount : 0;

    // Calculate clustering coefficient
    const clusteringCoefficient = this.calculateClusteringCoefficient();

    return {
      nodeCount,
      edgeCount,
      avgDegree,
      diameter,
      avgPathLength,
      clusteringCoefficient,
      isConnected,
      components
    };
  }

  /**
   * Depth-first search to find connected component
   */
  private dfs(start: string, visited: Set<string>): string[] {
    const component: string[] = [];
    const stack = [start];

    while (stack.length > 0) {
      const node = stack.pop()!;
      if (visited.has(node)) {
        continue;
      }

      visited.add(node);
      component.push(node);

      const neighbors = this.adjacencyList.get(node);
      if (neighbors) {
        for (const neighbor of neighbors) {
          if (!visited.has(neighbor)) {
            stack.push(neighbor);
          }
        }
      }
    }

    return component;
  }

  /**
   * Breadth-first search to calculate shortest paths
   */
  private bfs(start: string): Map<string, number> {
    const distances = new Map<string, number>();
    const queue: string[] = [start];
    distances.set(start, 0);

    while (queue.length > 0) {
      const node = queue.shift()!;
      const currentDistance = distances.get(node)!;

      const neighbors = this.adjacencyList.get(node);
      if (neighbors) {
        for (const neighbor of neighbors) {
          if (!distances.has(neighbor)) {
            distances.set(neighbor, currentDistance + 1);
            queue.push(neighbor);
          }
        }
      }
    }

    // Set unreachable nodes to Infinity
    for (const agentId of this.agentIds) {
      if (!distances.has(agentId)) {
        distances.set(agentId, Infinity);
      }
    }

    return distances;
  }

  /**
   * Calculate clustering coefficient
   * Measures how well connected the neighbors of each node are
   */
  private calculateClusteringCoefficient(): number {
    let totalCoefficient = 0;
    let nodeCount = 0;

    for (const agentId of this.agentIds) {
      const neighbors = Array.from(this.adjacencyList.get(agentId)!);
      const k = neighbors.length;

      if (k < 2) {
        continue; // Need at least 2 neighbors to form triangles
      }

      // Count edges between neighbors
      let edgeCount = 0;
      for (let i = 0; i < neighbors.length; i++) {
        for (let j = i + 1; j < neighbors.length; j++) {
          if (this.adjacencyList.get(neighbors[i])!.has(neighbors[j])) {
            edgeCount++;
          }
        }
      }

      // Clustering coefficient for this node
      const maxEdges = (k * (k - 1)) / 2;
      const coefficient = maxEdges > 0 ? edgeCount / maxEdges : 0;

      totalCoefficient += coefficient;
      nodeCount++;
    }

    return nodeCount > 0 ? totalCoefficient / nodeCount : 0;
  }

  /**
   * Build routing table for an agent using shortest paths
   */
  buildRoutingTable(sourceAgentId: string): Map<string, RoutingEntry> {
    const routingTable = new Map<string, RoutingEntry>();

    // BFS with path tracking
    const queue: Array<{ node: string; path: string[] }> = [
      { node: sourceAgentId, path: [sourceAgentId] }
    ];
    const visited = new Set<string>([sourceAgentId]);

    while (queue.length > 0) {
      const { node, path } = queue.shift()!;

      const neighbors = this.adjacencyList.get(node);
      if (neighbors) {
        for (const neighbor of neighbors) {
          if (!visited.has(neighbor)) {
            visited.add(neighbor);
            const newPath = [...path, neighbor];

            // Add routing entry
            routingTable.set(neighbor, {
              destination: neighbor,
              nextHop: path.length === 1 ? neighbor : path[1], // Next hop from source
              hopCount: newPath.length - 1,
              path: newPath
            });

            queue.push({ node: neighbor, path: newPath });
          }
        }
      }
    }

    return routingTable;
  }

  /**
   * Get neighbors for an agent
   */
  getNeighbors(agentId: string): string[] {
    const neighbors = this.adjacencyList.get(agentId);
    return neighbors ? Array.from(neighbors) : [];
  }

  /**
   * Get all edges
   */
  getEdges(): GraphEdge[] {
    return this.edges;
  }

  /**
   * Get connection degree distribution
   */
  getDegreeDistribution(): Map<number, number> {
    const distribution = new Map<number, number>();

    for (const agentId of this.agentIds) {
      const degree = this.adjacencyList.get(agentId)!.size;
      distribution.set(degree, (distribution.get(degree) || 0) + 1);
    }

    return distribution;
  }

  /**
   * Balance connection load
   * Ensures all agents have similar number of connections
   */
  balanceLoad(targetDegree: number): void {
    // Find agents with too many or too few connections
    const overloaded: string[] = [];
    const underloaded: string[] = [];

    for (const agentId of this.agentIds) {
      const degree = this.adjacencyList.get(agentId)!.size;
      if (degree > targetDegree) {
        overloaded.push(agentId);
      } else if (degree < targetDegree) {
        underloaded.push(agentId);
      }
    }

    // Rebalance by removing edges from overloaded and adding to underloaded
    for (const overAgent of overloaded) {
      const neighbors = Array.from(this.adjacencyList.get(overAgent)!);
      const removeCount = neighbors.length - targetDegree;

      for (let i = 0; i < removeCount && underloaded.length > 0; i++) {
        const neighborToRemove = neighbors[i];
        const underAgent = underloaded[0];

        // Check if we can move this connection
        if (
          !this.adjacencyList.get(underAgent)!.has(neighborToRemove) &&
          underAgent !== overAgent
        ) {
          // Remove edge from overloaded agent
          this.removeEdge(overAgent, neighborToRemove);

          // Add edge to underloaded agent
          this.addEdge(underAgent, neighborToRemove);

          // Update underloaded list
          if (this.adjacencyList.get(underAgent)!.size >= targetDegree) {
            underloaded.shift();
          }
        }
      }
    }
  }

  /**
   * Remove edge between two agents
   */
  private removeEdge(from: string, to: string): void {
    this.adjacencyList.get(from)?.delete(to);
    this.adjacencyList.get(to)?.delete(from);

    // Remove from edges list
    this.edges = this.edges.filter(
      (edge) =>
        !(
          (edge.from === from && edge.to === to) ||
          (edge.from === to && edge.to === from)
        )
    );
  }

  /**
   * Export topology as DOT format (for visualization with Graphviz)
   */
  exportToDOT(): string {
    let dot = 'graph MeshTopology {\n';
    dot += '  node [shape=circle];\n';

    // Add edges
    for (const edge of this.edges) {
      dot += `  "${edge.from}" -- "${edge.to}";\n`;
    }

    dot += '}\n';
    return dot;
  }

  /**
   * Generate topology report
   */
  generateReport(): string {
    const properties = this.analyzeGraph();
    const degreeDistribution = this.getDegreeDistribution();

    let report = '='.repeat(80) + '\n';
    report += 'MESH TOPOLOGY ANALYSIS REPORT\n';
    report += '='.repeat(80) + '\n\n';

    report += 'Graph Properties:\n';
    report += `  Nodes (Agents):           ${properties.nodeCount}\n`;
    report += `  Edges (Connections):      ${properties.edgeCount}\n`;
    report += `  Average Degree:           ${properties.avgDegree.toFixed(2)}\n`;
    report += `  Diameter:                 ${properties.diameter}\n`;
    report += `  Average Path Length:      ${properties.avgPathLength.toFixed(2)}\n`;
    report += `  Clustering Coefficient:   ${properties.clusteringCoefficient.toFixed(4)}\n`;
    report += `  Connected:                ${properties.isConnected ? 'Yes' : 'No'}\n`;
    report += `  Connected Components:     ${properties.components.length}\n\n`;

    report += 'Degree Distribution:\n';
    const sortedDegrees = Array.from(degreeDistribution.entries()).sort(
      (a, b) => a[0] - b[0]
    );
    for (const [degree, count] of sortedDegrees) {
      const percentage = (count / properties.nodeCount) * 100;
      report += `  Degree ${degree}: ${count} agents (${percentage.toFixed(1)}%)\n`;
    }

    report += '\n';

    // Comparison with full mesh
    if (properties.nodeCount > 0) {
      const fullMeshConnections =
        (properties.nodeCount * (properties.nodeCount - 1)) / 2;
      const connectionReduction =
        ((fullMeshConnections - properties.edgeCount) / fullMeshConnections) *
        100;

      report += 'Scalability Analysis:\n';
      report += `  Full Mesh Connections:    ${fullMeshConnections}\n`;
      report += `  Actual Connections:       ${properties.edgeCount}\n`;
      report += `  Connection Reduction:     ${connectionReduction.toFixed(1)}%\n`;
      report += `  Efficiency Gain:          ${(fullMeshConnections / properties.edgeCount).toFixed(2)}x\n\n`;
    }

    report += '='.repeat(80) + '\n';

    return report;
  }
}

/**
 * Topology utility functions
 */
export class TopologyUtils {
  /**
   * Calculate optimal k for partial mesh
   * Based on network size and desired connectivity
   */
  static calculateOptimalK(
    networkSize: number,
    targetDiameter: number = 3
  ): number {
    // For small networks, use full mesh
    if (networkSize <= 10) {
      return networkSize - 1;
    }

    // For large networks, use empirical formula
    // k ≈ ln(N) for small-world properties
    const lnN = Math.log(networkSize);
    const baseK = Math.ceil(lnN * 2);

    // Ensure minimum connectivity
    const minK = Math.max(3, baseK);

    // Cap at reasonable maximum (20-30 for very large networks)
    const maxK = Math.min(30, networkSize - 1);

    return Math.min(minK, maxK);
  }

  /**
   * Estimate average latency for topology
   * Assumes base P2P latency and additional routing overhead
   */
  static estimateAverageLatency(
    avgPathLength: number,
    baseLatencyMs: number = 50,
    routingOverheadMs: number = 5
  ): number {
    // Latency = base latency + (hops - 1) * routing overhead
    return baseLatencyMs + (avgPathLength - 1) * routingOverheadMs;
  }

  /**
   * Calculate memory overhead for mesh
   * Estimates memory usage per agent based on connection count
   */
  static estimateMemoryOverhead(
    connectionsPerAgent: number,
    baseMemoryMB: number = 10,
    memoryPerConnectionMB: number = 2
  ): number {
    return baseMemoryMB + connectionsPerAgent * memoryPerConnectionMB;
  }
}
