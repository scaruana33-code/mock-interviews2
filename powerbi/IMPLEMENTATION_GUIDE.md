# Power BI Activity Dataflow Implementation Guide

## Quick Start

### Step 1: Verify Files Structure
```
powerbi/
├── dataflows/
│   └── ActivityDataflow.json          ← Main dataflow definition
├── data-sources/
│   ├── session-activity.json          ← 5 sample records
│   ├── file-edits.json                ← 5 sample records
│   ├── git-activity.json              ← 5 sample records
│   ├── task-activity.json             ← 5 sample records
│   └── tool-executions.json           ← 6 sample records
├── models/
│   └── ActivityModel.json             ← DAX measures & semantic model
├── activity_dataflow.py               ← Python data integration script
└── README.md
```

### Step 2: Load into Power BI Desktop

1. Open **Power BI Desktop**
2. Select **Get Data** → **Web**
3. Enter path to `ActivityDataflow.json`
4. Select **Load** (Power BI auto-creates relationships)
5. Create visualizations from the pre-calculated measures

### Step 3: Publish to Power BI Service

1. Click **Publish** in Power BI Desktop
2. Select workspace and dataset name
3. Configure refresh schedule (hourly recommended)
4. Share dashboard with team

---

## Sample Dashboard Layouts

### Dashboard 1: Session Overview
```
┌─────────────────────────────────────┬─────────────────┐
│  Total Sessions (KPI Card)          │ Active Sessions │
│  42 sessions                        │  3              │
├─────────────────────────────────────┼─────────────────┤
│  Session Duration Over Time         │ Activity Type   │
│  (Line Chart: 7-day trend)          │ (Pie Chart)     │
│  │                                  │ • Editing: 60%  │
│  │ ╱╲                               │ • Testing: 20%  │
│  │╱  ╲                              │ • Review: 15%   │
│  └────                              │ • Other: 5%     │
├─────────────────────────────────────┴─────────────────┤
│  Recent Sessions (Table)                              │
│  SessionName | User | Duration | Status | Branch     │
│  refresh(41) | user │ 30m      │ active │ feat/xyz   │
│  code review │ user │ 60m      │ done   │ main       │
└──────────────────────────────────────────────────────┘
```

### Dashboard 2: Development Activity
```
┌─────────────────────────────────────┬─────────────────┐
│  Total Commits (KPI Card)           │ Code Churn      │
│  156 commits                        │ 2,847 lines     │
├─────────────────────────────────────┼─────────────────┤
│  Files Changed Over Time            │ Top File Types  │
│  (Stacked Area: by FileType)        │ (Horizontal Bar)│
│  ▁▂▃▅▆███████                       │ ████ ts   40%   │
│  ▁▂▃▅▆███████                       │ ███ json  30%   │
│  ▁▂▃▅▆███████                       │ ██ md    20%    │
├─────────────────────────────────────┼─────────────────┤
│  Commits by Branch (Pie)            │ Avg Lines/Commit│
│ • main: 45%                         │ 18 lines        │
│ • develop: 35%                      │                 │
│ • feature/*: 20%                    │                 │
└─────────────────────────────────────┴─────────────────┘
```

### Dashboard 3: Task & Quality
```
┌─────────────────────────────────────┬─────────────────┐
│  Task Completion Rate (Gauge)       │ Pending Tasks   │
│  78%                                │  12 tasks       │
├─────────────────────────────────────┼─────────────────┤
│  Tasks by Status (Pie)              │ Time to Complete│
│ • Done: 156 (78%)                   │ (KPI: hours)    │
│ • In Progress: 32 (16%)             │ 4.2h avg        │
│ • Pending: 12 (6%)                  │                 │
├─────────────────────────────────────┼─────────────────┤
│  Overdue Tasks (Table + Alert)      │ Tasks by Priority│
│  Task | Priority | Days Overdue     │ (Clustered Bar) │
│  ⚠ Deploy API  | High  | 2          │ ████ High   40% │
│  ⚠ Docs Update | Med   | 1          │ ███ Medium  35% │
│                                     │ ██ Low      25% │
└─────────────────────────────────────┴─────────────────┘
```

### Dashboard 4: Tool Performance
```
┌─────────────────────────────────────┬─────────────────┐
│  Total Tool Executions (KPI)        │ Success Rate    │
│  1,247 executions                   │  96.2%          │
├─────────────────────────────────────┼─────────────────┤
│  Most Used Tools (Horizontal Bar)   │ Failed Tools    │
│  ███████ view      340 (27%)         │ (Table)         │
│  ██████ edit       210 (17%)         │ Tool | Count    │
│  █████ grep       180 (14%)         │ git  | 12       │
│  ████ powershell  150 (12%)         │ test | 8        │
│  ██ create        100 (8%)          │                 │
│  ██ other        267 (21%)          │                 │
├─────────────────────────────────────┼─────────────────┤
│  Execution Time Trends (Line)       │ Tool Execution  │
│  │ ╱╲                               │ Details (Table) │
│  │╱  ╲                              │ Tool|Time|Status│
│  └──── ╱╲                           │ git |450ms|OK   │
│        ╲                            │ test|850ms|FAIL │
└─────────────────────────────────────┴─────────────────┘
```

---

## Using Python for Data Integration

### Run Validation
```bash
cd powerbi
python activity_dataflow.py --validate

# Output:
# ✓ Session Activity: 5 records
# ✓ File Edits: 5 records
# ✓ Git Activity: 5 records
# ✓ Tool Executions: 6 records
# ✓ Task Activity: 5 records
# ✓ Dataflow validation passed!
```

### Integrate with Real Git Repository
```bash
python activity_dataflow.py --repo . --output powerbi/data-sources
```

### Modify for Custom Data Sources

Edit `activity_dataflow.py`:

```python
# Example: Pull from GitHub API
def generate_session_activity_github(self, org: str, repo: str, token: str):
    import requests
    
    headers = {"Authorization": f"token {token}"}
    
    # Get pull requests as sessions
    url = f"https://api.github.com/repos/{org}/{repo}/pulls?state=all"
    response = requests.get(url, headers=headers)
    
    activity = []
    for pr in response.json():
        activity.append({
            "SessionId": f"pr-{pr['number']}",
            "SessionName": pr['title'],
            "Timestamp": pr['created_at'],
            "ActivityType": "review",
            "Duration": self._calc_duration(pr['created_at'], pr['closed_at']),
            "UserName": pr['user']['login'],
            "Repository": f"{org}/{repo}",
            "Branch": pr['head']['ref'],
            "Status": "completed" if pr['state'] == "closed" else "active"
        })
    
    return activity
```

---

## Advanced Configurations

### Connect to SQL Database
1. In Power BI Desktop: **Get Data** → **SQL Server**
2. Server: `your-server.database.windows.net`
3. Database: `ActivityDB`
4. Edit SQL queries to filter/transform data
5. Create relationships matching the dataflow schema

### Automated Refresh with Azure Data Factory

**Create Pipeline:**
```json
{
  "name": "RefreshActivityDataflow",
  "type": "Microsoft.DataFactory/factories/pipelines",
  "properties": {
    "activities": [
      {
        "name": "ExecuteDataflow",
        "type": "ExecuteDataFlowActivity",
        "dataflow": {
          "referenceName": "ActivityDataflow",
          "type": "DataFlowReference"
        },
        "compute": {
          "coreCount": 4,
          "computeType": "General"
        }
      }
    ],
    "trigger": {
      "type": "ScheduleTrigger",
      "recurrence": {
        "frequency": "Hour",
        "interval": 1
      }
    }
  }
}
```

### Row-Level Security (RLS)

Add to `ActivityModel.json`:
```json
"roles": [
  {
    "name": "Developer",
    "description": "Can see only own session data",
    "filters": [
      {
        "table": "SessionActivity",
        "filter": "[UserName] = USERNAME()"
      }
    ]
  },
  {
    "name": "Manager",
    "description": "Can see all team data",
    "filters": []
  }
]
```

---

## Key Metrics Reference

### Session Metrics
| Metric | Calculation | Example |
|--------|-------------|---------|
| Total Sessions | COUNTA(SessionId) | 42 |
| Active Sessions | Filtered to Status='active' | 3 |
| Avg Duration | AVERAGE(Duration) | 52 min |
| Completion Rate | Completed / Total | 78% |
| Peak Hour | Most sessions by hour | 2-3 PM |

### Development Metrics
| Metric | Calculation | Example |
|--------|-------------|---------|
| Total Commits | COUNTA(CommitId) | 156 |
| Code Churn | SUM(Insertions + Deletions) | 2,847 lines |
| Avg Commit Size | AVG(Files + Insertions + Deletions) | 18 lines |
| Files Changed | DISTINCTCOUNT(FilePath) | 84 files |
| Most Active Branch | MAX commits | main (71) |

### Task Metrics
| Metric | Calculation | Example |
|--------|-------------|---------|
| Task Completion Rate | Done / Total | 78% |
| Avg Time to Complete | AVG(TimeToComplete) | 4.2 hours |
| Overdue Tasks | Filtered to TimeToComplete > 8h | 3 tasks |
| By Priority | COUNT grouped by Priority | High: 40% |
| Blocked Tasks | Filtered to Status='blocked' | 2 tasks |

### Tool Metrics
| Metric | Calculation | Example |
|--------|-------------|---------|
| Success Rate | Successful / Total | 96.2% |
| Most Used Tool | Top by execution count | view (27%) |
| Avg Execution Time | AVERAGE(ExecutionTime) | 320 ms |
| Failed Executions | Filtered to Success=FALSE | 47 |
| Tools by Type | Grouped by ToolType | 12 different |

---

## Troubleshooting

### Issue: Relationships Not Auto-Created
**Solution**: Verify column names match exactly:
- SessionActivity.SessionId = FileEdits.SessionId
- SessionActivity.SessionId = ToolExecutions.SessionId

### Issue: Empty Tables
**Solution**: Check file paths in `ActivityDataflow.json`:
```json
"source": {
  "type": "json",
  "path": "session-activity.json"  ← Must match actual filename
}
```

### Issue: Slow Refresh
**Solution**: Add date filters to recent data only:
```python
"filter": "[Timestamp] > DATEADD(DAY, -30, TODAY())"
```

### Issue: Data Type Mismatches
**Solution**: Verify data types in `ActivityModel.json`:
```json
"columns": [
  {"name": "Duration", "dataType": "Integer"},  ← Not String
  {"name": "Timestamp", "dataType": "DateTime"} ← ISO format
]
```

---

## Best Practices

1. **Refresh Schedule**: Hour, starting 08:00 daily
2. **Data Retention**: Keep 30-90 days of activity data
3. **Cache Strategy**: Aggregate daily data separately
4. **Row-Level Security**: Implement for multi-team access
5. **Data Quality**: Validate schema weekly
6. **Backup**: Export dataflow JSON weekly to version control
7. **Documentation**: Keep data dictionary updated
8. **Monitoring**: Set alerts on key KPIs

---

## Resources

- [Power BI Dataflows Documentation](https://learn.microsoft.com/power-bi/transform-model/dataflows/dataflows-introduction-self-service)
- [DAX Function Reference](https://learn.microsoft.com/dax/dax-function-reference)
- [Power Query Editor Guide](https://learn.microsoft.com/power-query/power-query-what-is-power-query)
- [Best Practices in Power BI](https://learn.microsoft.com/power-bi/guidance/power-bi-optimization)

---

**Last Updated**: 2026-09-03  
**Version**: 1.0.0
