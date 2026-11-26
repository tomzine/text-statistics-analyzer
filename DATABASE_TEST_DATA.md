# School Management API — Example Database

This document describes the **fictional testing data** created by `seed_demo_data.py` for the FastAPI + SQLAlchemy school management project.

> **Important:** These are the **expected records after the seed script runs successfully**, not a report of the database's current contents. The seed script **replaces existing application records**. Back up `students.db` before running it. Never use this reset script against production data.

## 1. Database tables

| Table | Purpose | Expected rows after seeding |
| --- | --- | ---: |
| `school_classes` | School class names | 3 |
| `courses` | Available courses | 5 |
| `students` | Student profiles | 9 |
| `student_courses` | Student–course enrollments | 18 |
| `users` | Authentication accounts | 2 |
| `alembic_version` | Applied migration revision | Preserved; not reset |

Primary keys are assigned by SQLite. **Do not assume that IDs will always start at 1** or hardcode them when testing relationships.

## 2. School classes

| Class name | Description | Students |
| --- | --- | ---: |
| `TCS` | Tronc Commun Scientifique | 3 |
| `1Bac` | First year of Baccalaureate | 3 |
| `2Bac` | Second year of Baccalaureate | 3 |

## 3. Courses

| Course name | Enrolled students |
| --- | ---: |
| Mathematics | 6 |
| Physics and Chemistry | 5 |
| Computer Science | 2 |
| French | 2 |
| English | 3 |

## 4. Students and course enrollments

All names and emails below are fictional. The reserved `.test` domain is used to prevent confusion with real email accounts.

| Name | Age | Grade | School class | Email | Courses |
| --- | ---: | --- | --- | --- | --- |
| Ahmed Alaoui | 15 | TCS | TCS | ahmed.alaoui@example.test | Mathematics; Computer Science |
| Sara Bennani | 16 | TCS | TCS | sara.bennani@example.test | Mathematics; French |
| Adam Amrani | 15 | TCS | TCS | adam.amrani@example.test | Physics and Chemistry; English |
| Youssef Idrissi | 17 | 1Bac | 1Bac | youssef.idrissi@example.test | Mathematics; Physics and Chemistry |
| Fatima Tazi | 16 | 1Bac | 1Bac | fatima.tazi@example.test | Mathematics; French |
| Lina Berrada | 17 | 1Bac | 1Bac | lina.berrada@example.test | Physics and Chemistry; English |
| Omar Fassi | 18 | 2Bac | 2Bac | omar.fassi@example.test | Mathematics; Physics and Chemistry |
| Salma El Amrani | 17 | 2Bac | 2Bac | salma.elamrani@example.test | Mathematics; Computer Science |
| Hamza Benali | 18 | 2Bac | 2Bac | hamza.benali@example.test | Physics and Chemistry; English |

Each student belongs to **one** school class and is enrolled in **two** courses. This exercises both the one-to-many and many-to-many relationships.

## 5. Authentication accounts

| Login email | Role | Active | Password |
| --- | --- | --- | --- |
| `admin@example.test` | `admin` | Yes | 1234567890 |
| `teacher@example.test` | `teacher` | Yes | 123456789 |

- Passwords are **hashed**, never stored as plaintext in the database.
- There are **no default passwords** in this document or in the seed script.
- Public registration must never allow a caller to assign themselves the `admin` role.
- **Rotate your JWT `SECRET_KEY` after resetting the users.** Tokens contain user IDs (`sub`), and SQLite may reuse IDs after a full reset. Without rotating the key, an old valid token could accidentally match a newly created account, potentially with a different role. After rotating the key, restart the API and sign in again.
- The JWT `SECRET_KEY` is stored separately in your local environment; **never commit `.env`**.

## 6. Safely resetting and seeding

From the project root, with the FastAPI server stopped:

```powershell
uv run alembic current
uv run python seed_demo_data.py
```

The reset script should:

1. Check that the intended SQLite database and tables exist.
2. Require the explicit confirmation `RESET`.
3. Ask you to choose two passwords without displaying them.
4. Create a timestamped backup **outside the Git repository**.
5. Delete application rows in foreign-key-safe order: `student_courses`, `students`, `courses`, `school_classes`, `users`.
6. Insert all classes, courses, students, enrollments, and test users **within one transaction**.
7. Commit if everything succeeds or roll back if any operation fails.

After a successful user reset, **generate a new JWT secret locally**, replace the value in your untracked `.env` file, and restart FastAPI. Do not share or commit the secret. This invalidates tokens issued before the reset.

**Do not delete tables, drop the database, or clear `alembic_version`.** The existing migration schema should remain intact.

## 7. Verify the data

Expected summary after seeding:

```text
Classes: 3
Courses: 5
Students: 9
Enrollments: 18
Users: 2
```

Optional read-only SQLite queries:

```sql
SELECT COUNT(*) FROM school_classes;
SELECT COUNT(*) FROM courses;
SELECT COUNT(*) FROM students;
SELECT COUNT(*) FROM student_courses;
SELECT COUNT(*) FROM users;

SELECT s.name AS student, sc.name AS school_class
FROM students AS s
LEFT JOIN school_classes AS sc ON sc.id = s.school_class_id
ORDER BY sc.name, s.name;

SELECT s.name AS student, c.name AS course
FROM student_courses AS enrollment
JOIN students AS s ON s.id = enrollment.student_id
JOIN courses AS c ON c.id = enrollment.course_id
ORDER BY s.name, c.name;
```

## 8. API testing checklist

Start FastAPI with the local JWT secret loaded:

```powershell
uv run --env-file .env fastapi dev api_server.py
```

Open `http://127.0.0.1:8000/docs`.

| Scenario | Expected result |
| --- | --- |
| `POST /auth/login` with teacher credentials | Successful login with a Bearer token |
| `POST /auth/login` with admin credentials | Successful login with a Bearer token |
| `GET /auth/me` with a valid token | Authenticated user profile |
| `GET /students` without a token | `401 Unauthorized` |
| `GET /students` with a valid token | `200 OK`; nine students, if no records have been changed |
| `DELETE /students/{student_id}` without a token | `401 Unauthorized` |
| `DELETE /students/{student_id}` with a teacher token | `403 Forbidden`; no deletion |
| `DELETE /students/{student_id}` with an admin token and a nonexistent ID | `404 Not Found`; no deletion |
| `DELETE /students/{student_id}` with an admin token and a **disposable** student | Successful deletion |

To test successful deletion, first create a **disposable** student. Avoid deleting one of the nine seeded students if you want to retain a predictable dataset for later lessons.

## 9. Future project exercises

- Filter students by `age`, `grade`, or class.
- Search student names with `ilike()`.
- Paginate and sort the student list.
- Join students with `school_classes` and `courses`.
- Compare `joinedload()` with `selectinload()`.
- Test teacher versus admin authorization.
- Add automated endpoint tests using `pytest` and FastAPI's test client.