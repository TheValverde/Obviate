# Kanban For Agents - Workflow Guide

## Overview

This guide covers all the workflows and user journeys for the Kanban For Agents system, from basic board management to complex multi-agent collaboration scenarios.

## Table of Contents

1. [Basic User Workflows](#basic-user-workflows)
2. [Agent Workflows](#agent-workflows)
3. [Multi-Agent Collaboration](#multi-agent-collaboration)
4. [Project Management Workflows](#project-management-workflows)
5. [Advanced Workflows](#advanced-workflows)
6. [Workflow Templates](#workflow-templates)
7. [Troubleshooting Workflows](#troubleshooting-workflows)

## Basic User Workflows

### 1. Getting Started Workflow

**Goal**: Set up a new Kanban board for a project

**Steps**:
1. **Create Workspace**
   ```bash
   curl -X POST "http://localhost:8000/v1/workspaces/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "My Project",
       "description": "Main workspace for my project"
     }'
   ```

2. **Create Board**
   ```bash
   curl -X POST "http://localhost:8000/v1/boards/" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Development Board",
       "description": "Main development tasks",
       "workspace_id": "WORKSPACE_ID"
     }'
   ```

3. **Verify Default Columns**
   ```bash
   curl -X GET "http://localhost:8000/v1/columns/board/BOARD_ID"
   ```

**Expected Result**: A board with "Todo", "In Progress", and "Done" columns

### 2. Task Management Workflow

**Goal**: Create and manage tasks through the Kanban workflow

**Steps**:
1. **Create a Task**
   ```bash
   curl -X POST "http://localhost:8000/v1/cards/" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Implement user authentication",
       "description": "Add OAuth2 authentication with Google and GitHub",
       "board_id": "BOARD_ID",
       "column_id": "TODO_COLUMN_ID",
       "priority": 3,
       "labels": ["backend", "security"],
       "assignees": ["developer@example.com"]
     }'
   ```

2. **Move Task to In Progress**
   ```bash
   curl -X POST "http://localhost:8000/v1/cards/CARD_ID/move" \
     -H "Content-Type: application/json" \
     -d '{
       "column_id": "IN_PROGRESS_COLUMN_ID"
     }'
   ```

3. **Update Task Progress**
   ```bash
   curl -X PUT "http://localhost:8000/v1/cards/CARD_ID" \
     -H "Content-Type: application/json" \
     -H "If-Match: 1" \
     -d '{
       "description": "OAuth2 implementation completed, testing in progress",
       "actual_hours": 4.5,
       "meta_data": {
         "progress": 75,
         "blockers": ["Need test environment setup"]
       }
     }'
   ```

4. **Move Task to Done**
   ```bash
   curl -X POST "http://localhost:8000/v1/cards/CARD_ID/move" \
     -H "Content-Type: application/json" \
     -d '{
       "column_id": "DONE_COLUMN_ID"
     }'
   ```

### 3. Board Organization Workflow

**Goal**: Organize and customize board structure

**Steps**:
1. **Add Custom Columns**
   ```bash
   curl -X POST "http://localhost:8000/v1/columns/" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Backlog",
       "description": "Future tasks and ideas",
       "board_id": "BOARD_ID",
       "position": 0,
       "color": "#8B5CF6"
     }'
   ```

2. **Reorder Columns**
   ```bash
   curl -X POST "http://localhost:8000/v1/columns/COLUMN_ID/reorder" \
     -H "Content-Type: application/json" \
     -d '{
       "new_position": 2
     }'
   ```

3. **Bulk Create Tasks**
   ```bash
   # Create multiple tasks in a loop
   for task in "${tasks[@]}"; do
     curl -X POST "http://localhost:8000/v1/cards/" \
       -H "Content-Type: application/json" \
       -d "$task"
   done
   ```

## Agent Workflows

### 1. Agent Task Assignment Workflow

**Goal**: Automatically assign tasks to AI agents based on capabilities

**Steps**:
1. **Get Available Tasks**
   ```bash
   curl -X GET "http://localhost:8000/v1/cards/?column_id=TODO_COLUMN_ID&limit=50"
   ```

2. **Filter Tasks by Agent Capabilities**
   ```python
   # Example: Filter tasks that match agent skills
   def filter_tasks_for_agent(tasks, agent_capabilities):
       return [
           task for task in tasks
           if any(skill in task.get('labels', []) for skill in agent_capabilities)
       ]
   ```

3. **Assign Task to Agent**
   ```bash
   curl -X PUT "http://localhost:8000/v1/cards/CARD_ID" \
     -H "Content-Type: application/json" \
     -H "If-Match: 1" \
     -d '{
       "assignees": ["agent-backend-001"],
       "meta_data": {
         "assigned_at": "2025-08-23T12:00:00Z",
         "agent_capabilities": ["backend", "security"],
         "estimated_completion": "2025-08-25T12:00:00Z"
       }
     }'
   ```

### 2. Agent Task Processing Workflow

**Goal**: Standardized workflow for agents to process assigned tasks

**Steps**:
1. **Get Agent's Assigned Tasks**
   ```bash
   curl -X GET "http://localhost:8000/v1/cards/?assignees=agent-backend-001&column_id=TODO_COLUMN_ID"
   ```

2. **Start Processing Task**
   ```bash
   curl -X POST "http://localhost:8000/v1/cards/CARD_ID/move" \
     -H "Content-Type: application/json" \
     -d '{
       "column_id": "IN_PROGRESS_COLUMN_ID"
     }'
   ```

3. **Update Task with Progress**
   ```bash
   curl -X PUT "http://localhost:8000/v1/cards/CARD_ID" \
     -H "Content-Type: application/json" \
     -H "If-Match: 1" \
     -d '{
       "description": "Agent processing: Analyzing requirements and implementing solution",
       "meta_data": {
         "agent_status": "processing",
         "started_at": "2025-08-23T12:00:00Z",
         "current_step": "implementation",
         "progress_percentage": 60
       }
     }'
   ```

4. **Complete Task**
   ```bash
   curl -X POST "http://localhost:8000/v1/cards/CARD_ID/move" \
     -H "Content-Type: application/json" \
     -d '{
       "column_id": "DONE_COLUMN_ID"
     }'
   ```

5. **Add Completion Summary**
   ```bash
   curl -X PUT "http://localhost:8000/v1/cards/CARD_ID" \
     -H "Content-Type: application/json" \
     -H "If-Match: 1" \
     -d '{
       "description": "Task completed by agent-backend-001. OAuth2 implementation successful with Google and GitHub providers.",
       "actual_hours": 6.5,
       "meta_data": {
         "agent_status": "completed",
         "completed_at": "2025-08-23T18:30:00Z",
         "completion_summary": "Successfully implemented OAuth2 authentication",
         "quality_score": 95,
         "tests_passed": true
       }
     }'
   ```

### 3. Agent Error Handling Workflow

**Goal**: Handle task failures and blockers gracefully

**Steps**:
1. **Detect Blocking Issue**
   ```bash
   curl -X PUT "http://localhost:8000/v1/cards/CARD_ID" \
     -H "Content-Type: application/json" \
     -H "If-Match: 1" \
     -d '{
       "meta_data": {
         "agent_status": "blocked",
         "blocker_type": "dependency_missing",
         "blocker_description": "Required API key not available",
         "blocked_at": "2025-08-23T14:00:00Z",
         "estimated_resolution_time": "2 hours"
       }
     }'
   ```

2. **Move to Blocked Column (if exists)**
   ```bash
   curl -X POST "http://localhost:8000/v1/cards/CARD_ID/move" \
     -H "Content-Type: application/json" \
     -d '{
       "column_id": "BLOCKED_COLUMN_ID"
     }'
   ```

3. **Resolve Blocker**
   ```bash
   curl -X PUT "http://localhost:8000/v1/cards/CARD_ID" \
     -H "Content-Type: application/json" \
     -H "If-Match: 1" \
     -d '{
       "meta_data": {
         "agent_status": "resolved",
         "blocker_resolved_at": "2025-08-23T16:00:00Z",
         "resolution_notes": "API key provided by admin"
       }
     }'
   ```

4. **Resume Processing**
   ```bash
   curl -X POST "http://localhost:8000/v1/cards/CARD_ID/move" \
     -H "Content-Type: application/json" \
     -d '{
       "column_id": "IN_PROGRESS_COLUMN_ID"
     }'
   ```

## Multi-Agent Collaboration

### 1. Task Distribution Workflow

**Goal**: Distribute tasks among multiple agents efficiently

**Steps**:
1. **Get All Available Tasks**
   ```bash
   curl -X GET "http://localhost:8000/v1/cards/?column_id=TODO_COLUMN_ID&limit=100"
   ```

2. **Analyze Agent Workloads**
   ```python
   def get_agent_workloads():
       agents = ["agent-backend-001", "agent-frontend-001", "agent-qa-001"]
       workloads = {}
       
       for agent in agents:
           # Get tasks in progress
           in_progress = get_cards_by_assignee_and_column(agent, "IN_PROGRESS_COLUMN_ID")
           workloads[agent] = len(in_progress)
       
       return workloads
   ```

3. **Assign Tasks Based on Workload and Skills**
   ```python
   def assign_tasks_optimally(tasks, agents, workloads):
       for task in tasks:
           # Find agent with lowest workload and matching skills
           best_agent = find_best_agent(task, agents, workloads)
           
           # Assign task
           assign_task_to_agent(task["id"], best_agent)
           workloads[best_agent] += 1
   ```

### 2. Agent Communication Workflow

**Goal**: Enable agents to communicate about shared tasks

**Steps**:
1. **Create Communication Card**
   ```bash
   curl -X POST "http://localhost:8000/v1/cards/" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "API Integration Discussion",
       "description": "Need to coordinate API integration between backend and frontend agents",
       "board_id": "BOARD_ID",
       "column_id": "DISCUSSION_COLUMN_ID",
       "assignees": ["agent-backend-001", "agent-frontend-001"],
       "labels": ["discussion", "coordination"],
       "meta_data": {
         "communication_type": "inter_agent",
         "priority": "high",
         "participants": ["agent-backend-001", "agent-frontend-001"]
       }
     }'
   ```

2. **Update with Discussion Results**
   ```bash
   curl -X PUT "http://localhost:8000/v1/cards/CARD_ID" \
     -H "Content-Type: application/json" \
     -H "If-Match: 1" \
     -d '{
       "description": "Agreement reached: Backend will provide REST API endpoints, Frontend will handle UI integration",
       "meta_data": {
         "discussion_completed": true,
         "decisions": [
           "Use REST API for communication",
           "Backend provides /api/v1/ endpoints",
           "Frontend handles authentication UI"
         ],
         "next_actions": [
           "Backend: Implement API endpoints",
           "Frontend: Create authentication forms"
         ]
       }
     }'
   ```

### 3. Handoff Workflow

**Goal**: Smooth handoff between agents for multi-stage tasks

**Steps**:
1. **Mark Task Ready for Handoff**
   ```bash
   curl -X PUT "http://localhost:8000/v1/cards/CARD_ID" \
     -H "Content-Type: application/json" \
     -H "If-Match: 1" \
     -d '{
       "meta_data": {
         "ready_for_handoff": true,
         "handoff_from": "agent-backend-001",
         "handoff_to": "agent-frontend-001",
         "handoff_reason": "Backend API completed, ready for frontend integration",
         "completion_criteria": "API endpoints tested and documented"
       }
     }'
   ```

2. **Create Handoff Card**
   ```bash
   curl -X POST "http://localhost:8000/v1/cards/" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Frontend Integration - User Authentication",
       "description": "Integrate backend OAuth2 API with frontend authentication UI",
       "board_id": "BOARD_ID",
       "column_id": "TODO_COLUMN_ID",
       "assignees": ["agent-frontend-001"],
       "labels": ["frontend", "integration"],
       "meta_data": {
         "handoff_from_task": "CARD_ID",
         "dependencies": ["Backend OAuth2 API"],
         "estimated_hours": 4.0
       }
     }'
   ```

## Project Management Workflows

### 1. Sprint Planning Workflow

**Goal**: Plan and organize work for a development sprint

**Steps**:
1. **Create Sprint Board**
   ```bash
   curl -X POST "http://localhost:8000/v1/boards/" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Sprint 3 - User Authentication",
       "description": "Sprint focused on implementing user authentication features",
       "workspace_id": "WORKSPACE_ID"
     }'
   ```

2. **Add Sprint-Specific Columns**
   ```bash
   # Add Sprint columns
   curl -X POST "http://localhost:8000/v1/columns/" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Sprint Backlog",
       "description": "Tasks planned for this sprint",
       "board_id": "SPRINT_BOARD_ID",
       "position": 1,
       "color": "#8B5CF6"
     }'
   ```

3. **Create Sprint Tasks**
   ```bash
   # Create multiple sprint tasks
   sprint_tasks = [
     {
       "title": "Implement OAuth2 Backend",
       "description": "Add OAuth2 authentication endpoints",
       "board_id": "SPRINT_BOARD_ID",
       "column_id": "SPRINT_BACKLOG_COLUMN_ID",
       "priority": 1,
       "labels": ["backend", "security", "sprint-3"],
       "estimated_hours": 8.0,
       "meta_data": {"story_points": 5, "sprint": "sprint-3"}
     },
     {
       "title": "Create Login UI",
       "description": "Design and implement login interface",
       "board_id": "SPRINT_BOARD_ID",
       "column_id": "SPRINT_BACKLOG_COLUMN_ID",
       "priority": 2,
       "labels": ["frontend", "ui", "sprint-3"],
       "estimated_hours": 6.0,
       "meta_data": {"story_points": 3, "sprint": "sprint-3"}
     }
   ]
   
   for task in sprint_tasks:
     curl -X POST "http://localhost:8000/v1/cards/" \
       -H "Content-Type: application/json" \
       -d json.dumps(task)
   ```

### 2. Release Management Workflow

**Goal**: Manage software releases through Kanban

**Steps**:
1. **Create Release Board**
   ```bash
   curl -X POST "http://localhost:8000/v1/boards/" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Release v1.2.0",
       "description": "Release management for version 1.2.0",
       "workspace_id": "WORKSPACE_ID"
     }'
   ```

2. **Add Release-Specific Columns**
   ```bash
   release_columns = [
     {"title": "Ready for Release", "position": 1, "color": "#10B981"},
     {"title": "In Testing", "position": 2, "color": "#F59E0B"},
     {"title": "QA Approved", "position": 3, "color": "#3B82F6"},
     {"title": "Released", "position": 4, "color": "#059669"}
   ]
   
   for column in release_columns:
     curl -X POST "http://localhost:8000/v1/columns/" \
       -H "Content-Type: application/json" \
       -d json.dumps({
         **column,
         "board_id": "RELEASE_BOARD_ID",
         "description": f"Features {column['title'].lower()}"
       })
   ```

3. **Track Release Progress**
   ```bash
   # Move completed features to release
   curl -X POST "http://localhost:8000/v1/cards/FEATURE_CARD_ID/move" \
     -H "Content-Type: application/json" \
     -d '{
       "column_id": "READY_FOR_RELEASE_COLUMN_ID"
     }'
   ```

## Advanced Workflows

### 1. Automated Testing Workflow

**Goal**: Integrate automated testing into the Kanban process

**Steps**:
1. **Create Test Column**
   ```bash
   curl -X POST "http://localhost:8000/v1/columns/" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Testing",
       "description": "Automated and manual testing",
       "board_id": "BOARD_ID",
       "position": 3,
       "color": "#F59E0B"
     }'
   ```

2. **Automated Test Trigger**
   ```python
   def trigger_automated_tests(card_id):
       # When card moves to Testing column
       test_results = run_automated_tests(card_id)
       
       if test_results["passed"]:
           # Move to Done
           move_card_to_column(card_id, "DONE_COLUMN_ID")
       else:
           # Move back to In Progress with test failures
           move_card_to_column(card_id, "IN_PROGRESS_COLUMN_ID")
           update_card_with_test_failures(card_id, test_results["failures"])
   ```

### 2. Code Review Workflow

**Goal**: Integrate code review process into Kanban

**Steps**:
1. **Add Review Column**
   ```bash
   curl -X POST "http://localhost:8000/v1/columns/" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Code Review",
       "description": "Code review and approval",
       "board_id": "BOARD_ID",
       "position": 4,
       "color": "#8B5CF6"
     }'
   ```

2. **Review Process**
   ```python
   def code_review_workflow(card_id, reviewer_id):
       # Assign reviewer
       update_card_assignees(card_id, [reviewer_id])
       
       # Add review metadata
       update_card_metadata(card_id, {
         "review_status": "pending",
         "reviewer": reviewer_id,
         "review_requested_at": datetime.now().isoformat()
       })
   ```

### 3. Performance Monitoring Workflow

**Goal**: Monitor and optimize agent performance

**Steps**:
1. **Track Performance Metrics**
   ```python
   def track_agent_performance(agent_id, time_period="week"):
       # Get agent's completed tasks
       completed_tasks = get_cards_by_assignee_and_column(
         agent_id, "DONE_COLUMN_ID", time_period
       )
       
       # Calculate metrics
       metrics = {
         "tasks_completed": len(completed_tasks),
         "average_completion_time": calculate_avg_completion_time(completed_tasks),
         "quality_score": calculate_quality_score(completed_tasks),
         "blocker_frequency": calculate_blocker_frequency(agent_id, time_period)
       }
       
       return metrics
   ```

2. **Performance Optimization**
   ```python
   def optimize_agent_workload(agent_id):
       metrics = track_agent_performance(agent_id)
       
       if metrics["blocker_frequency"] > 0.3:  # 30% of tasks blocked
           # Reduce workload
           reassign_tasks_from_agent(agent_id, 0.5)  # Reduce by 50%
       
       if metrics["quality_score"] < 0.8:  # Quality below 80%
           # Add review step
           add_quality_review_step(agent_id)
   ```

## Workflow Templates

### 1. Standard Development Workflow

```json
{
  "name": "Standard Development",
  "description": "Standard workflow for development tasks",
  "columns": [
    {"title": "Backlog", "position": 0, "color": "#8B5CF6"},
    {"title": "Todo", "position": 1, "color": "#6B7280"},
    {"title": "In Progress", "position": 2, "color": "#3B82F6"},
    {"title": "Code Review", "position": 3, "color": "#F59E0B"},
    {"title": "Testing", "position": 4, "color": "#EF4444"},
    {"title": "Done", "position": 5, "color": "#10B981"}
  ],
  "default_labels": ["bug", "feature", "enhancement", "documentation"],
  "priority_levels": [1, 2, 3, 4, 5]
}
```

### 2. Agent-Only Workflow

```json
{
  "name": "Agent-Only Development",
  "description": "Workflow optimized for AI agent collaboration",
  "columns": [
    {"title": "Agent Queue", "position": 0, "color": "#8B5CF6"},
    {"title": "Processing", "position": 1, "color": "#3B82F6"},
    {"title": "Review", "position": 2, "color": "#F59E0B"},
    {"title": "Completed", "position": 3, "color": "#10B981"}
  ],
  "agent_specific": {
    "auto_assignment": true,
    "skill_matching": true,
    "workload_balancing": true,
    "quality_gates": true
  }
}
```

### 3. Multi-Team Workflow

```json
{
  "name": "Multi-Team Collaboration",
  "description": "Workflow for multiple teams working together",
  "columns": [
    {"title": "Product Backlog", "position": 0, "color": "#8B5CF6"},
    {"title": "Sprint Planning", "position": 1, "color": "#6B7280"},
    {"title": "Development", "position": 2, "color": "#3B82F6"},
    {"title": "QA Testing", "position": 3, "color": "#F59E0B"},
    {"title": "UAT", "position": 4, "color": "#EF4444"},
    {"title": "Production Ready", "position": 5, "color": "#10B981"}
  ],
  "team_assignments": {
    "product_backlog": ["product-team"],
    "development": ["backend-team", "frontend-team"],
    "qa_testing": ["qa-team"],
    "uat": ["business-team"]
  }
}
```

## Troubleshooting Workflows

### 1. Task Stuck Workflow

**Problem**: Task is stuck in a column for too long

**Solution**:
1. **Identify Stuck Tasks**
   ```python
   def find_stuck_tasks(board_id, threshold_hours=24):
       all_cards = get_all_cards(board_id)
       stuck_tasks = []
       
       for card in all_cards:
           if card["column_id"] not in ["DONE_COLUMN_ID", "ARCHIVED_COLUMN_ID"]:
               time_in_column = calculate_time_in_column(card)
               if time_in_column > threshold_hours:
                   stuck_tasks.append(card)
       
       return stuck_tasks
   ```

2. **Analyze Blockers**
   ```python
   def analyze_blockers(card_id):
       card = get_card(card_id)
       blockers = card.get("meta_data", {}).get("blockers", [])
       
       if blockers:
           return {
             "card_id": card_id,
             "blockers": blockers,
             "recommended_action": "resolve_blockers"
           }
       else:
           return {
             "card_id": card_id,
             "recommended_action": "reassign_or_escalate"
           }
   ```

### 2. Agent Performance Issues

**Problem**: Agent is not completing tasks efficiently

**Solution**:
1. **Analyze Performance**
   ```python
   def analyze_agent_performance(agent_id):
       metrics = track_agent_performance(agent_id)
       
       issues = []
       if metrics["average_completion_time"] > 8:  # More than 8 hours
           issues.append("slow_completion")
       
       if metrics["quality_score"] < 0.7:  # Quality below 70%
           issues.append("low_quality")
       
       if metrics["blocker_frequency"] > 0.5:  # More than 50% blocked
           issues.append("frequent_blockers")
       
       return issues
   ```

2. **Implement Solutions**
   ```python
   def resolve_agent_issues(agent_id, issues):
       for issue in issues:
           if issue == "slow_completion":
               # Reduce workload or provide more resources
               reduce_agent_workload(agent_id, 0.3)
           
           elif issue == "low_quality":
               # Add quality review step
               add_quality_gate(agent_id)
           
           elif issue == "frequent_blockers":
               # Provide better documentation or training
               assign_training_tasks(agent_id)
   ```

### 3. Workflow Bottlenecks

**Problem**: Work is piling up in certain columns

**Solution**:
1. **Identify Bottlenecks**
   ```python
   def identify_bottlenecks(board_id):
       columns = get_board_columns(board_id)
       bottlenecks = []
       
       for column in columns:
           card_count = len(get_column_cards(column["id"]))
           if card_count > 10:  # More than 10 cards in column
               bottlenecks.append({
                 "column_id": column["id"],
                 "column_name": column["title"],
                 "card_count": card_count,
                 "severity": "high" if card_count > 20 else "medium"
               })
       
       return bottlenecks
   ```

2. **Resolve Bottlenecks**
   ```python
   def resolve_bottlenecks(bottlenecks):
       for bottleneck in bottlenecks:
           if bottleneck["severity"] == "high":
               # Immediate action needed
               reassign_cards_from_column(bottleneck["column_id"])
           else:
               # Add more resources
               add_agents_to_column(bottleneck["column_id"])
   ```

This comprehensive workflow guide provides all the patterns and examples needed to implement effective Kanban workflows for both human users and AI agents, enabling efficient project management and collaboration.
