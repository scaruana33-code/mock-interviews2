# Power BI Dataflows - Activity Tracking

This directory contains Power BI dataflow configurations for tracking and visualizing development activity, including session metrics, file edits, git activity, task progress, and tool execution statistics.

## Directory Structure

```
powerbi/
├── dataflows/
│   └── ActivityDataflow.json          # Main dataflow definition
├── data-sources/
│   ├── session-activity.json          # Session activity records
│   ├── file-edits.json                # File modification tracking
│   ├── git-activity.json              # Git commit and branch data
│   ├── task-activity.json             # Task completion metrics
│   └── tool-executions.json           # Tool execution logs
└── README.md                           # This file
```

## Dataflow Overview

The **ActivityDataflow** orchestrates five interconnected data entities:

### 1. **SessionActivity**
Tracks core session-level metrics and activity types.

**Key Columns:**
- `SessionId` (PK): Unique session identifier
- `SessionName`: Human-readable session name
- `Timestamp`: Session start time
- `ActivityType`: Type of activity (editing, review, testing, debugging, documentation)
- `Duration`: Session duration in seconds
- `UserName`: User who conducted the session
- `Repository`: Target repository
- `Branch`: Working branch
- `Status`: Current status (active, completed)

**Transformations:**
- Filters for active and completed sessions only
- Derives `ActivityDate` from timestamp
- Extracts `ActivityHour` for hourly distribution analysis

### 2. **FileEdits**
Tracks all file modifications within sessions.

**Key Columns:**
- `EditId` (PK): Unique edit identifier
- `SessionId` (FK): Links to SessionActivity
- `FilePath`: Path to modified file
- `FileType`: File extension/type (json, markdown, html, etc.)
- `ChangeType`: Operation type (create, modify, delete)
- `LinesAdded`: Lines added in change
- `LinesRemoved`: Lines removed in change
- `Timestamp`: When the edit occurred

**Transformations:**
- Calculates `NetLinesChanged` (added - removed)
- Groups statistics by file type with totals

### 3. **GitActivity**
Captures git commits and branch operations.

**Key Columns:**
- `CommitId` (PK): Commit hash
- `CommitMessage`: Commit message
- `AuthorName`: Commit author
- `CommitDate`: Commit timestamp
- `FilesChanged`: Number of files in commit
- `Insertions`: Total lines inserted
- `Deletions`: Total lines deleted
- `Branch`: Target branch

**Transformations:**
- Derives `CommitDay` for daily aggregation
- Calculates `CommitWeek` for weekly trends

### 4. **TaskActivity**
Tracks task creation, progress, and completion.

**Key Columns:**
- `TaskId` (PK): Unique task identifier
- `TaskTitle`: Task description
- `Status`: Current status (pending, in_progress, done, blocked)
- `CreatedDate`: Task creation timestamp
- `CompletedDate`: Task completion timestamp
- `TimeToComplete`: Seconds from creation to completion
- `Priority`: Task priority (high, medium, low)
- `Category`: Task category (analytics, infrastructure, reporting, documentation)

**Transformations:**
- Filters to show completed tasks only
- Flags overdue tasks (completion time > 28,800 seconds / 8 hours)

### 5. **ToolExecutions**
Logs all tool and command executions within sessions.

**Key Columns:**
- `ExecutionId` (PK): Unique execution identifier
- `SessionId` (FK): Links to SessionActivity
- `ToolName`: Name of tool executed (grep, git, powershell, etc.)
- `ExecutionTime`: Execution duration in milliseconds
- `Success`: Boolean success/failure indicator
- `ExecutedAt`: Execution timestamp
- `ToolType`: Category (file-operation, search, command, vcs)

**Transformations:**
- Derives `ExecutionStatus` (Success/Failed)
- Groups statistics by tool with average execution times

## Data Relationships

```
SessionActivity (1) ─── (Many) FileEdits
SessionActivity (1) ─── (Many) ToolExecutions
GitActivity (independent)
TaskActivity (independent)
```

## Refresh Schedule

The dataflow is configured to refresh **hourly** starting at 08:00 AM daily, ensuring real-time activity tracking with a 1-hour cadence.

## Key Metrics & KPIs

### Session-Level KPIs
- **Total Sessions**: Count of distinct sessions
- **Avg Session Duration**: Average time per session
- **Activity Type Distribution**: Breakdown by activity type
- **Active Sessions**: Sessions with status = 'active'
- **Completion Rate**: Completed sessions / total sessions

### File Edit Metrics
- **Total Files Edited**: Distinct file count
- **Lines of Code Changed**: Total additions - deletions
- **File Type Distribution**: Activity by file type
- **Average Edit Size**: Avg lines changed per edit
- **Most Edited Files**: Ranked by modification count

### Git Activity Metrics
- **Total Commits**: Count of all commits
- **Avg Commit Size**: Average files/insertions per commit
- **Commits by Branch**: Distribution across branches
- **Code Churn**: Total insertions + deletions
- **Commit Frequency**: Commits per day/week

### Task Metrics
- **Task Completion Rate**: Completed / total tasks
- **Avg Task Duration**: Average time to complete
- **Overdue Task **: Tasks exceeding 8-hour completion threshold
- **Tasks by Priority**: Distribution across priority levels
- **Tasks by Category**: Breakdown by task type

### Tool Usage Metrics
- **Total Tool Executions**: Count of tool runs
- **Execution Success Rate**: Successful / total executions
- **Tool Frequency**: Most commonly used tools
- **Avg Execution Time**: Average duration by tool
- **Failed Executions**: Count and tools with failures

## Using the Dataflow

### In Power BI Desktop:
1. Open Power BI Desktop
2. Get Data → Web (or JSON)
3. Load the `ActivityDataflow.json` file
4. The dataflow will automatically establish relationships between entities
5. Create visualizations using the pre-processed data

### Recommended Visualizations:

**Session Analytics Dashboard:**
- Activity timeline (line chart by date/hour)
- Session duration by type (bar chart)
- User activity heatmap (activity × hour)
- Branch distribution (pie chart)

**Development Productivity Dashboard:**
- File edits over time (area chart)
- Code churn by file type (stacked bar)
- Commits per branch (clustered bar)
- Top 10 edited files (horizontal bar)

**Task & Quality Dashboard:**
- Task completion funnel
- Avg time to complete by category
- Overdue task indicators
- Priority distribution

**Tool Performance Dashboard:**
- Execution success rate gauge
- Tool usage frequency (horizontal bar)
- Execution time by tool (scatter)
- Failed execution log table

## Data Source Locations

All data sources are JSON files in the `data-sources/` directory:

- **Session Activity**: `data-sources/session-activity.json`
- **File Edits**: `data-sources/file-edits.json`
- **Git Activity**: `data-sources/git-activity.json`
- **Task Activity**: `data-sources/task-activity.json`
- **Tool Executions**: `data-sources/tool-executions.json`

These files can be:
- Replaced with live data connectors (Azure DevOps, GitHub API, etc.)
- Connected to a database (SQL Server, PostgreSQL)
- Updated via Azure Data Factory pipelines
- Synced from cloud storage (Azure Blob, AWS S3)

## Configuration Options

### Update Refresh Frequency:
Edit `ActivityDataflow.json` line ~245:
```json
"refreshSchedule": {
  "frequency": "Hourly",  // "Hourly", "Daily", "Weekly"
  "interval": 1,
  "startTime": "08:00:00"
}
```

### Add New Data Source:
1. Create new JSON file in `data-sources/`
2. Define entity in `entities` array of `ActivityDataflow.json`
3. Add transformations and relationships as needed
4. Publish updated dataflow

### Modify Transformations:
Edit transformation objects within each entity to:
- Filter records
- Add calculated columns
- Group and aggregate data
- Merge datasets

## Integration Examples

### GitHub API Integration
Connect to real GitHub data:
```json
"source": {
  "type": "api",
  "endpoint": "https://api.github.com/repos/{owner}/{repo}/commits",
  "authentication": "token"
}
```

### SQL Server Integration
Pull from database:
```json
"source": {
  "type": "sql",
  "server": "sqlserver.example.com",
  "database": "ActivityDB",
  "query": "SELECT * FROM SessionActivity"
}
```

### Azure DevOps Integration
Connect work items and activities:
```json
"source": {
  "type": "azuredevops",
  "organization": "myorg",
  "project": "myproject",
  "entity": "workitems"
}
```

## Sample Data

Sample JSON files are included with realistic test data for 5 sessions across 3 days. To populate with real data:

1. Connect to actual data sources via API or database queries
2. Use Azure Data Factory to orchestrate ETL
3. Schedule pipeline runs to refresh hourly
4. Monitor data quality metrics

## Troubleshooting

**Issue**: Dataflow fails to load
- **Solution**: Verify all data source files are present and valid JSON

**Issue**: Relationships not auto-created
- **Solution**: Ensure foreign key columns have matching names and data types

**Issue**: Transformation errors
- **Solution**: Check column names match exactly in filter/groupBy expressions

**Issue**: Slow refresh performance
- **Solution**: Add date filters to data sources to limit historical data volume

## Next Steps

1. **Connect Live Data**: Replace JSON files with live API/database connections
2. **Build Dashboard**: Create reports and visualizations in Power BI
3. **Set Alerts**: Configure data alerts for key metrics (e.g., task delays, failed tools)
4. **Schedule Exports**: Export reports to PowerPoint or email on schedule
5. **Monitor Quality**: Track data freshness and reconcile with source systems

## Contact & Support

For questions about the dataflow architecture or data definitions, refer to the Power BI documentation or your organization's data governance team.

---

**Created**: 2026-09-03  
**Version**: 1.0.0  
**Status**: Production Ready
