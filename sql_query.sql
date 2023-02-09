DROP DATABASE IF EXISTS railway;
CREATE DATABASE railway;
USE railway;

CREATE TABLE departments(
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    dept_id VARCHAR(255) NOT NULL UNIQUE CHECK (dept_id != ""),
    dept_name VARCHAR(255) NOT NULL CHECK (dept_name != ""),
    dean_name VARCHAR(255),
    building VARCHAR(255),
    room INTEGER
);

CREATE TABLE courses(
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    dept_id VARCHAR(255) NOT NULL,
    course_id VARCHAR(10) NOT NULL UNIQUE CHECK (course_id != ""),
    course_name VARCHAR(255) NOT NULL,  
    hour INTEGER,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        ON UPDATE CASCADE
);

CREATE TABLE students(
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(10) NOT NULL UNIQUE CHECK (student_id != ""),
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    gpa FLOAT NOT NULL DEFAULT 0
);

CREATE TABLE prerequisites(
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    course_id VARCHAR(10) NOT NULL,
    course_prereq_id VARCHAR(10) NOT NULL,
    min_grade INTEGER NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
        ON UPDATE CASCADE,
    CHECK (min_grade >= 0 AND min_grade <= 100)
);

CREATE TABLE enrolled(
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(10) NOT NULL,
    course_id VARCHAR(10) NOT NULL,
    enrollment_year YEAR NOT NULL,
    grade INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON UPDATE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON UPDATE CASCADE,
    UNIQUE (student_id, course_id, enrollment_year),
    CHECK (grade >= 0 AND grade <= 100)
);


/*Creating a trigger and temporary table*/
DROP TRIGGER IF EXISTS before_enrolled_insert;
CREATE TRIGGER before_student_course_insert
    BEFORE INSERT ON enrolled 
    FOR EACH ROW
BEGIN
    /*Create temporary tables to hold 1. prerequisites of courses and 2. unmet_prereqs*/
    DROP TEMPORARY TABLE IF EXISTS tempo_prereqs;
    DROP TEMPORARY TABLE IF EXISTS unmet_prereqs;
    CREATE TEMPORARY TABLE IF NOT EXISTS tempo_prereqs(
        course_prereq VARCHAR(10) REFERENCES courses(course_id),
        min_grade INTEGER
    );

    CREATE TEMPORARY TABLE IF NOT EXISTS unmet_prereqs(
        course_prereq VARCHAR(10) REFERENCES courses(course_id)
    );
    
    /*Does this course have prereqs? If yes, insert them into temp_prereq -> filter out the course*/
    INSERT INTO tempo_prereqs(course_prereq, min_grade)
    SELECT course_prereq_id, min_grade FROM prerequisites WHERE course_id = NEW.course_id;
    /*New course ID we want to insert*/

    /*Are there any unmet prereqs? -> student-specific*/
    INSERT INTO unmet_prereqs(course_prereq)
    SELECT course_prereq
    FROM tempo_prereqs AS tp
    WHERE tp.course_prereq NOT IN
        (SELECT e.course_id FROM enrolled AS e WHERE e.student_id= NEW.student_id AND e.grade > tp.min_grade);

    /*If there are, insert will fail and message the user*/
    IF EXISTS (SELECT course_prereq FROM unmet_prereqs) THEN
        SET @message_text = CONCAT(
            'Student ', NEW.student_id, ' cannot take course ', NEW.course_id, 
            ' because not all the prerequisites are met.'
            );

        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = @message_text;
    END IF;
END;

DROP TRIGGER IF EXISTS after_enrolled_update;
CREATE TRIGGER after_enrolled_update
    AFTER UPDATE ON enrolled 
    FOR EACH ROW
BEGIN
    UPDATE students
    SET gpa = (SELECT AVG(grade) FROM enrolled AS e WHERE e.student_id = NEW.student_id AND e.grade IS NOT NULL)
    WHERE student_id = NEW.student_id;
END;

DROP FUNCTION IF EXISTS calculate_letter_grade;
CREATE FUNCTION calculate_letter_grade(gpa FLOAT)
  RETURNS VARCHAR(10) DETERMINISTIC
  BEGIN
    DECLARE letter_grade VARCHAR(10);

    IF gpa >= 90 THEN SET letter_grade = 'A';
    ELSEIF gpa >= 80 THEN SET letter_grade = 'B';
    ELSEIF gpa >= 70 THEN SET letter_grade = 'C';
    ELSEIF gpa >= 60 THEN SET letter_grade = 'D';
    ELSE SET letter_grade = 'E';
    END IF;
    RETURN letter_grade;
  END;