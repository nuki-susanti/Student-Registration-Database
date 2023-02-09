import typer
from rich.console import Console
from rich.table import Table
from datetime import datetime

from db import resetting_db, populating_db, showing_department, showing_course, showing_student, adding_department, adding_course, adding_student, showing_prereq, adding_prereq, showing_enrolled, enrolling_student, updating_grade, showing_transcript

app = typer.Typer()
console = Console()

def pretty_table(with_headers, data, in_color):
    table = Table(*with_headers, show_header=True,
                  header_style=f"bold {in_color}")

    for row in data:
        table.add_row(*map(str, row))

    console.print(table)
    

@app.command()
def reset_db(data_seed: bool = True):
    user_answer = input(
        "Are you sure? This will delete all the data. (y/n): ").strip().lower()

    if user_answer == "y":
        resetting_db()
        typer.echo("Successfully reset database")

        # It will automatically populate database with data seed stored in db_seed.
        # Otherwise user should specify --no-data-seed
        if data_seed:
            populating_db() 
    else:
        typer.echo("Database reset aborted")


@app.command()
def add_department():
    user_answer = input("Do you want to add a department? (y/n): ").strip().lower()

    if user_answer == "y":
        
        dept_id = input("Enter department ID: ").lower()
        dept_name = input("Enter department name: ").lower()
        dean_name = input("Enter dean name of the department (optional): ").lower()
        building = input("Enter building name (optional): ").lower()
        
        try:
            room = int(input("Enter room number (optional): ").strip())
        except:
            room = None

        dept_details = (dept_id, dept_name, dean_name, building, room)

        adding_department(dept_details)
    else:
        typer.echo("Okay. Thank you!")


@app.command()
def show_department():
    user_answer = input("Do you want to see one particular department?. Enter department name: ").strip().lower()
    
    if user_answer:
        pretty_table(["Department ID", "Department Name", "Dean Name", "Building", "Room"],
                    data=showing_department(user_answer), in_color="green")
    else:
        department = None
        typer.echo(typer.style("Showing all departments...", bg=typer.colors.WHITE, fg=typer.colors.GREEN))
        pretty_table(["No", "Department ID", "Department Name", "Dean Name", "Building", "Room"],
                    data=showing_department(department), in_color="green")


@app.command()
def show_course():
    user_answer = input("Enter department ID: ").strip().lower()
    
    if user_answer:
        pretty_table(["Department ID", "Course ID", "Course Name", "Duration (hr)"],
                    data=showing_course(user_answer), in_color="green")
    else:
        department = None
        typer.echo(typer.style("Showing all courses...", bg=typer.colors.WHITE, fg=typer.colors.GREEN))
        pretty_table(["No", "Department ID", "Course ID", "Course Name", "Duration (hr)"],
                    data=showing_course(department), in_color="green")


@app.command()
def add_course():
    user_answer = input("Do you want to add a course? (y/n): ").strip().lower()

    if user_answer == "y":
        dept_id = input("Enter department ID: ").lower()
        course_id = input("Enter course ID: ").lower()
        course_name = input("Enter course name: ").lower()

        try:
            hour = int(input("Enter the duration of the course in hour: ").strip())
        except:
            hour = None

        course_details = (dept_id, course_id, course_name, hour)

        adding_course(course_details)
    else:
        typer.echo("Okay. Thank you!")


@app.command()
def show_student():
    user_answer = input("Search for student's name: ").strip().lower()
    
    if user_answer:
        pretty_table(["Student ID", "First Name", "Last Name", "GPA"],
                 data=showing_student(user_answer), in_color="green")
    else:
        student_name = None
        typer.echo(typer.style("Showing all students...", bg=typer.colors.WHITE, fg=typer.colors.GREEN))
        pretty_table(["No", "Student ID", "First Name", "Last Name", "GPA"],
                 data=showing_student(student_name), in_color="green")


@app.command()
def add_student():
    user_answer = input("Do you want add a student? (y/n): ").strip().lower()

    if user_answer == "y":
        student_id = input("Enter student id: ").lower()
        first_name = input("Enter student's first name: ").lower()
        last_name = input("Enter student's last name: ").lower()

        student_details = (student_id, first_name, last_name)

        adding_student(student_details)
    else:
        typer.echo("Okay. Thank you!")


@app.command()
def show_prereq():
    user_answer = input("Enter course ID: ").strip().lower()
    
    if user_answer:
        pretty_table(["Course ID", "Course Prerequisites", "Minimum Grade"],
                 data=showing_prereq(user_answer), in_color="green")
    else:
        course_id = None
        typer.echo(typer.style("Showing all course prerequisites...", bg=typer.colors.WHITE, fg=typer.colors.GREEN))
        pretty_table(["No", "Course ID", "Course Prerequisites", "Minimum Grade"],
                    data=showing_prereq(course_id), in_color="green")
    

@app.command()
def add_prereq():
    user_answer = input(
        "Do you want to add prerequisite for a course? (y/n): ").strip().lower()

    if user_answer == "y":
        course_id = input("Enter course ID: ").lower()
        course_prereq_id = input("Enter course prerequisite: ").lower()

        try:
            min_grade = int(input("Enter the minimum grade for the course: ").strip())
        except:
            min_grade = 50  # default minimum grade            

        prereq_details = (course_id, course_prereq_id, min_grade)

        adding_prereq(prereq_details)
    else:
        typer.echo("Okay. Thank you!")


@app.command()
def show_enrolled():
    user_answer = input("Enter student ID: ").strip().lower()
    
    if user_answer:
        pretty_table(["Student ID", "Course ID", "Enrollment year", "Grade"],
                 data=showing_enrolled(user_answer), in_color="green")
    else:
        course_id = None
        typer.echo(typer.style("Showing all enrolled students...", bg=typer.colors.WHITE, fg=typer.colors.GREEN))
        pretty_table(["No", "Student ID", "Course ID", "Enrollment year", "Grade"],
                    data=showing_enrolled(course_id), in_color="green")


@app.command()
def enroll_student():
    user_answer = input(
        "Do you want to enroll a student? (y/n): ").strip().lower()

    if user_answer == "y":
        student_id = input("Enter your student id: ").strip().lower()
        course_id = input("Enter your course id you want to enroll: ").strip().lower()
        year = datetime.now().year

        enrollment_details = (student_id, course_id, year)

        enrolling_student(enrollment_details)
    else:
        typer.echo("Okay. Thank you!")


@app.command()
def update_grade():
    user_answer = input("Do you want to update course grade? (y/n): ").strip().lower()

    if user_answer == "y":
        student_id = input("Enter your student id: ").strip().lower()
        course_id = input("Enter the course id: ").strip().lower()

        try:
            year = int(input("Enter the year: ").strip())
        except:
            year = datetime.now().year

        grade = int(input("Enter your grade: ").strip())

        updating_grade(student_id, course_id, year, grade)
    else:
        typer.echo("Okay. Thank you!")
    

@app.command()
def show_transcript():
    student_id = input("Enter your student id: ").strip().lower()

    if student_id:
        data = showing_transcript(student_id)
        pretty_table(["Student ID", "First Name", "Last Name", "GPA", "Letter Grade"], data=data, in_color="green")
    else:
        typer.echo("Okay. Thank you!")



if __name__ == "__main__":
    app()
