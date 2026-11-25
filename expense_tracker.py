
import sqlite3
from datetime import datetime
import re
import csv

# Personal Expense Tracker

DB_NAME = "expenses.db"


# Create database tables
def create_table():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            month TEXT PRIMARY KEY,
            amount REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Validate date
def validate_date(date):

    try:
        datetime.strptime(date, "%d-%m-%Y")
        return True

    except ValueError:
        return False


# Display expenses in a formatted table
def display_expense_table(records):

    if not records:
        print("No expenses found.")
        return

    print("\n" + "=" * 85)
    print(
        f"{'ID':<5}{'NAME':<22}{'AMOUNT':<15}"
        f"{'CATEGORY':<20}{'DATE':<15}"
    )
    print("-" * 85)

    total = 0

    for expense in records:

        expense_id, name, amount, category, date = expense

        print(
            f"{expense_id:<5}"
            f"{name[:20]:<22}"
            f"{'₹' + format(amount, '.2f'):<15}"
            f"{category[:18]:<20}"
            f"{date:<15}"
        )

        total += amount

    print("-" * 85)
    print(f"Total Expenses: ₹{total:.2f}")
    print(f"Number of Expenses: {len(records)}")
    print("=" * 85)


# Calculate spending for a particular month
def get_monthly_spending(month_key):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT amount, date FROM expenses")
    records = cursor.fetchall()

    conn.close()

    total = 0

    for amount, date in records:

        expense_date = datetime.strptime(date, "%d-%m-%Y")

        if expense_date.strftime("%Y-%m") == month_key:
            total += amount

    return total


# Check monthly budget
def check_monthly_budget():

    current_month = datetime.today().strftime("%Y-%m")
    month_name = datetime.today().strftime("%B %Y")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT amount FROM budgets WHERE month = ?",
        (current_month,)
    )

    result = cursor.fetchone()
    conn.close()

    if result is None:
        return

    budget = result[0]
    spent = get_monthly_spending(current_month)
    remaining = budget - spent

    print("\n===== MONTHLY BUDGET STATUS =====")
    print("Month:", month_name)
    print(f"Budget: ₹{budget:.2f}")
    print(f"Spent: ₹{spent:.2f}")

    if remaining > 0:
        print(f"Remaining budget: ₹{remaining:.2f}")

    elif remaining == 0:
        print("Warning: You have reached your monthly budget!")

    else:
        print(
            f"WARNING: You exceeded your budget by "
            f"₹{abs(remaining):.2f}"
        )


# Feature 1: Add an expense
def add_expense():

    while True:
        expense_name = input("Enter expense name: ").strip()

        if expense_name:
            break
        else:
            print("Expense name cannot be empty.")

    while True:
        try:
            amount = float(input("Enter amount: "))

            if amount > 0:
                break
            else:
                print("Amount must be greater than zero.")

        except ValueError:
            print("Invalid input! Please enter a number.")

    while True:
        category = input("Enter category: ").strip()

        if category:
            break
        else:
            print("Category cannot be empty.")

    while True:
        date = input("Enter date (DD-MM-YYYY): ").strip()

        if not re.fullmatch(r"\d{2}-\d{2}-\d{4}", date):
            print("Please enter date in DD-MM-YYYY format.")
            continue

        if validate_date(date):
            break
        else:
            print("Invalid date! Please enter a valid date.")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO expenses (name, amount, category, date)
        VALUES (?, ?, ?, ?)
    """, (expense_name, amount, category, date))

    conn.commit()
    conn.close()

    print("\nExpense added successfully!")
    check_monthly_budget()


# Feature 2: View expenses
def view_expenses():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, amount, category, date
        FROM expenses
        ORDER BY id
    """)

    records = cursor.fetchall()
    conn.close()

    print("\n========== ALL EXPENSES ==========")
    display_expense_table(records)


# Feature 3: Calculate total expenses
def calculate_total():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount), COUNT(*) FROM expenses")

    total, count = cursor.fetchone()
    conn.close()

    total = total if total is not None else 0

    print("\n========== EXPENSE TOTAL ==========")
    print(f"Total Expenses: ₹{total:.2f}")
    print("Number of Expenses:", count)


# Feature 4: Category-wise summary
def category_summary():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, SUM(amount), COUNT(*)
        FROM expenses
        GROUP BY category
        ORDER BY SUM(amount) DESC
    """)

    records = cursor.fetchall()
    conn.close()

    print("\n========== CATEGORY-WISE SUMMARY ==========")

    if not records:
        print("No expenses recorded yet.")
        return

    print("-" * 55)
    print(f"{'CATEGORY':<25}{'TOTAL AMOUNT':<18}{'COUNT':<10}")
    print("-" * 55)

    for category, total, count in records:
     print(
        f"{category[:23]:<25}"
        f"{'₹' + format(total, '.2f'):<18}"
        f"{count:<10}"
    )

    print("-" * 55)


# Feature 5: Update an expense
def update_expense():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        expense_id = int(input("Enter expense ID to update: "))

        cursor.execute(
            "SELECT * FROM expenses WHERE id = ?",
            (expense_id,)
        )

        expense = cursor.fetchone()

        if expense is None:
            print("Expense ID not found.")

        else:
            print("Current expense:", expense)

            while True:
                try:
                    new_amount = float(input("Enter new amount: "))

                    if new_amount > 0:
                        break
                    else:
                        print("Amount must be greater than zero.")

                except ValueError:
                    print("Please enter a valid number.")

            cursor.execute(
                "UPDATE expenses SET amount = ? WHERE id = ?",
                (new_amount, expense_id)
            )

            conn.commit()
            print("Expense updated successfully!")

            check_monthly_budget()

    except ValueError:
        print("Please enter a valid expense ID.")

    finally:
        conn.close()


# Feature 6: Delete an expense
def delete_expense():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        expense_id = int(input("Enter expense ID to delete: "))

        cursor.execute(
            "SELECT * FROM expenses WHERE id = ?",
            (expense_id,)
        )

        expense = cursor.fetchone()

        if expense is None:
            print("Expense ID not found.")

        else:
            print("Expense to be deleted:", expense)

            confirm = input(
                "Are you sure you want to delete this expense? (yes/no): "
            ).strip().lower()

            if confirm == "yes":

                cursor.execute(
                    "DELETE FROM expenses WHERE id = ?",
                    (expense_id,)
                )

                conn.commit()
                print("Expense deleted successfully!")

                check_monthly_budget()

            else:
                print("Deletion cancelled.")

    except ValueError:
        print("Please enter a valid expense ID.")

    finally:
        conn.close()


# Feature 7: Search an expense
def search_expense():

    search_term = input(
        "Enter expense name or category to search: "
    ).strip()

    if not search_term:
        print("Search term cannot be empty.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, amount, category, date
        FROM expenses
        WHERE name LIKE ? COLLATE NOCASE
        OR category LIKE ? COLLATE NOCASE
    """, ("%" + search_term + "%", "%" + search_term + "%"))

    records = cursor.fetchall()
    conn.close()

    print("\n========== SEARCH RESULTS ==========")
    display_expense_table(records)


# Feature 8: Date-wise expense filtering
def date_filter():

    print("\n===== DATE-WISE EXPENSE FILTER =====")
    print("1. Search by a specific date")
    print("2. Search between two dates")

    choice = input("Enter your choice: ")

    if choice not in ["1", "2"]:
        print("Invalid choice.")
        return

    while True:
        start_date = input(
            "Enter date (DD-MM-YYYY): "
        ).strip()

        if validate_date(start_date):
            break
        else:
            print("Invalid date! Please enter a valid date.")

    if choice == "2":

        while True:
            end_date = input(
                "Enter ending date (DD-MM-YYYY): "
            ).strip()

            if validate_date(end_date):
                break
            else:
                print("Invalid date! Please enter a valid date.")

        start = datetime.strptime(start_date, "%d-%m-%Y")
        end = datetime.strptime(end_date, "%d-%m-%Y")

        if start > end:
            print("Starting date cannot be after ending date.")
            return

    else:
        end_date = start_date

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, amount, category, date
        FROM expenses
    """)

    records = cursor.fetchall()
    conn.close()

    filtered_records = []

    start = datetime.strptime(start_date, "%d-%m-%Y")
    end = datetime.strptime(end_date, "%d-%m-%Y")

    for expense in records:

        expense_date = datetime.strptime(
            expense[4], "%d-%m-%Y"
        )

        if start <= expense_date <= end:
            filtered_records.append(expense)

    print("\n========== FILTERED EXPENSES ==========")
    display_expense_table(filtered_records)


# Feature 9: Monthly expense summary
def monthly_summary():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT amount, date FROM expenses")

    records = cursor.fetchall()
    conn.close()

    if not records:
        print("No expenses recorded yet.")
        return

    monthly_totals = {}

    for amount, date in records:

        expense_date = datetime.strptime(date, "%d-%m-%Y")
        month_key = expense_date.strftime("%Y-%m")
        month_name = expense_date.strftime("%B %Y")

        if month_key not in monthly_totals:
            monthly_totals[month_key] = [month_name, 0, 0]

        monthly_totals[month_key][1] += amount
        monthly_totals[month_key][2] += 1

    print("\n========== MONTHLY EXPENSE SUMMARY ==========")
    print("-" * 55)
    print(f"{'MONTH':<22}{'TOTAL':<18}{'COUNT':<10}")
    print("-" * 55)

    for key in sorted(monthly_totals):

        month, total, count = monthly_totals[key]

        print(
            f"{month:<22}"
            f"{'₹' + format(total, '.2f'):<18}"
            f"{count:<10}"
        )

    print("-" * 55)


# Feature 10: Monthly budget
def monthly_budget():

    current_month = datetime.today().strftime("%Y-%m")
    month_name = datetime.today().strftime("%B %Y")

    print("\n========== MONTHLY BUDGET ==========")
    print("1. Set monthly budget")
    print("2. View budget status")

    choice = input("Enter your choice: ")

    if choice == "1":

        while True:
            try:
                budget = float(input("Enter your monthly budget: ₹"))

                if budget > 0:
                    break
                else:
                    print("Budget must be greater than zero.")

            except ValueError:
                print("Please enter a valid amount.")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO budgets (month, amount)
            VALUES (?, ?)
            ON CONFLICT(month)
            DO UPDATE SET amount = excluded.amount
        """, (current_month, budget))

        conn.commit()
        conn.close()

        print("Monthly budget saved successfully for", month_name)
        check_monthly_budget()

    elif choice == "2":

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT amount FROM budgets WHERE month = ?",
            (current_month,)
        )

        result = cursor.fetchone()
        conn.close()

        if result is None:
            print("No budget has been set for this month.")
        else:
            check_monthly_budget()

    else:
        print("Invalid choice.")


# Feature 11: Export expenses to CSV
def export_to_csv():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, amount, category, date
        FROM expenses
        ORDER BY id
    """)

    records = cursor.fetchall()
    conn.close()

    if not records:
        print("No expenses available to export.")
        return

    try:
        with open(
            "expenses_export.csv",
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "ID",
                "Expense Name",
                "Amount",
                "Category",
                "Date"
            ])

            writer.writerows(records)

        print("\nExpenses exported successfully!")
        print("File name: expenses_export.csv")
        print("Location: Project folder")

    except OSError as error:
        print("Unable to export file:", error)


# Feature 12: Overall expense report
def overall_report():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*),
            SUM(amount),
            AVG(amount),
            MAX(amount)
        FROM expenses
    """)

    count, total, average, highest = cursor.fetchone()

    cursor.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        GROUP BY category
        ORDER BY SUM(amount) DESC
        LIMIT 1
    """)

    top_category = cursor.fetchone()

    conn.close()

    print("\n" + "=" * 45)
    print("          OVERALL EXPENSE REPORT")
    print("=" * 45)

    if count == 0:
        print("No expenses recorded yet.")
        return

    print(f"Total Transactions : {count}")
    print(f"Total Spending     : ₹{total:.2f}")
    print(f"Average Expense    : ₹{average:.2f}")
    print(f"Highest Expense    : ₹{highest:.2f}")

    print("-" * 45)

    print(
        "Highest Spending Category:",
        top_category[0]
    )

    print(f"Category Spending: ₹{top_category[1]:.2f}")

    print("=" * 45)


# Create tables when program starts
create_table()


# Main menu
while True:

    print("\n========== PERSONAL EXPENSE TRACKER ==========")
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. Calculate Total")
    print("4. Category-wise Summary")
    print("5. Update Expense")
    print("6. Delete Expense")
    print("7. Search Expense")
    print("8. Date-wise Expense Filter")
    print("9. Monthly Expense Summary")
    print("10. Set/Check Monthly Budget")
    print("11. Export Expenses to CSV")
    print("12. Overall Expense Report")
    print("13. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        add_expense()

    elif choice == "2":
        view_expenses()

    elif choice == "3":
        calculate_total()

    elif choice == "4":
        category_summary()

    elif choice == "5":
        update_expense()

    elif choice == "6":
        delete_expense()

    elif choice == "7":
        search_expense()

    elif choice == "8":
        date_filter()

    elif choice == "9":
        monthly_summary()

    elif choice == "10":
        monthly_budget()

    elif choice == "11":
        export_to_csv()

    elif choice == "12":
        overall_report()

    elif choice == "13":
        print("Thank you for using Expense Tracker!")
        break

    else:
        print("Invalid choice. Please try again.")
