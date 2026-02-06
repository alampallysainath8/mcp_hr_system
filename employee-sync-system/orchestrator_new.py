#!/usr/bin/env python3

import os
import subprocess
import time
from pathlib import Path

from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# LLM Configuration - Choose between Groq or Ollama
USE_GROQ = os.getenv("USE_GROQ", "false").lower() == "true"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")  # Paste your Groq API key in .env file

print(f"\n{'='*60}")
if USE_GROQ:
    print("🚀 Starting with ChatGroq LLM")
    if not GROQ_API_KEY:
        raise ValueError("❌ GROQ_API_KEY is required when USE_GROQ=true. Please set it in your .env file.")
else:
    print("🚀 Starting with Ollama LLM")
print(f"{'='*60}\n")

# Get LLM instance based on configuration
def get_llm():
    if USE_GROQ:
        return ChatGroq(
            api_key=GROQ_API_KEY,
            model="openai/gpt-oss-20b",
            temperature=0.1
        )
    else:
        return ChatOllama(
            base_url="http://localhost:11434",
            model="gpt-oss:20b",
            streaming=False
        )

# Paths
ROOT_DIR = Path(__file__).parent.resolve()

def start_hr_mcp_server():
    """Start HR MCP Server in background"""
    try:
        print("🔧 Starting HR MCP Server...")
        server_process = subprocess.Popen([
            "python3", "hr_mcp_server.py"
        ], cwd=ROOT_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)  # Give server time to start
        print("✅ HR MCP Server started")
        return server_process
    except Exception as e:
        print(f"❌ Failed to start HR MCP Server: {e}")
        return None

def detect_hr_changes():
    """Detect changes in HR system and create sync payload"""
    try:
        # Start HR MCP server if needed
        start_hr_mcp_server()
        
        # Import and run HR agent auto function
        from hr_agent import run_agent_auto
        import asyncio
        result = asyncio.run(run_agent_auto())
        return f"HR change detection completed: {result}"
    except Exception as e:
        return f"❌ HR detection error: {str(e)}"

def process_payroll_sync():
    """Process sync payload and update payroll system"""
    try:
        # Import and run Payroll agent  
        from payroll_agent import run_payroll_agent
        run_payroll_agent()
        return "Payroll sync completed successfully"
    except Exception as e:
        return f"❌ Payroll sync error: {str(e)}"

# Create HR Agent with tools
hr_agent = create_react_agent(
    model=get_llm(),
    tools=[detect_hr_changes],
    prompt="You are an HR system agent that detects employee changes and creates sync payloads",
    name="hr_agent"
)

# Create Payroll Agent with tools
payroll_agent = create_react_agent(
    model=get_llm(),
    tools=[process_payroll_sync],
    prompt="You are a payroll system agent that processes sync payloads and updates payroll database",
    name="payroll_agent"
)

# Create Supervisor
supervisor = create_supervisor(
    agents=[hr_agent, payroll_agent],
    model=get_llm(),
    prompt=(
        "You are the Employee Sync System Orchestrator. You coordinate HR and payroll agents.\n"
        "IMPORTANT: You MUST complete the full workflow by calling the appropriate transfer tools.\n\n"
        "For 'sync employees' or 'full sync' requests:\n"
        "1. Transfer to HR agent to detect changes\n"
        "2. After HR agent returns, immediately transfer to payroll agent to process\n"
        "3. Do NOT just describe what should happen - actually call transfer_to_payroll_agent\n\n"
        "For 'check changes' - transfer to HR agent only\n"
        "For 'process payroll' - transfer to payroll agent only\n\n"
        "Always use transfer tools to delegate work, never just describe the plan."
    )
).compile()

def run_orchestrator():
    """Run the orchestrator agent with user interaction"""
    
    print("="*60)
    print("🏢 EMPLOYEE SYNC SYSTEM ORCHESTRATOR")
    print("="*60)
    print("Available commands:")
    print("• 'sync employees' - Detect HR changes and sync to payroll")
    print("• 'check changes' - Check for new HR changes only") 
    print("• 'process payroll' - Process existing sync payload")
    print("• 'quit' - Exit")
    print("="*60)
    
    while True:
        try:
            user_input = input("\n🤖 What would you like me to do? ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            print(f"\n🎯 Processing request: '{user_input}'")
            print("="*50)
            
            # Stream the response to show real-time progress
            for chunk in supervisor.stream(
                {"messages": [{"role": "user", "content": user_input}]},
                {"recursion_limit": 50}  # Allow enough iterations for the full workflow
            ):
                # Extract and display only message type and content
                for agent_name, data in chunk.items():
                    messages = data.get("messages", [])
                    for msg in messages:
                        msg_type = type(msg).__name__
                        
                        # Get sender name if available
                        sender = getattr(msg, 'name', None) or agent_name
                        
                        # Get content
                        content = getattr(msg, 'content', '')
                        
                        if content:  # Only print if there's actual content
                            print(f"\n[{msg_type}] {sender}:")
                            print(content)
                            print("-" * 50)
                            
            print("="*50)
            print("✅ Task completed!")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again or type 'quit' to exit.")

if __name__ == "__main__":
    run_orchestrator()
