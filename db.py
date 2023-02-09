from dotenv import load_dotenv
from os import environ as env
from mysql.connector import connect, Error, IntegrityError, DatabaseError
import db_seed
from collections import namedtuple
import typer

load_dotenv()


def create_server_connection():
    connection = None
    try:
        connection = connect(
            user=env.get("USERNAME"),
            password=env.get("PASSW"),
            host=env.get("HOST"),
            port=env.get("PORT"),
            database=env.get("DB")
        )

        print("Successfully connected to MySQL")
    except Error as err:
        print(f"Error: '{err}'")

    return connection


def resetting_db():
    try:
        with create_server_connection() as con:
            with con.cursor() as cur:
                with open('sql_query.sql', 'r') as file:
                    for statement in cur.execute(file.read(), multi=True):
                        print(f"Executed: {statement.statement}")
    except Error as err:
        print(f"Error: '{err}'")


def query(connection, query, data=None, many=False, fetch=None):
    cur = connection.cursor()

    try:
        if many:
            cur.executemany(query, data)
        else:
            cur.execute(query, data)

        if fetch:
            return cur.fetchall()
        else:
            connection.commit()

        print(f"Executed successfully: {query}")

        typer.echo(typer.style("Successful!",
                   bg=typer.colors.WHITE, fg=typer.colors.GREEN))

    except (IntegrityError, DatabaseError, Error) as err:
        typer.echo(
            f"Failed. You have an error message: {typer.style(err, bg=typer.colors.WHITE, fg=typer.colors.RED)}")
    finally:
        cur.close()


def populating_db():

    sql_departments = "INSERT INTO departments(dept_id, dept_name, dean_name, building, room) VALUES(%s, %s, %s, %s, %s);"
    sql_courses = "INSERT INTO courses(dept_id, course_id, course_name, hour) VALUES(%s, %s, %s, %s);"
    sql_prerequisites = "INSERT INTO prerequisites(course_id, course_prereq_id, min_grade) VALUES(%s, %s, %s);"
    sql_students = "INSERT INTO students(student_id, first_name, last_name) VALUES(%s, %s, %s);"

    with create_server_connection() as con:
        query(con, sql_departments, db_seed.seed_departments, many=True)
        query(con, sql_courses, db_seed.seed_courses, many=True)
        query(con, sql_prerequisites, db_seed.seed_prerequisites, many=True)
        query(con, sql_students, db_seed.seed_students, many=True)
        print("Database is successfully initialized.")


def showing_department(department):
    with create_server_connection() as con:
        
        if department != None:
            sql_script = "SELECT dept_id, dept_name, dean_name, building, room FROM departments WHERE dept_name = %s;"
            return query(con, sql_script, data=(department, ), fetch=True)
        else:
            sql_script = "SELECT * FROM departments;"
            return query(con, sql_script, fetch=True)


def adding_department(dept_details):
    with create_server_connection() as con:
        sql_script = "INSERT INTO departments(dept_id, dept_name, dean_name, building, room) VALUES(%s, %s, %s, %s, %s);"
        query(con, sql_script, dept_details)


def showing_course(department):
    with create_server_connection() as con:
        
        if department != None:
            sql_script = "SELECT dept_id, course_id, course_name, hour FROM courses WHERE dept_id = %s;"
            return query(con, sql_script, data=(department, ), fetch=True)
        else:
            sql_script = "SELECT * FROM courses;"
            return query(con, sql_script, fetch=True)


def adding_course(course_details):
    with create_server_connection() as con:
        sql_script = "INSERT INTO courses(dept_id, course_id, course_name, hour) VALUES(%s, %s, %s, %s);"
        query(con, sql_script, course_details)


def showing_student(student_name):
    with create_server_connection() as con:

        if student_name != None:     
            student = ('%' + student_name + '%', '%' + student_name + '%',) # Regex
            sql_script = """
                SELECT student_id, first_name, last_name, gpa FROM students WHERE first_name LIKE %s OR last_name LIKE %s
            """
            return query(con, sql_script, data=(student), fetch=True)
        else:
            sql_script = "SELECT * FROM students;"
            return query(con, sql_script, fetch=True)


def adding_student(student_details):
    with create_server_connection() as con:
        sql_script = "INSERT INTO students(student_id, first_name, last_name) VALUES(%s, %s, %s);"
        query(con, sql_script, student_details)


def showing_prereq(course_id):
    with create_server_connection() as con:
        data = (course_id,)

        if course_id != None:
            sql_script = "SELECT course_id, course_prereq_id, min_grade FROM prerequisites WHERE course_id = %s"
            return query(con, sql_script, data=data, fetch=True)
        else:
            sql_script = "SELECT * FROM prerequisites;"
            return query(con, sql_script, fetch=True)


def adding_prereq(prereq_details):
    with create_server_connection() as con:
        sql_script = "INSERT INTO prerequisites(course_id, course_prereq_id, min_grade) VALUES(%s, %s, %s);"
        query(con, sql_script, prereq_details)


def showing_enrolled(student_id):
    with create_server_connection() as con:
        data = (student_id,)

        if student_id != None:
            sql_script = "SELECT student_id, course_id, enrollment_year, grade FROM enrolled WHERE student_id = %s"
            return query(con, sql_script, data=data, fetch=True)
        else:
            sql_script = "SELECT * FROM enrolled;"
            return query(con, sql_script, fetch=True)


def enrolling_student(enrollment_details):
    with create_server_connection() as con:
        sql_script = "INSERT INTO enrolled(student_id, course_id, enrollment_year) VALUES(%s, %s, %s);"
        query(con, sql_script, enrollment_details)


def updating_grade(student_id, course_id, year, grade):
    with create_server_connection() as con:
        sql_script = """
            UPDATE enrolled SET grade = %s WHERE student_id = %s 
            AND course_id = %s 
            AND enrollment_year = %s;
        """
        data = (grade, student_id, course_id, year)

        return query(con, sql_script, data=data)


def showing_transcript(student_id):
    with create_server_connection() as con:
        sql_script = """
            SELECT student_id, first_name, last_name, gpa, calculate_letter_grade(gpa) AS letter_grade
            FROM students WHERE student_id = %s;
            """

        return query(con, sql_script, (student_id, ), fetch=True)
