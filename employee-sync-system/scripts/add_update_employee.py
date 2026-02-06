import sqlite3
import os
from datetime import datetime
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "hr_system.db"

def add_employee(employee_id, first_name, last_name, email, department, position, salary):
    """Add or update an employee in the HR system"""
    
    if not DB_PATH.exists():
        raise FileNotFoundError(f"❌ Database not found at {DB_PATH}. Run init_hr_db.py first.")

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Check if the employee exists
    cursor.execute("SELECT * FROM employees WHERE employee_id = ?", (employee_id,))
    existing = cursor.fetchone()

    # Insert new employee
    if not existing:
        cursor.execute("""
            INSERT INTO employees (
                employee_id, first_name, last_name, email, department, position, salary
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (employee_id, first_name, last_name, email, department, position, salary))
        print(f"🆕 Added new employee: {first_name} {last_name} ({employee_id})")
    else:
        print(f"❌ Employee {employee_id} already exists. Use update_employee() instead.")
        conn.close()
        return

    conn.commit()

    # Check if trigger fired
    cursor.execute("SELECT * FROM employee_change_log WHERE employee_id = ? ORDER BY change_timestamp DESC LIMIT 1", (employee_id,))
    trigger_row = cursor.fetchone()

    # Show employee details
    cursor.execute("SELECT * FROM employees WHERE employee_id = ?", (employee_id,))
    updated_row = cursor.fetchone()
    
    if updated_row:
        print(f"   📋 Employee Details:")
        print(f"      ID: {updated_row[0]}")
        print(f"      Name: {updated_row[1]} {updated_row[2]}")
        print(f"      Email: {updated_row[3]}")
        print(f"      Department: {updated_row[4]}")
        print(f"      Position: {updated_row[5]}")
        print(f"      Salary: ${updated_row[6]:,.2f}")

    if trigger_row:
        print(f"✅ Trigger executed: employee_id '{employee_id}' added to change_log.")
    else:
        print(f"⚠️ Trigger did NOT execute for employee_id '{employee_id}'.")

    conn.close()

def update_employee(employee_id, **updates):
    """Update an existing employee's information"""
    
    if not DB_PATH.exists():
        raise FileNotFoundError(f"❌ Database not found at {DB_PATH}. Run init_hr_db.py first.")

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Check if employee exists
    cursor.execute("SELECT * FROM employees WHERE employee_id = ?", (employee_id,))
    existing = cursor.fetchone()
    
    if not existing:
        print(f"❌ Employee {employee_id} not found.")
        conn.close()
        return

    # Build update query
    valid_fields = ['first_name', 'last_name', 'email', 'department', 'position', 'salary', 'status']
    update_fields = {k: v for k, v in updates.items() if k in valid_fields and v is not None}
    
    if not update_fields:
        print("❌ No valid fields to update.")
        conn.close()
        return

    set_clause = ", ".join([f"{field} = ?" for field in update_fields.keys()])
    values = list(update_fields.values()) + [employee_id]
    
    cursor.execute(f"UPDATE employees SET {set_clause} WHERE employee_id = ?", values)
    conn.commit()

    print(f"🔁 Updated employee: {employee_id}")
    print(f"   📝 Updated fields: {', '.join(update_fields.keys())}")

    # Check if trigger fired
    cursor.execute("SELECT * FROM employee_change_log WHERE employee_id = ? ORDER BY change_timestamp DESC LIMIT 1", (employee_id,))
    trigger_row = cursor.fetchone()

    if trigger_row:
        print(f"✅ Trigger executed: employee_id '{employee_id}' change logged.")
    else:
        print(f"⚠️ Trigger did NOT execute for employee_id '{employee_id}'.")

    conn.close()

if __name__ == "__main__":
    
    # 🧾 CHANGE THIS DATA TO ADD/UPDATE EMPLOYEES
    
    # Option 1: Add a new employee
    new_employee = {
        "employee_id": "EMP02",
        "first_name": "Bhavish  ",
        "last_name": "patel",
        "email": "bhavish.patel@company.com",
        "department": "engineering",
        "position": "engineering Specialist",
        "salary": 102000.00
    }
    
    # Uncomment to add the new employee:
    add_employee(**new_employee)
    
    # Option 2: Update an existing employee
    # employee_updates = {
    #     "employee_id": "EMP001",  # John Doe
    #     "salary": 105000.00,      # Salary increase
    #     "position": "Principal Developer"  # Promotion
    # }
    
    # # Uncomment to update the employee:
    # update_employee(**employee_updates)
    
    # # Option 3: Another update example
    # # update_employee(
    # #     employee_id="EMP002",
    # #     department="Digital Marketing",
    # #     salary=92000.00
    # # )
