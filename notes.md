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

### Lesson learned
Data should be separated from application logic.