# 🧠 Smart Attendance System

A modular, secure, and web-based classroom attendance management system built using **Streamlit**, **Supabase**, and **Python**.  
The system provides **role-based access** with dedicated interfaces for **Admins** and **Students**, along with analytics, logging, and GitHub-integrated data exports.

---

## 🚀 Features

### 🔐 Admin Panel
Accessible only with valid admin credentials.

**Class Management**
- Create new classes with default attendance code and daily limit
- Select and manage existing classes
- Update attendance code and daily submission limit
- Toggle attendance status (Open / Close)
- Enforces **only one open class at a time**

**Attendance Analytics**
- Date-wise pivot attendance matrix
- Visual distinction:
  - **P (Present)** – Green
  - **A (Absent)** – Red
- Download attendance matrix as CSV
- Push CSV to GitHub repository with timestamped auto-commits

**Delete Class**
- Permanently removes:
  - Class configuration
  - Attendance records
  - Roll-number mappings
- Requires explicit `"DELETE"` confirmation

---

### 🎓 Student Panel
No login required. Attendance can only be marked when a class is **open**.

**Submit Attendance**
- Select open class
- Enter roll number and name
- Name locks to roll number after first submission
- Enter valid attendance code
- Submission is blocked if:
  - Incorrect code
  - Attendance already marked for the day
  - Daily class limit reached

**View Personal Attendance**
- Displays only the student’s own records
- Structured date-wise table
- Privacy-focused filtered view

---

## 🏗️ Project Structure

```text
Attendence/
│
├── admin.py              → Admin dashboard logic
├── analytics.py          → Attendance analytics
├── clients.py            → Supabase client builder
├── config.py             → Environment/config loader
├── logger.py             → Central logging system
├── student.py            → Student attendance UI + logic
├── supabase_client.py    → (deprecated now, merged into clients)
├── utils.py              → Shared helpers (dates, etc.)
│
├── admin_main.py         → Streamlit entry for admin
├── student_main.py       → Streamlit entry for student
│
├── logs/
│   └── app.log           → Combined logs
│
├── records/              → CSV exports for admin analytics
│
├── pyproject.toml        → Project dependencies
├── requirements.txt      → For pip installs
├── versions.py           → Prints package versions
```


---

## ⚙️ Tech Stack

| Layer         | Technology       |
|--------------|------------------|
| Frontend     | Streamlit        |
| Backend      | Python           |
| Database     | Supabase         |
| Analytics    | Pandas           |
| Visualization| Matplotlib       |
| Storage      | GitHub API (CSV) |
| Logging      | Python Logging   |
| Environment  | uv / venv        |

---

## 🧪 Logging & Observability

The system uses structured logging with:

- Timestamp
- Module and function names
- File and line numbers
- Severity levels (INFO, DEBUG, WARNING, ERROR)

Example log:

```text

2025-12-01 20:15:32,891 | INFO | Attendence.student | student.py:45 | show_student_panel() | Fetching open classes from Supabase…

2025-12-01 20:15:33,104 | DEBUG | Attendence.clients | clients.py:22 | create_supabase_client() | Supabase client initialized successfully.

2025-12-01 20:15:33,982 | ERROR | Attendence.student | student.py:78 | show_student_panel() | Failed to fetch roll map

2025-12-01 20:15:33,982 | ERROR | Attendence.student | student.py:78 | show_student_panel() | Traceback (most recent call last):

2025-12-01 20:15:33,982 | ERROR | Attendence.student | student.py:78 | show_student_panel() |   File "Attendence/student.py", line 65, in show_student_panel

2025-12-01 20:15:33,982 | ERROR | Attendence.student | student.py:78 | show_student_panel() |     roll_map_response = supabase.table("roll_map")...

2025-12-01 20:15:33,982 | ERROR | Attendence.student | student.py:78 | show_student_panel() | postgrest.exceptions.APIError: invalid input syntax for integer: ""

2025-12-01 20:15:34,120 | WARNING | Attendence.admin | admin.py:102 | toggle_classroom() | Classroom '8 C' was already open.

2025-12-01 20:15:34,982 | INFO | Attendence.admin | admin.py:150 | download_attendance_report() | Report generated: attendance_matrix_8C_20251201.csv


```


Logs are stored in `logs/app.log` for debugging and monitoring.

---

## 🛠️ Setup & Installation

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd attendance-system
```

### 2. Create Virtual Environment (uv)
```bash
uv init
uv venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
``` 

### 4. Environment Variables (.env):
```text
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
GITHUB_TOKEN=your_token
```

## ▶️ RUNNING THE APPLICATION:

## Admin Panel:
```bash
streamlit run admin_main.py
```

## Student Panel:
```bash
streamlit run student_main.py   
```



## 🔒 Security Considerations
- Role-based panel separation
- Attendance code validation
- Roll-number locking
- Delete confirmations
- Environment variable secret management

## 📄 License
MIT License

---

## 👩‍💻 Author
**Amrutha Kanakatte  Ravishankar**
