## FastAPI Basics

### Endpoint

An endpoint is a URL path in the API that is linked to a function.

Example:

```python
@app.get("/demo-grades")
def demo_grades():
    return [...]
```

This means when a GET request is sent to `/demo-grades`, the function runs.

---

### Request

A request is an HTTP message sent from a client to the server.

Example:

```
GET /demo-grades
```

It tells the server what data is being asked.

---

### Response

A response is what the server sends back after processing a request.

Example:

```json
[
  {"course_code": "MATH101", "grade": 87}
]
```

---

### What happened in my test

1. Swagger UI sent a GET request to `/demo-grades`
2. FastAPI matched the endpoint
3. The function `demo_grades()` executed
4. Python returned a list of dictionaries
5. FastAPI converted it into JSON
6. The server returned a 200 OK response
7. Swagger displayed the result

---

### Notes

* FastAPI automatically converts Python → JSON
* Swagger UI is useful for testing endpoints
* `--reload` updates the server automatically when saving

---

### Mistakes / Issues

* Running uvicorn in the wrong folder caused import errors
* Opening `/` gave 404 because no root endpoint was defined


## Reading Excel with pandas

### Goal
pandas is a pytohn library for working with tabular data
Load data from an Excel file and return it through an API.

---

### Code

```python
@app.get("/grades")
def get_grades():
    import pandas as pd
    #this creates an alias
    #instead of working with panda.read_excel
    #it becomes pd.read_excel`

    df = pd.read_excel("app/grades.xlsx")
    #this reads the excel file and stores it in a variable named df (short for DataFrame)
    #A DataFrame is a pandas table structure, like a spreadsheet in memory (eg: grades.xlsx)
    #So df contains the whole excel sheet
    #the above function opens the .xlsx file and converts it into a DataFrame
    return df.to_dict(orient="records")
```

---

### What happens step by step

1. A GET request is sent to `/grades`
2. FastAPI matches the endpoint
3. The function `get_grades()` executes
4. `pandas.read_excel()` reads the Excel file into a DataFrame
5. The DataFrame is converted to a list of dictionaries:

   ```python
   df.to_dict(orient="records")
   ```
6. FastAPI converts the result to JSON
7. The server returns a 200 OK response

---

### DataFrame

A DataFrame is a table-like data structure in pandas.

Example:

| course_code | grade |
| ----------- | ----- |
| MATH101     | 87    |
| PHY101      | 92    |

---

### File Path Issue

Error encountered:

```
FileNotFoundError: No such file or directory: 'grades.xlsx'
```

Cause:

* Python looks for files relative to the **current working directory**
* The file was inside `app/`, not the root folder

Fix:

```python
pd.read_excel("app/grades.xlsx")
```

---

### Notes

* Use forward slashes `/` in paths (even on Windows)
* File location must match the path exactly
* pandas requires `openpyxl` for `.xlsx` files

---

### Learned

* How to read Excel using pandas
* How to convert DataFrame → JSON
* How file paths work in Python
* Difference between code errors and file system errors

## Filtering grades by student

### Goal
Return only the grades that belong to one student.

### Code
```python
@app.get("/grades")
def get_grades(student_id: int):
    import pandas as pd

    df = pd.read_excel("app/grades.xlsx")
    filtered_df = df[df["student_id"] == student_id]
    # df["student_id"] == student_id
    # Creates a boolean comparison for every row.

    # to_dict(orient="records")
    # Converts the filtered DataFrame into a list of dictionaries, which FastAPI then returns as JSON.
    return filtered_df.to_dict(orient="records")

    ## Multiple Filters in API

### Goal

Allow filtering grades by both student_id and course_code.

---

### Code

```python
@app.get("/grades")
def get_grades(student_id: int, course_code: str = None):
    import pandas as pd

    df = pd.read_excel("app/grades.xlsx")

    filtered_df = df[df["student_id"] == student_id]

    if course_code:
        filtered_df = filtered_df[filtered_df["course_code"] == course_code]

    return filtered_df.to_dict(orient="records")
```

---

### Concepts

#### Optional parameter

`course_code: str = None`
Means the parameter is not required.

---

#### Conditional filtering

The filter is only applied if the parameter exists.

---

#### Chained filtering

Data is filtered step by step:

1. by student_id
2. then by course_code (if provided)

---

### Example requests

All grades:

```id="r1"
/grades?student_id=20240175
```

Specific course:

```id="r2"
/grades?student_id=20240175&course_code=MATH101
```

---

### Lesson learned

* APIs can accept multiple parameters
* Filtering can be dynamic
* This mimics database queries

## Grade Structure (0–100 System)

### Design

Each row represents one student’s result in one course.

---

### Columns

* student_id
* course_code
* course_name
* continuous_assessment
* exam_grade
* final_grade

---

### Example

| student_id | course_code | continuous_assessment | exam_grade | final_grade |
| ---------- | ----------- | --------------------- | ---------- | ----------- |
| 20240175   | MATH101     | 75                    | 80         | 78          |

---

### Notes

* Grades are numeric (0–100)
* continuous_assessment and exam_grade are components of the same course
* final_grade can be stored or calculated

---

### Lesson learned

* Related data should be stored in the same row
* Structure should match real-world meaning
* API automatically returns all columns from DataFrame
`
## User Storage

### Problem
Hardcoding users inside the code is not scalable.

### Solution
Store users in an external file (users.xlsx).

### Structure
| username | student_id |

### Benefit
- Easier to update
- No need to modify code
- More realistic system design

Chatbot Endpoint
Goal

Allow users to interact with the system using chat-like commands instead of directly calling API endpoints.

Example:

help
login shelton
grades shelton
grades shelton MATH101
Endpoint
@app.get("/chat")
def chat(message: str):

The endpoint receives a text message and interprets it as a command.

Message Processing
split()
parts = message.strip().split()

Example:

"grades shelton".split()

Result:

["grades", "shelton"]
strip()

Removes extra spaces at the beginning and end.

Example:

"  grades shelton  ".strip()

Result:

"grades shelton"
lower()
command = parts[0].lower()

Converts text to lowercase.

Example:

"HELP".lower()

Result:

"help"

This allows commands to be case-insensitive.

Command Routing

The chatbot checks which command the user entered.

Example:

if command == "help":
elif command == "login":
elif command == "grades":

This pattern is called command routing.

Example Flow

User sends:

grades shelton

Processing:

Message received
↓
Split into words
↓
Detect command "grades"
↓
Find student in users.xlsx
↓
Find grades in grades.xlsx
↓
Build response text
↓
Return response
Lesson Learned

A chatbot is essentially:

Input
↓
Interpretation
↓
Business Logic
↓
Response

The same backend logic can later be connected to:

WeChat
DingTalk
Telegram
Web UI

without changing the core system.

Refactoring the Code
Goal

Avoid repeating the same code multiple times.

Before

Both /grades and /my-grades contained:

pd.read_excel(...)
required_columns = {...}
filtered_df = ...

Repeated code is harder to maintain.

After

Created helper functions:

load_users()
def load_users():

Loads data from:

users.xlsx
load_grades()
def load_grades():

Loads data from:

grades.xlsx
validate_grade_columns()
def validate_grade_columns(df):

Checks whether all required columns exist.

filter_grades()
def filter_grades(df, student_id, course_code=None):

Filters the DataFrame.

handle_empty_grades()
def handle_empty_grades(...):

Returns a 404 error when no records are found.

Benefits
Less duplicated code
Easier debugging
Easier maintenance
More professional project structure
Frontend Chat Interface
Goal

Create a user interface that looks like a chat application.

Architecture
User
↓
Chat UI (HTML/CSS/JavaScript)
↓
/chat endpoint
↓
FastAPI
↓
Excel files
↓
Response
fetch()

The frontend sends messages using:

fetch(...)

Example:

const response = await fetch(
    `http://127.0.0.1:8000/chat?message=${message}`
);
async / await

Allows JavaScript to wait for the server response.

Example:

const response = await fetch(...)

Without await, the code would continue before the response arrives.

JSON Response

FastAPI returns:

{
  "response": "Grades for Shelton..."
}

JavaScript converts it into an object:

const data = await response.json();
Lesson Learned

The frontend does not directly access Excel files.

Instead:

Frontend
↓
API
↓
Data

This separation is a fundamental principle of modern web applications.

Project Architecture
Current System
Student
↓
Chat Interface
↓
FastAPI Backend
↓
Command Parser
↓
Excel Storage
↓
Response
Technologies Used
FastAPI

Used to create REST API endpoints.

pandas

Used to:

Read Excel files
Filter records
Process tabular data
Excel (.xlsx)

Used as a lightweight database for prototyping.

Files:

users.xlsx
grades.xlsx
HTML

Creates the user interface.

CSS

Styles the chat interface.

JavaScript

Handles communication between frontend and backend.

Future Improvements
Authentication

Replace:

user_code

with:

WeChat OpenID
DingTalk User ID
University Account
Database

Replace Excel with:

SQLite
PostgreSQL
MySQL
AI Features

Allow natural language queries such as:

What is my Math grade?

instead of:

grades shelton MATH101

using an LLM or NLP model.

Platform Integration

Potential integrations:

WeChat
DingTalk
Telegram
AstrBot