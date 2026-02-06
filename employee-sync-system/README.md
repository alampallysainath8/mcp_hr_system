# Employee Sync System - MCP Agent Orchestration

This project demonstrates an automated employee change detection and sync system using **MCP (Model Context Protocol)**, **LangChain agents**, and **AI orchestration**. It detects changes in the HR system and automatically syncs them to the Payroll system using intelligent agents.

---

## 🔍 Purpose

This system automates employee data synchronization between HR and Payroll systems using AI agents:

1. **Detect employee changes** automatically using SQLite triggers
2. **HR Agent** detects changes and creates sync payloads using MCP tools
3. **Orchestrator** coordinates the workflow between HR and Payroll agents
4. **Payroll Agent** receives and applies changes to the payroll database
5. **Real-time processing** with streaming responses and progress tracking

---

## 🏗️ Architecture

**Three-Layer Agent System:**
- **Supervisor/Orchestrator** - Coordinates workflow between agents
- **HR Agent** - Detects changes and creates sync payloads via MCP
- **Payroll Agent** - Processes sync payloads and updates payroll database

**MCP Servers:**
- HR MCP Server (port 8000) - Provides tools for change detection
- Payroll MCP Server (port 7002) - Provides tools for payload processing

---

## 📁 Folder Structure

```plaintext
employee-sync-system/
│
├── data/                          # All databases and payloads
│   ├── hr_system.db              # HR database with employees and change_log
│   ├── payroll_system.db         # Payroll database with sync_log
│   ├── sync_payload.json         # Generated payload for transfer
│   └── received_payload.json     # Payload received by payroll system
│
├── scripts/                       # Setup and test scripts
│   ├── init_hr_db.py             # Initialize HR database with sample data
│   ├── init_payroll_db.py        # Initialize Payroll database
│   └── add_update_employee.py    # Add or update employees to trigger sync
│
├── shared/                        # Shared utilities (currently unused)
│   ├── models.py                 # Data models
│   └── utils.py                  # Database utilities
│
├── hr_mcp_server.py              # MCP server for HR system (2 tools)
├── payroll_mcp_server.py         # MCP server for Payroll system (3 tools)
├── hr_agent.py                   # HR agent with MCP client
├── payroll_agent.py              # Payroll agent for processing sync
├── orchestrator_new.py           # Main orchestrator coordinating both agents
├── orchestrator_agent_new.py     # Alternative orchestrator implementation
├── .env                          # Environment variables
└── .env.example                  # Environment configuration template
```

---

## 🚀 Quick Start

### 1. Configure Environment

Choose your LLM provider by configuring `.env`:

**For Ollama (default):**
```bash
USE_GROQ=false
```

**For Groq:**
```bash
USE_GROQ=true
GROQ_API_KEY=your_groq_api_key_here
```

### 2. Initialize Databases

```bash
python scripts/init_hr_db.py
python scripts/init_payroll_db.py
```

### 3. Start MCP Servers

Start the HR MCP server:
```bash
python hr_mcp_server.py      # Port 8000
```

In a separate terminal, start the Payroll MCP server:
```bash
python payroll_mcp_server.py # Port 7002
```

### 4. Run the Orchestrator

```bash
python orchestrator_new.py
```

**Available commands:**
- `sync employees` - Full sync: detect HR changes and sync to payroll
- `check changes` - Check for new HR changes only
- `process payroll` - Process existing sync payload
- `quit` - Exit

---

## 🔧 MCP Tools

### HR System (hr_mcp_server.py)
- **`detect_changes`** - Find unprocessed employee changes in HR database
- **`create_sync_payload`** - Create JSON payload with changes for payroll system

### Payroll System (payroll_mcp_server.py)
- **`receive_payload`** - Accept and store incoming sync payload
- **`validate_sync_data`** - Validate received data for payroll system
- **`apply_changes`** - Apply changes to payroll database

---

## 🤖 LLM Configuration

The system supports two LLM providers:

### Ollama (Local)
- Model: `gpt-oss:20b`
- Endpoint: `http://localhost:11434`
- No API key required
- Set `USE_GROQ=false` in `.env`

### Groq (Cloud)
- Model: `llama-3.3-70b-versatile`
- Requires API key from https://console.groq.com/keys
- Set `USE_GROQ=true` and `GROQ_API_KEY` in `.env`

---

## 🧪 Testing the System

### Add a New Employee
```bash
python scripts/add_update_employee.py
```

Follow the prompts to add or update employee records. Changes are automatically logged in the HR database.

### Monitor the Workflow

The orchestrator displays clean message flow:
- `[HumanMessage]` - User input
- `[AIMessage]` - Agent responses
- `[ToolMessage]` - Tool execution results

---

## 🔄 Complete Workflow

1. **User Request**: User types "sync employees"
2. **Supervisor**: Analyzes request and transfers to HR Agent
3. **HR Agent**: 
   - Connects to HR MCP server
   - Calls `detect_changes` tool
   - Calls `create_sync_payload` tool
   - Returns payload info to Supervisor
4. **Supervisor**: Transfers to Payroll Agent
5. **Payroll Agent**:
   - Reads sync payload file
   - Calls `process_sync_payload` function
   - Connects to Payroll MCP server (future: use MCP tools)
   - Updates payroll database
   - Returns success confirmation
6. **Supervisor**: Reports final status to user

---

## 📊 Database Schema

### HR System
- **employees** - Employee master data
- **change_log** - Tracks all employee changes with triggers
- **sync_log** - Tracks sync operations

### Payroll System  
- **employees** - Payroll employee records
- **sync_log** - Tracks received sync operations

---

## 🔍 Key Features

✅ **Automatic Change Detection** - Database triggers log all changes  
✅ **AI Agent Orchestration** - Supervisor coordinates multi-agent workflow  
✅ **MCP Integration** - Uses Model Context Protocol for tool access  
✅ **Dual LLM Support** - Choose between Ollama (local) or Groq (cloud)  
✅ **Clean Output** - Filters metadata, shows only essential messages  
✅ **Streaming Support** - Real-time progress updates (can be disabled)  
✅ **Error Handling** - Comprehensive error messages and logging  

---

## 📝 Notes

- The `shared/` folder contains utility classes but is currently not used by the main system
- HR MCP server must be running before starting the orchestrator
- Payroll MCP server is used for receiving and processing payloads
- The orchestrator automatically starts the HR MCP server if not running
- Recursion limit is set to 50 to allow complete workflow execution

---

## 🧩 Real-world Use Case

**Scenario:** HR updates employee salary → Automatically syncs to Payroll

1. HR manager updates John Doe's salary from $95,000 to $98,000 using `add_update_employee.py`
2. Database trigger logs the UPDATE change
3. User runs orchestrator and types "sync employees"
4. HR agent detects the change and generates sync payload
5. Orchestrator hands off to Payroll agent
6. Payroll agent validates and applies the change
7. John's payroll record is updated with new salary
8. Next paycheck reflects the new amount

---

## 🛠️ Future Enhancements

- [ ] Use MCP tools in Payroll agent instead of direct file access
- [ ] Add authentication between systems
- [ ] Implement rollback mechanism for failed syncs
- [ ] Add scheduling for automated periodic syncs
- [ ] Support batch processing for multiple changes
- [ ] Add audit logging and compliance reporting
