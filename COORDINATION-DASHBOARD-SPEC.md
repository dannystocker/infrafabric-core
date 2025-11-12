# Real-Time Coordination Dashboard Specification

## Overview

A real-time monitoring and coordination dashboard for managing 7 parallel AI sessions working on InfraFabric project tasks. Provides live visibility into session health, task execution, progress tracking, cost management, and critical path monitoring.

## Dashboard Panels

### 1. Live Session Status
**Purpose**: Monitor health and activity of all 7 concurrent sessions

**Display Elements**:
- Grid layout showing all 7 sessions (Session A-G)
- Per-session indicators:
  - Session ID and name
  - Current status (ACTIVE, IDLE, WORKING, ERROR, OFFLINE)
  - Last heartbeat timestamp
  - Uptime duration
  - Current task (if any)
  - Session coordinator name
- Color coding:
  - Green: Active and healthy (heartbeat <30s)
  - Yellow: Warning (heartbeat 30s-5min)
  - Red: Critical (heartbeat >5min or error state)
  - Gray: Offline/Disconnected

**Data Source**: `sessions/session-{A-G}/STATUS.yaml` - `lastHeartbeat`, `status`, `currentTask`

**Update Frequency**: 30 seconds (synchronized with session heartbeat)

---

### 2. Task Board State
**Purpose**: Real-time view of task distribution and status across all sessions

**Display Elements**:
- Kanban-style board with columns:
  - **Available** (Ready to claim)
  - **Claimed** (Assigned but not started)
  - **In Progress** (Actively being worked)
  - **Blocked** (Waiting on dependencies)
  - **Completed** (Finished)
- Task cards showing:
  - Task ID and name
  - Assigned session
  - Duration/elapsed time
  - Dependencies
  - Priority level
- Card count per column
- Drag-and-drop capability (optional)

**Data Source**: `TASK-BOARD.yaml` - `tasks` array with status field

**Update Frequency**: 30 seconds

---

### 3. Progress Bars per Phase
**Purpose**: Visual representation of completion percentage for each project phase

**Display Elements**:
- Horizontal progress bars for each phase:
  - Phase 1: Foundation Setup
  - Phase 2: Core Services
  - Phase 3: Advanced Features
  - Phase 4: Integration & Testing
- Per bar metrics:
  - Percentage complete (tasks completed / total tasks)
  - Tasks completed count (e.g., "12/20")
  - Estimated completion time
  - Behind/ahead of schedule indicator
- Overall project progress bar at top

**Data Source**: `TASK-BOARD.yaml` - aggregate task status by phase tags

**Update Frequency**: 30 seconds

---

### 4. Cost Tracking
**Purpose**: Monitor API costs in real-time to prevent budget overruns

**Display Elements**:
- **Total Cost Meter**: Large display showing cumulative cost
- **Per-Session Breakdown**:
  - Session ID
  - Current session cost
  - Cost rate ($/hour)
  - Percentage of budget used
- **Budget Indicators**:
  - Total budget allocation
  - Remaining budget
  - Projected final cost (based on current rate)
  - Burn rate graph (cost over time)
- **Cost Efficiency Metrics**:
  - Cost per task completed
  - Cost per hour
  - Most/least cost-efficient sessions

**Data Source**: `sessions/session-{A-G}/COST-TRACKING.yaml` - `totalCost`, `sessionCosts`

**Update Frequency**: 60 seconds (cost updates are less frequent)

---

### 5. Timeline/Gantt View
**Purpose**: Visualize task scheduling, dependencies, and timeline

**Display Elements**:
- Gantt chart with:
  - Time axis (hours/days)
  - Task bars showing:
    - Start time
    - Duration
    - End time (actual or estimated)
  - Dependencies (arrows between tasks)
  - Critical path highlighted (red)
  - Milestones (diamond markers)
  - Current time indicator (vertical line)
- Session swim lanes (group by assigned session)
- Zoom controls (hour/day/week view)

**Data Source**:
- `TASK-BOARD.yaml` - task timing, dependencies
- `PROJECT-TIMELINE.yaml` - milestones, phase dates

**Update Frequency**: 30 seconds (task start/end times)

---

### 6. Critical Path Visualization
**Purpose**: Identify and monitor tasks that directly impact project completion

**Display Elements**:
- **Critical Path Graph**:
  - Network diagram showing task dependencies
  - Critical path tasks highlighted in red
  - Non-critical tasks in gray
  - Slack time displayed on non-critical edges
- **Critical Path Metrics**:
  - Number of tasks on critical path
  - Critical path duration
  - Earliest completion date
  - Latest completion date
- **Risk Indicators**:
  - Tasks at risk of delay
  - Blocker count on critical path
  - Critical path changes over time

**Data Source**: `TASK-BOARD.yaml` - dependencies, calculated critical path

**Update Frequency**: 60 seconds (recomputed as tasks complete)

---

### 7. Blocker Alerts
**Purpose**: Surface and prioritize issues preventing progress

**Display Elements**:
- **Active Blockers List**:
  - Blocker ID and description
  - Affected task(s)
  - Blocked session(s)
  - Duration (how long blocked)
  - Severity (critical/high/medium/low)
  - Assigned resolver
- **Blocker Statistics**:
  - Total active blockers
  - Average resolution time
  - Blockers resolved today
- **Alert Panel**:
  - New blockers (last 5 minutes)
  - Escalated blockers (>30 minutes)
  - Critical path blockers
- Sound/visual alerts for new critical blockers

**Data Source**: `BLOCKERS.yaml` - active blockers list

**Update Frequency**: 15 seconds (critical for responsiveness)

---

### 8. Session Health
**Purpose**: Monitor technical health and performance of each session

**Display Elements**:
- **Health Matrix Table**:
  - Session ID
  - Heartbeat status (last ping time)
  - Uptime (session duration)
  - Task completion count
  - Error count
  - Response time (average API latency)
  - Memory/resource usage (if available)
- **Health Score**: Aggregate score per session (0-100)
- **Alerts**:
  - Session timeout warnings (heartbeat >5min)
  - High error rate (>3 errors in last hour)
  - Performance degradation (response time >2x average)
- **Historical Uptime Graph**: 24-hour uptime history per session

**Data Source**:
- `sessions/session-{A-G}/STATUS.yaml` - heartbeat, errors
- `sessions/session-{A-G}/HEALTH-LOG.yaml` - historical metrics

**Update Frequency**: 30 seconds

---

### 9. Milestone Tracker
**Purpose**: Track progress toward major project milestones

**Display Elements**:
- **Milestone Timeline**:
  - Milestone name
  - Target date
  - Completion percentage
  - Status (not started/in progress/completed/at risk)
  - Dependencies/prerequisites
- **Milestone Cards**:
  - Phase milestone
  - Deliverables checklist
  - Acceptance criteria
  - Responsible sessions
  - Completion ETA
- **Progress Indicators**:
  - Days ahead/behind schedule
  - Risk level (based on critical path)
  - Completion forecast

**Data Source**: `PROJECT-TIMELINE.yaml` - milestones, phase definitions

**Update Frequency**: 60 seconds

---

### 10. Performance Metrics
**Purpose**: Measure and optimize team productivity and efficiency

**Display Elements**:
- **Productivity Metrics**:
  - Tasks completed per hour (overall)
  - Tasks completed per session per hour
  - Average task duration
  - Task throughput trend (graph)
- **Cost Efficiency**:
  - Cost per task completed
  - Cost per feature delivered
  - ROI by session
  - Budget utilization efficiency
- **Quality Metrics**:
  - Task rework rate
  - Blocker frequency
  - Error rate per session
  - Review pass/fail rate
- **Comparison Charts**:
  - Session-to-session performance
  - Current vs. target metrics
  - Trend lines (improving/declining)

**Data Source**:
- `TASK-BOARD.yaml` - task completion data
- `sessions/session-{A-G}/COST-TRACKING.yaml` - cost data
- `METRICS.yaml` - aggregated performance metrics

**Update Frequency**: 60 seconds

---

## Data Sources

### Primary Data Files
1. **Task Board**: `/home/user/infrafabric/TASK-BOARD.yaml`
   - Task definitions, status, assignments, dependencies
   - Update frequency: 30s by sessions

2. **Session Status Files**: `/home/user/infrafabric/sessions/session-{A-G}/STATUS.yaml`
   - Session health, heartbeat, current task
   - Update frequency: 30s per session

3. **Cost Tracking**: `/home/user/infrafabric/sessions/session-{A-G}/COST-TRACKING.yaml`
   - Per-session costs, cumulative totals
   - Update frequency: Variable (after API calls)

4. **Blockers**: `/home/user/infrafabric/BLOCKERS.yaml`
   - Active blockers, descriptions, affected tasks
   - Update frequency: As blockers are added/resolved

5. **Project Timeline**: `/home/user/infrafabric/PROJECT-TIMELINE.yaml`
   - Milestones, phase dates, dependencies
   - Update frequency: Less frequent (manual updates)

6. **Metrics**: `/home/user/infrafabric/METRICS.yaml`
   - Aggregated performance and efficiency metrics
   - Update frequency: 60s (computed by dashboard)

### Derived Data
- **Critical Path**: Calculated from TASK-BOARD.yaml dependencies
- **Health Scores**: Computed from STATUS.yaml metrics
- **Trend Lines**: Time-series analysis of historical metrics

---

## Update Frequency

### Polling Strategy
- **Fast Poll (15s)**: Blocker alerts - requires immediate visibility
- **Standard Poll (30s)**: Session status, task board, phase progress - synchronized with session heartbeat
- **Slow Poll (60s)**: Cost tracking, critical path, milestones, performance metrics - less time-sensitive

### Synchronization
- All 7 sessions update STATUS.yaml every 30 seconds
- Dashboard polls on same 30s cycle to maintain consistency
- Offset polling by data source to distribute load:
  - T+0s: Session status files
  - T+10s: Task board
  - T+15s: Blocker alerts
  - T+20s: Cost tracking

### Real-Time Updates (Optional)
- File system watchers (inotify) for instant updates on file changes
- WebSocket connections for push-based updates
- Reduces polling load and improves responsiveness

---

## Alert Thresholds

### Critical Alerts (Immediate Action Required)
- **Session Timeout**: Heartbeat >5 minutes - Session may be crashed
- **Budget Critical**: Total cost >90% of budget - Risk of overrun
- **Critical Path Blocked**: Blocker on critical path task >15 minutes - Threatens timeline
- **Session Error Spike**: >3 errors in 10 minutes - Session instability
- **Zero Available Tasks**: Task board empty with sessions idle - Coordination issue

### Warning Alerts (Monitor Closely)
- **Session Slow**: Heartbeat 2-5 minutes - Potential issues
- **Budget Warning**: Total cost >75% of budget - Approaching limit
- **Task Overdue**: Task duration >2x estimate - May need intervention
- **High Blocker Count**: >5 active blockers - Coordination bottleneck
- **Performance Degradation**: Task completion rate <50% of target - Productivity issue

### Info Alerts (Awareness)
- **Milestone Approaching**: Within 24 hours of milestone - Prepare for review
- **Phase Completion**: Phase progress >95% - Ready to transition
- **Session Restarted**: Session ID changed - Recovery from crash
- **High Utilization**: All sessions actively working - Good throughput
- **Cost Milestone**: Reached 25%/50%/75% of budget - Budget tracking

### Alert Delivery
- **Visual**: Color-coded indicators, flashing elements, modal popups
- **Audio**: Configurable sounds for critical alerts
- **Notifications**: Desktop/browser notifications for off-dashboard alerts
- **Logging**: All alerts logged to `DASHBOARD-ALERTS.log` for post-mortem

---

## Implementation Suggestions

### Option 1: Web UI Dashboard (Recommended)
**Technology Stack**:
- Frontend: React + TypeScript
- Data Visualization: D3.js or Recharts for graphs
- Real-time: WebSocket or polling
- Styling: Tailwind CSS or Material-UI
- Deployment: Served via local Node.js server

**Pros**:
- Rich visualizations (Gantt charts, network graphs)
- Interactive (click to drill down, filter, zoom)
- Cross-platform (access from any browser)
- Easy to share/remote access
- Persistent state

**Cons**:
- Requires web server setup
- More complex implementation
- Higher resource usage

**Implementation Time**: 2-3 days

---

### Option 2: Terminal Dashboard
**Technology Stack**:
- Python + Rich library or Textual framework
- YAML parsing with PyYAML
- Terminal graphics with curses/blessed
- File watching with watchdog

**Pros**:
- Lightweight and fast
- No dependencies beyond Python
- Runs in SSH sessions
- Lower resource usage
- Quick to implement

**Cons**:
- Limited visualization options (no Gantt charts)
- Terminal must stay open
- Less interactive
- Fixed layout

**Implementation Time**: 1 day

---

### Option 3: Hybrid - Terminal + Web Report
**Technology Stack**:
- Terminal: Simple status dashboard (Python + Rich)
- Web: Detailed reports and analytics (Static HTML generation)
- Update mechanism: Cron job generates HTML reports every minute

**Pros**:
- Best of both worlds
- Real-time terminal monitoring
- Detailed web analysis when needed
- No persistent server required

**Cons**:
- Maintain two codebases
- Static web reports (not real-time)

**Implementation Time**: 1.5 days

---

### Option 4: Data Aggregation Service
**Technology Stack**:
- Background service (Python daemon)
- Aggregates data into single DASHBOARD-DATA.json
- Multiple consumers:
  - Terminal client
  - Web UI
  - CLI commands (dashboard status)

**Pros**:
- Centralized data processing
- Multiple visualization options
- Reduces file I/O (read once, serve many)
- Easy to add new clients

**Cons**:
- Additional service to manage
- More complex architecture

**Implementation Time**: 2 days

---

## Technical Architecture

### Data Flow
```
Sessions (A-G)
  ↓ Write every 30s
STATUS.yaml files
  ↓ Poll/Watch
Dashboard Data Aggregator
  ↓ Process & Compute
Dashboard State (JSON/Memory)
  ↓ Render
UI Components (Web/Terminal)
  ↓ Display to
User
```

### File Structure
```
infrafabric/
├── sessions/
│   ├── session-A/
│   │   ├── STATUS.yaml
│   │   ├── COST-TRACKING.yaml
│   │   └── HEALTH-LOG.yaml
│   ├── session-B/ ...
│   └── session-G/ ...
├── TASK-BOARD.yaml
├── BLOCKERS.yaml
├── PROJECT-TIMELINE.yaml
├── METRICS.yaml
├── DASHBOARD-ALERTS.log
└── dashboard/
    ├── aggregator.py          # Data collection service
    ├── web-ui/                # Web dashboard
    ├── terminal-ui/           # Terminal dashboard
    └── config.yaml            # Dashboard configuration
```

### Configuration
**dashboard/config.yaml**:
```yaml
updateFrequency:
  fast: 15        # Blocker alerts
  standard: 30    # Status, tasks
  slow: 60        # Cost, metrics

alerts:
  sessionTimeout: 300         # 5 minutes
  budgetWarning: 0.75        # 75%
  budgetCritical: 0.90       # 90%
  blockerEscalation: 1800    # 30 minutes
  errorThreshold: 3          # errors per 10min

dataSources:
  taskBoard: /home/user/infrafabric/TASK-BOARD.yaml
  blockers: /home/user/infrafabric/BLOCKERS.yaml
  timeline: /home/user/infrafabric/PROJECT-TIMELINE.yaml
  sessions: /home/user/infrafabric/sessions/

display:
  theme: dark                # dark/light
  refreshRate: 30            # UI refresh (seconds)
  soundAlerts: true          # Enable audio alerts
  compactMode: false         # Compact layout
```

---

## Key Features

### 1. Critical Path Intelligence
- Automatic critical path calculation using CPM algorithm
- Real-time updates as tasks complete
- Slack time visualization for scheduling flexibility
- What-if scenario analysis (optional)

### 2. Predictive Analytics
- Completion time forecasting based on current velocity
- Budget projection using cost trends
- Risk assessment for timeline delays
- Bottleneck identification

### 3. Coordination Intelligence
- Idle session detection (no assigned task)
- Task recommendation engine (suggest tasks to idle sessions)
- Load balancing alerts (uneven task distribution)
- Dependency chain optimization

### 4. Historical Tracking
- Session performance over time
- Cost trends and anomalies
- Task completion velocity graphs
- Blocker resolution patterns

### 5. Export and Reporting
- Export dashboard state to JSON
- Generate progress reports (daily/weekly)
- Cost summary reports
- Performance analytics CSV

---

## Success Metrics

Dashboard is successful if it enables:
1. **Fast Reaction**: Critical issues detected and resolved within 5 minutes
2. **Cost Control**: Zero budget overruns, 95%+ budget accuracy
3. **Timeline Adherence**: Project milestones met within 10% variance
4. **High Utilization**: Sessions productive >80% of time (not idle/blocked)
5. **Coordination Efficiency**: <5% task conflicts, minimal duplicate work
6. **Visibility**: All stakeholders can assess project status in <30 seconds

---

## Implementation Phases

### Phase 1: Core Monitoring (Day 1)
- Session status panel
- Task board state
- Basic cost tracking
- File polling infrastructure

### Phase 2: Analytics (Day 2)
- Progress bars and phase tracking
- Performance metrics
- Critical path calculation
- Alert system

### Phase 3: Advanced Visualizations (Day 3)
- Gantt chart/timeline view
- Critical path graph
- Session health dashboard
- Milestone tracker

### Phase 4: Polish (Day 4)
- Alert threshold tuning
- UI/UX improvements
- Documentation
- Performance optimization

---

## Recommended Quick Start

**Best Approach for Immediate Value**:
1. **Start with Terminal Dashboard** (4 hours)
   - Implement panels 1, 2, 3, 4, 7, 8
   - Basic polling every 30s
   - Simple color-coded status

2. **Add Web Reports** (2 hours)
   - Static HTML generation for panels 5, 6, 9, 10
   - Generated every 60s
   - Open in browser for detailed analysis

3. **Iterate Based on Usage** (ongoing)
   - Add features as needs emerge
   - Upgrade to full web UI if needed
   - Enhance analytics over time

This gets a functional dashboard running in <1 day while keeping implementation simple.

---

## Appendix: Sample Alert Logic

```python
def check_alerts(dashboard_state):
    alerts = []

    # Session timeout
    for session in dashboard_state['sessions']:
        if session['heartbeat_age'] > 300:  # 5 minutes
            alerts.append({
                'severity': 'CRITICAL',
                'type': 'SESSION_TIMEOUT',
                'session': session['id'],
                'message': f"Session {session['id']} has not responded in {session['heartbeat_age']}s"
            })

    # Budget alerts
    budget_used = dashboard_state['cost']['total'] / dashboard_state['cost']['budget']
    if budget_used > 0.90:
        alerts.append({
            'severity': 'CRITICAL',
            'type': 'BUDGET_CRITICAL',
            'message': f"Budget {budget_used*100:.1f}% used - {dashboard_state['cost']['remaining']} remaining"
        })
    elif budget_used > 0.75:
        alerts.append({
            'severity': 'WARNING',
            'type': 'BUDGET_WARNING',
            'message': f"Budget {budget_used*100:.1f}% used"
        })

    # Critical path blockers
    for blocker in dashboard_state['blockers']:
        if blocker['on_critical_path'] and blocker['duration'] > 900:  # 15 min
            alerts.append({
                'severity': 'CRITICAL',
                'type': 'CRITICAL_PATH_BLOCKED',
                'blocker_id': blocker['id'],
                'message': f"Critical path blocked by {blocker['id']} for {blocker['duration']}s"
            })

    return alerts
```

---

**End of Specification**
