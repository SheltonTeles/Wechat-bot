# Student Grade Assistant – Learning Notes

This project is a FastAPI-based backend that simulates a system where students can access their grades using a chatbot-style interface.

The goal is not to replace the university system, but to **learn backend development, API design, and data handling using Python**.

---

# 🔹 FastAPI Basics

## Endpoint

An endpoint is a URL path linked to a function.

Example:

```python
@app.get("/grades")
def get_grades():
    return [...]
```

When a request is sent to `/grades`, this function executes.

---

## Request

A request is sent by a client to the server.

Example:

```
GET /grades?student_id=20240175
```

---

## Response

The server returns data after processing.

Example:

```json
[
  {"course_code": "MATH101", "grade": 87}
]
```

---

## What happens internally

1. Request sent
2. FastAPI matches endpoint
3. Function runs
4. Python returns data
5. FastAPI converts to JSON
6. Response sent (200 OK)

---

# 🔹 Reading Excel with pandas

## Goal

Load data from Excel and return it via API.

## Key function

```python
pd.read_excel("app/grades.xlsx")
```

### What it does

* Opens Excel file
* Converts it into a **DataFrame** (table in memory)

---

## DataFrame

A DataFrame is a table structure in pandas.

Example:

| course_code | grade |
| ----------- | ----- |
| MATH101     | 87    |
| PHY101      | 92    |

---

## Convert to JSON

```python
df.to_dict(orient="records")
```

### What it does

* Converts table to a list of dictionaries
* Required for API response

---

# 🔹 Filtering Data

## Code

```python
filtered_df = df[df["student_id"] == student_id]
```

### What it does

* Compares each row
* Keeps only matching rows

---

## Optional filtering

```python
if course_code:
    filtered_df = filtered_df[filtered_df["course_code"] == course_code]
```

---

# 🔹 Data Structure

## grades.xlsx

| student_id | student_name | course_code | continuous_assessment | exam_grade | final_grade |
| ---------- | ------------ | ----------- | --------------------- | ---------- | ----------- |

---

## users.xlsx

| user_code | student_id | student_name |
| --------- | ---------- | ------------ |

---

## Important Concept

```text
user_code → student_id → grades
```

---

# 🔹 Why NOT use names as ID

Names:

* can have spaces
* accents
* different formats

So:

* use `student_id` internally
* use `student_name` only for display

---

# 🔹 Helper Functions (IMPORTANT)

We created functions to avoid repeating code.

---

## load_users()

```python
def load_users():
    return pd.read_excel("app/users.xlsx")
```

### Purpose

* Reads users file
* Returns DataFrame

---

## load_grades()

```python
def load_grades():
    return pd.read_excel("app/grades.xlsx")
```

### Purpose

* Reads grades file
* Reusable across endpoints

---

## validate_grade_columns(df)

```python
required_columns = {...}
```

### Purpose

* Checks if Excel has correct structure
* Prevents runtime errors

---

## filter_grades(df, student_id, course_code)

```python
df[df["student_id"] == student_id]
```

### Purpose

* Filters grades by student
* Optionally filters by course

---

## handle_empty_grades(...)

### Purpose

* Checks if result is empty
* Raises HTTP error (404)

---

## Why these functions matter

Instead of repeating code:

* write once
* reuse everywhere

This improves:

* readability
* maintainability
* debugging

---

# 🔹 Chatbot Endpoint

## Endpoint

```python
@app.get("/chat")
```

---

## Example request

```
/chat?message=grades shelton
```

---

## How it works

### Step 1

Split message:

```python
parts = message.split()
```

Example:

```
"grades shelton"
→ ["grades", "shelton"]
```

---

### Step 2

Extract command:

```python
command = parts[0]
```

---

### Step 3

Execute logic

Examples:

#### help

Shows commands

#### login

Finds user in users.xlsx

#### grades

* gets student_id
* loads grades
* filters results

---

## Example response

```json
{
  "response": "MATH101 -> Final: 78"
}
```

---

# 🔹 Errors Handling

Using:

```python
raise HTTPException(...)
```

### Purpose

* Return meaningful errors
* Avoid crashing server

---

# 🔹 Common Issues Faced

### 1. Wrong folder

Fix:

```
run from project root
```

---

### 2. File not found

Fix:

```
app/grades.xlsx
```

---

### 3. Column name mismatch

Example:

```
continuous_assessment (correct)
```

---

### 4. Missing module

Fix:

```
pip install pandas
```

---

# 🔹 What I Learned

* How APIs work (request/response)
* How to use FastAPI
* How to read Excel using pandas
* How to filter data
* Importance of clean structure
* Difference between logic and data
* Basic chatbot design
* Real-world constraints (university systems)

---

# 🔹 Future Improvements

* Replace Excel with database
* Add authentication
* Connect to WeChat chatbot
* Improve command parsing
* Add notifications

---

# Final Understanding

This project simulates a real system:

```
User → API → Data → Response
```

and now:

```
User → Chat message → API → Data → Response
```

---

# Key Insight

Backend is not just code.

It is:

* data handling
* structure
* logic
* communication between systems
