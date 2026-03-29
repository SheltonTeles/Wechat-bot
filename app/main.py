from fastapi import FastAPI, HTTPException
import pandas as pd

"""
This is a demo endpoint that returns a list of grades for different courses. In a real application, you would replace this with actual logic to retrieve grades from a database or another data source(in this case a .xlsx file).

"""

app = FastAPI()
#endpoint; get HTTP method, this tells FASTAPI that this function will be called when a GET request is made to the /grades endpoint

#simulated login mappping
#Later this can be replaced by wechat openid
#Now users are stored in users.xlsx instead of hardcoded

def load_users():
    try:
        df = pd.read_excel("app/users.xlsx")
        return df
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="users.xlsx file not found")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/grades") 
def get_grades(student_id: int, course_code: str = None):
    try:
        df = pd.read_excel("app/grades.xlsx")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="grades.xlsx file not found")
    
    required_columns = {
        "student_id",
        "student_name",
        "course_code",
        "continuous_assessment",
        "exam_grade",
        "final_grade"
    }

    if not required_columns.issubset(df.columns):
        raise HTTPException(
            status_code=500, 
            detail="grades.xlsx file is missing one or more required columns: student_id, student_name, course_code, continuous_assessment, exam_grade, final_grade"
        )
    
    #First filter by student id
    filtered_df = df[df["student_id"] == student_id]

    #Then filter by course_code if provided
    if course_code:
        filtered_df = filtered_df[filtered_df["course_code"] == course_code]

    if filtered_df.empty:
        if course_code:
            raise HTTPException(
                status_code=404, 
                detail=f"No grades found for student_id {student_id} in course {course_code}"
            )
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"No grades found for student_id {student_id}"
            )

    return filtered_df.to_dict(orient="records")


#login simulation endpoint
@app.get("/login")
def login(user_code: str):
    df_users = load_users()

    user = df_users[df_users["user_code"] == user_code]

    if user.empty:
        raise HTTPException(status_code=404, detail="User not found")
    
    student_id = int(user.iloc[0]["student_id"])

    return {
        "message": f"Login successful for {user_code}",
        "student_id": student_id
    }


#endpoint to get grades using user_code instead of student_id
@app.get("/my-grades")
def my_grades(user_code: str, course_code: str = None):
    df_users = load_users()

    user = df_users[df_users["user_code"] == user_code]

    if user.empty:
        raise HTTPException(status_code=404, detail="User not found")

    student_id = int(user.iloc[0]["student_id"])

    try:
        df = pd.read_excel("app/grades.xlsx")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="grades.xlsx file not found")

    required_columns = {
        "student_id",
        "student_name",
        "course_code",
        "continuous_assessment",
        "exam_grade",
        "final_grade"
    }

    if not required_columns.issubset(df.columns):
        raise HTTPException(
            status_code=500, 
            detail="grades.xlsx file is missing required columns"
        )

    #First filter by student id
    filtered_df = df[df["student_id"] == student_id]

    #Then filter by course_code if provided
    if course_code:
        filtered_df = filtered_df[filtered_df["course_code"] == course_code]

    if filtered_df.empty:
        if course_code:
            raise HTTPException(
                status_code=404, 
                detail=f"No grades found for user_code {user_code} in course {course_code}"
            )
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"No grades found for user_code {user_code}"
            )

    return filtered_df.to_dict(orient="records")


'''
the path on terminal should be the root of the project, where the app folder is located run the following command to start the server: uvicorn app.main:app --reload

in my case the path is: C:\\Users\\HP\\Desktop\\chatbot> uvicorn app.main:app --reload

'''

    