#!/usr/bin/env python3
"""
Activity Dataflow Integration Script
Converts session, git, and tool activity data into Power BI dataflow format
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import subprocess


class ActivityDataflowGenerator:
    """Generate Power BI dataflow data from various sources"""
    
    def __init__(self, repo_path: str, output_dir: str = "powerbi/data-sources"):
        self.repo_path = repo_path
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def generate_session_activity(self, sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert session objects to dataflow format"""
        activity = []
        for session in sessions:
            activity.append({
                "SessionId": session.get("id", ""),
                "SessionName": session.get("name", ""),
                "Timestamp": session.get("created_at", datetime.now().isoformat()),
                "ActivityType": self._infer_activity_type(session.get("summary", "")),
                "Duration": session.get("duration_seconds", 0),
                "UserName": session.get("user", ""),
                "Repository": session.get("repository", ""),
                "Branch": session.get("branch", "main"),
                "Status": session.get("status", "pending")
            })
        return activity
    
    def _infer_activity_type(self, summary: str) -> str:
        """Infer activity type from session summary"""
        summary_lower = summary.lower()
        if "test" in summary_lower:
            return "testing"
        elif "review" in summary_lower or "review" in summary_lower:
            return "review"
        elif "debug" in summary_lower:
            return "debugging"
        elif "doc" in summary_lower:
            return "documentation"
        else:
            return "editing"
    
    def generate_git_activity(self) -> List[Dict[str, Any]]:
        """Extract git activity from repository"""
        activity = []
        try:
            # Get recent commits
            result = subprocess.run(
                ["git", "log", "--oneline", "--all", "-n", "50"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                
                parts = line.split(" ", 1)
                commit_hash = parts[0]
                message = parts[1] if len(parts) > 1 else ""
                
                # Get detailed commit info
                detail_result = subprocess.run(
                    ["git", "show", "--format=%ai|%an|%s", "--shortstat", commit_hash],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
                lines = detail_result.stdout.strip().split("\n")
                if len(lines) >= 2:
                    header = lines[0].split("|")
                    if len(header) >= 3:
                        commit_date = header[0]
                        author = header[1]
                        subject = header[2]
                        
                        # Parse stats
                        insertions = 0
                        deletions = 0
                        files_changed = 0
                        for stat_line in lines:
                            if "insertion" in stat_line:
                                parts = stat_line.split()
                                if parts:
                                    files_changed = int(parts[0])
                                    insertions = int(parts[-4]) if "insertion" in stat_line else 0
                                    deletions = int(parts[-1]) if "deletion" in stat_line else 0
                        
                        activity.append({
                            "CommitId": commit_hash,
                            "CommitMessage": subject,
                            "AuthorName": author,
                            "CommitDate": commit_date,
                            "FilesChanged": files_changed,
                            "Insertions": insertions,
                            "Deletions": deletions,
                            "Branch": self._get_commit_branch(commit_hash)
                        })
        except Exception as e:
            print(f"Warning: Could not extract git activity: {e}")
        
        return activity
    
    def _get_commit_branch(self, commit_hash: str) -> str:
        """Get branch name for a commit"""
        try:
            result = subprocess.run(
                ["git", "branch", "-r", "--contains", commit_hash],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            branches = result.stdout.strip().split("\n")
            return branches[0].strip() if branches and branches[0] else "unknown"
        except:
            return "unknown"
    
    def generate_file_edits(self, edits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert file edit records to dataflow format"""
        activity = []
        for edit in edits:
            activity.append({
                "EditId": edit.get("id", ""),
                "SessionId": edit.get("session_id", ""),
                "FilePath": edit.get("path", ""),
                "FileType": Path(edit.get("path", "")).suffix.lstrip(".") or "unknown",
                "ChangeType": edit.get("type", "modify"),
                "LinesAdded": edit.get("additions", 0),
                "LinesRemoved": edit.get("deletions", 0),
                "Timestamp": edit.get("timestamp", datetime.now().isoformat())
            })
        return activity
    
    def generate_tool_executions(self, executions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert tool execution records to dataflow format"""
        activity = []
        for execution in executions:
            activity.append({
                "ExecutionId": execution.get("id", ""),
                "SessionId": execution.get("session_id", ""),
                "ToolName": execution.get("tool", ""),
                "ExecutionTime": execution.get("duration_ms", 0),
                "Success": execution.get("success", False),
                "ExecutedAt": execution.get("timestamp", datetime.now().isoformat()),
                "ToolType": self._categorize_tool(execution.get("tool", ""))
            })
        return activity
    
    def _categorize_tool(self, tool_name: str) -> str:
        """Categorize tool by type"""
        tool_lower = tool_name.lower()
        if tool_lower in ["view", "edit", "create", "grep", "glob"]:
            return "file-operation"
        elif tool_lower in ["grep", "search", "find"]:
            return "search"
        elif tool_lower in ["git", "gh"]:
            return "vcs"
        elif tool_lower in ["powershell", "bash", "sh", "cmd"]:
            return "command"
        else:
            return "other"
    
    def generate_task_activity(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert task records to dataflow format"""
        activity = []
        for task in tasks:
            created = datetime.fromisoformat(task.get("created_at", datetime.now().isoformat()))
            completed = task.get("completed_at")
            time_to_complete = None
            
            if completed:
                completed_dt = datetime.fromisoformat(completed)
                time_to_complete = int((completed_dt - created).total_seconds())
            
            activity.append({
                "TaskId": task.get("id", ""),
                "TaskTitle": task.get("title", ""),
                "Status": task.get("status", "pending"),
                "CreatedDate": task.get("created_at", datetime.now().isoformat()),
                "CompletedDate": completed,
                "TimeToComplete": time_to_complete,
                "Priority": task.get("priority", "medium"),
                "Category": task.get("category", "general")
            })
        return activity
    
    def save_json(self, data: List[Dict[str, Any]], filename: str) -> None:
        """Save data to JSON file"""
        filepath = Path(self.output_dir) / filename
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"Saved: {filepath}")
    
    def load_sample_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load sample data from JSON files"""
        data = {}
        source_dir = Path(self.output_dir)
        
        for json_file in source_dir.glob("*.json"):
            key = json_file.stem
            with open(json_file) as f:
                data[key] = json.load(f)
        
        return data
    
    def validate_dataflow(self) -> bool:
        """Validate dataflow files and relationships"""
        try:
            session_data = None
            file_edit_data = None
            tool_exec_data = None
            
            source_dir = Path(self.output_dir)
            
            # Load session data
            session_file = source_dir / "session-activity.json"
            if session_file.exists():
                with open(session_file) as f:
                    session_data = json.load(f)
                print(f"✓ Session Activity: {len(session_data)} records")
            
            # Load file edit data
            edit_file = source_dir / "file-edits.json"
            if edit_file.exists():
                with open(edit_file) as f:
                    file_edit_data = json.load(f)
                print(f"✓ File Edits: {len(file_edit_data)} records")
            
            # Validate relationships
            if session_data and file_edit_data:
                session_ids = {s["SessionId"] for s in session_data}
                edit_session_ids = {e["SessionId"] for e in file_edit_data}
                orphaned = edit_session_ids - session_ids
                if orphaned:
                    print(f"⚠ Warning: Orphaned session IDs in FileEdits: {orphaned}")
            
            # Load tool executions
            tool_file = source_dir / "tool-executions.json"
            if tool_file.exists():
                with open(tool_file) as f:
                    tool_exec_data = json.load(f)
                print(f"✓ Tool Executions: {len(tool_exec_data)} records")
            
            # Load git activity
            git_file = source_dir / "git-activity.json"
            if git_file.exists():
                with open(git_file) as f:
                    git_data = json.load(f)
                print(f"✓ Git Activity: {len(git_data)} records")
            
            # Load task activity
            task_file = source_dir / "task-activity.json"
            if task_file.exists():
                with open(task_file) as f:
                    task_data = json.load(f)
                print(f"✓ Task Activity: {len(task_data)} records")
            
            print("\n✓ Dataflow validation passed!")
            return True
        
        except Exception as e:
            print(f"✗ Dataflow validation failed: {e}")
            return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Power BI dataflow data")
    parser.add_argument("--repo", default=".", help="Repository path")
    parser.add_argument("--output", default="powerbi/data-sources", help="Output directory")
    parser.add_argument("--validate", action="store_true", help="Validate existing dataflow")
    
    args = parser.parse_args()
    
    generator = ActivityDataflowGenerator(args.repo, args.output)
    
    if args.validate:
        generator.validate_dataflow()
    else:
        print(f"Activity Dataflow Generator")
        print(f"Repository: {args.repo}")
        print(f"Output: {args.output}")
        print(f"\nTo integrate with live data:")
        print(f"1. Modify generate_* methods to connect to real data sources")
        print(f"2. Run: python activity_dataflow.py --repo <repo_path>")
        print(f"3. Validate with: python activity_dataflow.py --validate")
