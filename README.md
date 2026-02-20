# EventIQ

EventIQ is a web-based event management platform built to organize, host, and participate in technical events such as hackathons, bootcamps, workshops, and meetups.  
The system supports role-based access for **users** and **hosts**, enabling smooth event creation, participation, and tracking.

---

## Features

### User
- Signup and login
- Browse events by category
- Register for events
- View attended events in profile
- See attendance count by event type

### Host
- Host account management
- Create and manage events
- Host company logo used as event banner
- View events created by the host
- View participant list for each event
- See count of events created by category

---

## Event Categories
- Hackathon  
- Bootcamp  
- Workshop  
- Meetup  

---

## Tech Stack

- Backend: Flask (Python)
- Frontend: HTML, CSS, Bootstrap, Jinja2
- Database: SQLite
- ORM: Flask-SQLAlchemy
- Authentication: Session-based
- Security: Werkzeug / bcrypt

---

## Project Structure

```commandline
EventIQ/
│
├── backend/
│ ├── main.py
│ ├── routes.py
│ ├── models.py
│ └── requirements.txt
│
├── frontend/
│ ├── templates/
│ └── static/
│
└── README.md
```



---

## Setup Instructions

1. Clone the repository
```bash
git clone <repository-url>
cd EventIQ
```

2. remove old venv file

3. Create and activate virtual environment remove old venv file
```bash
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
```

4. Install dependencies
```commandline
pip install -r requirements.txt
```
5. Run the application
```commandline
python backend/main.py
```
6. open in browser
```commandline
http://127.0.0.1:5000
```

