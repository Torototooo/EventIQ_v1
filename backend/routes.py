from flask import jsonify,request, render_template, redirect, url_for, session, flash
from datetime import datetime
from main import app
from models import db, Host,Event,User,EventParticipation,Review,UserPreference,WebsiteReview
from werkzeug.utils import secure_filename
from functools import wraps
import os
import matplotlib.pyplot as plt
import io
import base64
from collections import Counter
from flask_mail import Message
from main import mail
from authlib.integrations.flask_client import OAuth
from main import app,google



def send_welcome_email(user):
    msg = Message(
        subject="Welcome to EventIQ",
        recipients=[user.email]
    )

    msg.body = f"""
Hi {user.full_name},

Welcome to EventIQ!

You can now explore Hackathons, Bootcamps, Workshops, and Meetups.

Stay tuned for exciting tech events.

Best Regards,
Team EventIQ
"""

    mail.send(msg)



print("ROUTES.PY LOADED")
print("ROUTES.PY END")

@app.route("/hosts")
def show_hosts():
    hosts = Host.query.all()   # READ from DB
    return render_template("hosts.html", hosts=hosts)

@app.route("/add-host", methods=["GET", "POST"])
def add_host():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        host = Host(name=name, email=email, password=password)
        db.session.add(host)
        db.session.commit()

        return redirect(url_for("show_hosts"))

    return render_template("add_host.html")

@app.route("/edit-host/<int:id>", methods=["GET", "POST"])
def edit_host(id):
    host = Host.query.get_or_404(id)

    if request.method == "POST":
        host.name = request.form["name"]
        host.email = request.form["email"]
        host.password = request.form["password"]

        db.session.commit()
        return redirect(url_for("show_hosts"))

    return render_template("edit_host.html", host=host)

@app.route("/delete-host/<int:id>")
def delete_host(id):
    host = Host.query.get_or_404(id)
    db.session.delete(host)
    db.session.commit()
    return redirect(url_for("show_hosts"))


@app.route("/")
def index():
    hosts = Host.query.all()
    users= User.query.all()
    events = Event.query.all()
    host_count=len(hosts)
    event_count=len(events)
    user_count=len(users)

    reviews = (
        WebsiteReview.query
        .order_by(WebsiteReview.created_at.desc())
        .limit(3)
        .all()
    )

    return render_template("index.html", reviews=reviews,host_count=host_count,event_count=event_count,user_count=user_count)



@app.route("/hackathon")
def hackathon():
    hosts = Host.query.all()
    users = User.query.all()
    events = Event.query.all()
    host_count = len(hosts)
    event_count = len(events)
    user_count = len(users)
    return render_template("hackathon.html",event_count=event_count,user_count=user_count)




@app.route("/bootcamp")
def bootcamp():
    return render_template("bootcamp.html")

@app.route("/meetup")
def meetup():
    return render_template("meetup.html")




@app.route("/contact")
def contact():
    return render_template("contact-preferences.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()

            session["user_id"] = user.id
            session["role"] = "user"
            session["name"] = user.full_name

            flash("Login successful!", "success")
            return redirect("/")

        host = Host.query.filter_by(email=email).first()
        if host and host.check_password(password):
            host.last_login = datetime.utcnow()
            db.session.commit()

            session["host_id"] = host.id
            session["role"] = "host"
            session["name"] = host.full_name

            flash("Login successful!", "success")
            return redirect("/")


        flash("Invalid email or password", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/dashboard")
def user_dashboard():
    return "User Dashboard (login successful)"


@app.route("/host/dashboard")
def host_dashboard():
    return "Host Dashboard (login successful)"


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("login"))


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        # Common fields
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        is_host = request.form.get("is_host")


        if User.query.filter_by(email=email).first() or Host.query.filter_by(email=email).first():
            flash("Email already registered", "danger")
            return redirect(url_for("signup"))


        if is_host:

            logo_filename = None
            logo_file = request.files.get("company_logo")

            if logo_file and allowed_file(logo_file.filename):
                filename = secure_filename(logo_file.filename)
                logo_filename = f"{int(datetime.utcnow().timestamp())}_{filename}"
                logo_path = os.path.join(app.config["UPLOAD_FOLDER"], logo_filename)
                logo_file.save(logo_path)

            host = Host(
                full_name=full_name,
                email=email,
                company_name=request.form.get("company_name"),
                company_logo=logo_filename,
                website=request.form.get("website"),
                city=request.form.get("city"),
                state=request.form.get("state"),
                created_at=datetime.utcnow(),
                last_login=None
            )

            host.set_password(password)

            db.session.add(host)
            db.session.commit()



            flash("Host account created successfully. Please login.", "success")
            return redirect(url_for("login"))

        skills_list = request.form.getlist("skills")
        skills_str = ",".join(skills_list)

        user = User(
            full_name=full_name,
            email=email,
            description=request.form.get("description"),
            college=request.form.get("college"),
            course=request.form.get("course"),
            year=request.form.get("year"),
            skills=skills_str,
            created_at=datetime.utcnow(),
            last_login=None
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        send_welcome_email(user)

        flash("Account created successfully. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")





@app.route("/api/hackathons", methods=["GET"])
def get_hackathons():

    update_event_status()


    search = request.args.get("search")
    status = request.args.get("status")
    city = request.args.get("city")
    skill = request.args.get("skill")
    skill_level = request.args.get("skill_level")


    query = Event.query.filter(Event.type_of_event == "hackathon")

    if search:
        query = query.filter(Event.title.ilike(f"%{search}%"))

    if status:
        query = query.filter(Event.status == status)

    if city:
        query = query.filter(
            (Event.city == city) | (Event.location == city)
        )

    if skill_level:
        query = query.filter(Event.skill_level == skill_level)

    hackathons = query.order_by(Event.created_at.desc()).all()

    # Skill (CSV match)
    if skill:
        hackathons = [
            h for h in hackathons
            if skill.lower() in [s.strip().lower() for s in h.skills.split(",")]
        ]

    return jsonify([
        {
            "id": h.id,
            "title": h.title,
            "description": h.description,
            "start_date": h.start_date.isoformat(),
            "end_date": h.end_date.isoformat(),
            "location": h.location,
            "city": h.city,
            "state": h.state,
            "mode": h.mode,
            "status": h.status,
            "skills": h.skills,
            "skill_level": h.skill_level,
            "max_participants": h.max_participants,
            "banner_image": h.banner_image
        }
        for h in hackathons
    ])



@app.route("/api/hackathons/latest")
def latest_hackathons():
    update_event_status()
    hackathons = (
        Event.query
        .filter(Event.type_of_event == "hackathon",Event.end_date >= date.today())
        .order_by(Event.created_at.desc())
        .limit(3)
        .all()
    )

    return jsonify([
        {
            "id": h.id,
            "title": h.title,
            "description": h.description,

            "start_date": h.start_date.isoformat(),
            "end_date": h.end_date.isoformat(),

            "mode": h.mode,
            "city": h.city,
            "location": h.location,

            # 💰 IMPORTANT
            "registration_fee": h.registration_fee,

            # optional UI info
            "skill_level": h.skill_level,
            "banner_image": h.banner_image,

            "attending": h.attending
        }
        for h in hackathons
    ])

@app.route("/api/workshops/latest")
def latest_workshops():
    update_event_status()
    workshops = (
        Event.query
        .filter(Event.type_of_event == "workshop",Event.end_date >= date.today())
        .order_by(Event.created_at.desc())
        .limit(3)
        .all()
    )

    return jsonify([
        {
            "id": w.id,
            "title": w.title,
            "description": w.description,

            "start_time": w.start_time.isoformat() if w.start_time else None,
            "end_time": w.end_time.isoformat() if w.end_time else None,

            "registration_fee": w.registration_fee,

            "skill_level": w.skill_level,
            "host_name": w.host.company_name if w.host else "EventIQ",

            "attending": w.attending,
        }
        for w in workshops
    ])



@app.route("/api/meetups/latest")
def latest_meetups():
    update_event_status()
    meetups = (
        Event.query
        .filter(Event.type_of_event == "meetup",Event.end_date >= date.today())
        .order_by(Event.created_at.desc())
        .limit(2)   # 2 or 4 depending on your layout
        .all()
    )

    return jsonify([
        {
            "id": m.id,
            "title": m.title,
            "description": m.description,

            "start_date": m.start_date.isoformat(),
            "start_time": m.start_time.isoformat() if m.start_time else None,
            "end_time": m.end_time.isoformat() if m.end_time else None,

            "mode": m.mode,
            "city": m.city,
            "location": m.location,

            "attending": m.attending
        }
        for m in meetups
    ])




def host_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "host":
            flash("Host access required", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/host-event")
@host_required
def host_event():
    return render_template("host-event.html")




@app.route("/host-event", methods=["POST"])
@host_required
def create_event():
    host_id = session.get("host_id")


    def parse_date(value):
        return datetime.strptime(value, "%Y-%m-%d").date() if value else None

    title = request.form.get("title")
    description = request.form.get("description")
    event_type = request.form.get("event_type")
    start_raw = request.form.get("start_datetime")
    end_raw = request.form.get("end_datetime")
    mode = request.form.get("format")

    if not all([title, description, event_type, start_raw, end_raw, mode]):
        flash("Please fill all required fields (including event format)", "danger")
        return redirect(url_for("host_event"))


    start_dt = datetime.fromisoformat(start_raw)
    end_dt = datetime.fromisoformat(end_raw)


    skills_list = request.form.getlist("skills")
    skills = ", ".join(skills_list)


    registration_fee = int(request.form.get("registration_fee", 0))

    first_prize = request.form.get("first_prize")
    second_prize = request.form.get("second_prize")
    third_prize = request.form.get("third_prize")
    other_rewards = request.form.get("other_rewards")


    platform = request.form.get("platform")

    submission_start_date = parse_date(request.form.get("submission_start_date"))
    submission_end_date = parse_date(request.form.get("submission_end_date"))
    judging_start_date = parse_date(request.form.get("judging_start_date"))
    judging_end_date = parse_date(request.form.get("judging_end_date"))
    winner_announcement_date = parse_date(request.form.get("winner_announcement_date"))


    location = request.form.get("location")
    city = request.form.get("city")
    state = request.form.get("state")

    if mode == "online":
        location = "Online"
        city = None
        state = None

    host = Host.query.get(host_id)

    if not host:
        flash("Host not found", "danger")
        return redirect(url_for("host_event"))


    event = Event(
        title=title,
        description=description,
        type_of_event=event_type,

        start_date=start_dt.date(),
        end_date=end_dt.date(),
        start_time=start_dt.time(),
        end_time=end_dt.time(),

        submission_start_date=submission_start_date,
        submission_end_date=submission_end_date,
        judging_start_date=judging_start_date,
        judging_end_date=judging_end_date,
        winner_announcement_date=winner_announcement_date,

        mode=mode,
        platform=platform,
        location=location,
        city=city,
        state=state,

        status="upcoming",

        skills=skills,
        skill_level=request.form.get("skill_level", "any"),

        max_participants=(
            int(request.form.get("max_participants"))
            if request.form.get("max_participants")
            else None
        ),

        registration_fee=registration_fee,
        first_prize=int(first_prize) if first_prize else None,
        second_prize=int(second_prize) if second_prize else None,
        third_prize=int(third_prize) if third_prize else None,
        other_rewards=other_rewards,

        host_id=host_id,
        banner_image=host.company_logo,
    )

    db.session.add(event)
    db.session.commit()

    notify_users_about_event(event)

    flash("Event created successfully!", "success")
    return redirect(url_for("host_event"))


@app.route("/workshop")
def workshop():
    return render_template("workshop.html")


@app.route("/api/workshops", methods=["GET"])
def get_workshops():
    search = request.args.get("search")
    status = request.args.get("status")
    city = request.args.get("city")
    skill = request.args.get("skill")
    skill_level = request.args.get("skill_level")

    update_event_status()

    query = Event.query.filter(Event.type_of_event == "workshop")

    if search:
        query = query.filter(Event.title.ilike(f"%{search}%"))

    if status:
        query = query.filter(Event.status == status)

    if city:
        query = query.filter(
            (Event.city == city) | (Event.location == city)
        )

    if skill_level:
        query = query.filter(Event.skill_level == skill_level)

    workshops = query.order_by(Event.created_at.desc()).all()

    if skill:
        workshops = [
            w for w in workshops
            if skill.lower() in [s.strip().lower() for s in w.skills.split(",")]
        ]

    return jsonify([
        {
            "id": w.id,
            "title": w.title,
            "description": w.description,
            "start_date": w.start_date.isoformat(),
            "end_date": w.end_date.isoformat(),
            "start_time": w.start_time.isoformat() if w.start_time else None,
            "end_time": w.end_time.isoformat() if w.end_time else None,
            "location": w.location,
            "city": w.city,
            "state": w.state,
            "mode": w.mode,
            "status": w.status,
            "skills": w.skills,
            "skill_level": w.skill_level,
            "max_participants": w.max_participants,
            "registration_fee": w.registration_fee or 0,
            "banner_image": w.banner_image
        }
        for w in workshops
    ])


@app.route("/api/meetups", methods=["GET"])
def get_meetups():
    search = request.args.get("search")
    city = request.args.get("city")
    topic = request.args.get("topic")

    update_event_status()

    query = Event.query.filter(Event.type_of_event == "meetup")

    if search:
        query = query.filter(Event.title.ilike(f"%{search}%"))

    if city:
        query = query.filter(
            (Event.city == city) | (Event.location == city)
        )

    meetups = query.order_by(Event.created_at.desc()).all()

    # topic filter (skills-based)
    if topic:
        meetups = [
            m for m in meetups
            if m.skills and topic.lower() in
            [s.strip().lower() for s in m.skills.split(",")]
        ]

    return jsonify([
        {
            "id": m.id,
            "title": m.title,
            "description": m.description,

            "start_date": m.start_date.isoformat(),
            "start_time": m.start_time.isoformat() if m.start_time else None,
            "end_time": m.end_time.isoformat() if m.end_time else None,

            "mode": m.mode,
            "city": m.city,
            "location": m.location,

            "skills": m.skills,
            "attending": m.attending
        }
        for m in meetups
    ])


@app.route("/api/bootcamps", methods=["GET"])
def get_bootcamps():
    update_event_status()

    bootcamps = (
        Event.query
        .filter(Event.type_of_event == "bootcamp")
        .order_by(Event.created_at.desc())
        .all()
    )

    result = []

    for b in bootcamps:
        duration_days = None
        if b.start_date and b.end_date:
            duration_days = (b.end_date - b.start_date).days

        result.append({
            "id": b.id,
            "title": b.title,
            "description": b.description,

            "registration_fee": b.registration_fee or 0,

            "duration_days": duration_days,

            "skills": b.skills or "",

            "instructor": (
                b.host.company_name
                if hasattr(b, "host") and b.host
                else "EventIQ"
            )
        })

    return jsonify(result)

@app.route("/api/bootcamps/latest")
def latest_bootcamps():
    update_event_status()
    bootcamps = (
        Event.query
        .filter(Event.type_of_event == "bootcamp",Event.end_date >= date.today())
        .order_by(Event.created_at.desc())
        .limit(3)
        .all()
    )



    result = []

    for b in bootcamps:
        duration_days = None
        if b.start_date and b.end_date:
            duration_days = (b.end_date - b.start_date).days

        result.append({
            "id": b.id,
            "title": b.title,
            "description": b.description,

            "registration_fee": b.registration_fee or 0,

            "duration_days": duration_days,

            "instructor": (
                b.host.company_name
                if hasattr(b, "host") and b.host
                else "EventIQ"
            )
        })

    return jsonify(result)



@app.route("/event/<event_type>/<int:event_id>")
def event_detail(event_type, event_id):
    update_event_status()

    event = Event.query.filter_by(
        id=event_id,
        type_of_event=event_type,
    ).first_or_404()

    if event.status == "completed":
        flash("This event has already ended.", "info")
        return redirect(url_for("index"))

    rendering_template=""
    if event_type=="hackathon":
        rendering_template = "hackathon_details.html"
    elif event_type=="meetup":
        rendering_template = "meetup_details.html"
    elif event_type=="workshop":
        rendering_template = "workshop_details.html"
    elif event_type=="bootcamp":
        rendering_template = "bootcamp_details.html"

    already_registered = False
    user_id = session.get("user_id")
    if user_id:
        for p in event.participants:
            if p.user_id == user_id:
                already_registered = True
                break

    # 🔥 Calculate average rating
    reviews = event.reviews

    total_reviews = len(reviews)

    if total_reviews > 0:
        total_rating = sum(review.rating for review in reviews)
        avg_rating = round(total_rating / total_reviews, 1)
    else:
        avg_rating = 0

    return render_template(
        rendering_template,
        event=event,
        already_registered=already_registered,
        avg_rating=avg_rating,
    )

@app.route("/profile")
def profile():
    role = session.get("role")
    user_id = session.get("user_id")
    host_id = session.get("host_id")

    if not role:
        flash("Please login first", "warning")
        return redirect(url_for("login"))


    if role == "user":
        user = User.query.get_or_404(user_id)

        participations = EventParticipation.query.filter_by(
            user_id=user_id
        ).all()

        list_hackathon = []
        list_bootcamp = []
        list_meetup = []
        list_workshop = []

        for p in participations:
            event = Event.query.get(p.event_id)
            if not event:
                continue

            if p.event_type == "hackathon":
                list_hackathon.append(event)
            elif p.event_type == "bootcamp":
                list_bootcamp.append(event)
            elif p.event_type == "meetup":
                list_meetup.append(event)
            elif p.event_type == "workshop":
                list_workshop.append(event)

        return render_template(
            "profile.html",
            user=user,

            list_hackathon=list_hackathon,
            list_bootcamp=list_bootcamp,
            list_meetup=list_meetup,
            list_workshop=list_workshop,

            hackathon_attended=len(list_hackathon),
            bootcamp_attended=len(list_bootcamp),
            meetup_attended=len(list_meetup),
            workshop_attended=len(list_workshop),
        )


    elif role == "host":
        host = Host.query.get_or_404(host_id)

        events = Event.query.filter_by(
            host_id=host_id
        ).all()

        list_hackathon = []
        list_bootcamp = []
        list_meetup = []
        list_workshop = []

        for event in events:
            if event.type_of_event == "hackathon":
                list_hackathon.append(event)
            elif event.type_of_event == "bootcamp":
                list_bootcamp.append(event)
            elif event.type_of_event == "meetup":
                list_meetup.append(event)
            elif event.type_of_event == "workshop":
                list_workshop.append(event)

        total_events_created = (
            len(list_hackathon)
            + len(list_bootcamp)
            + len(list_meetup)
            + len(list_workshop)
        )

        # Generate analytics charts
        analytics_charts = generate_host_analytics(host_id)

        return render_template(
            "profile_host.html",
            host=host,

            list_hackathon=list_hackathon,
            list_bootcamp=list_bootcamp,
            list_meetup=list_meetup,
            list_workshop=list_workshop,

            hackathon_created=len(list_hackathon),
            bootcamp_created=len(list_bootcamp),
            meetup_created=len(list_meetup),
            workshop_created=len(list_workshop),
            total_events_created=total_events_created,

            analytics_charts=analytics_charts
        )



@app.route("/event/<int:event_id>/participate", methods=["POST"])
def participate_event(event_id):


    user_id = session.get("user_id")
    role = session.get("role")

    if not user_id:
        flash("Please login to participate", "warning")
        return redirect(url_for("login"))

    if role != "user":
        flash("Only users can participate in events", "danger")
        return redirect(request.referrer)


    event = Event.query.get_or_404(event_id)


    existing = EventParticipation.query.filter_by(
        user_id=user_id,
        event_id=event.id
    ).first()

    if existing:
        flash("You are already registered for this event", "info")
        return redirect(request.referrer)

    if event.max_participants:
        if event.attending is None:
            event.attending = 0

        if event.attending >= event.max_participants:
            flash("Event is full", "danger")
            return redirect(request.referrer)


    participation = EventParticipation(
        user_id=user_id,
        event_id=event.id,
        event_type=event.type_of_event
    )

    db.session.add(participation)


    event.attending = (event.attending or 0) + 1

    db.session.commit()

    flash("Successfully registered 🎉", "success")
    return redirect(request.referrer)

@app.route("/host/event/<int:event_id>")
@host_required
def host_event_detail(event_id):
    host_id = session.get("host_id")


    event = Event.query.filter_by(
        id=event_id,
        host_id=host_id
    ).first_or_404()


    participations = EventParticipation.query.filter_by(
        event_id=event.id
    ).all()


    participants = []

    reviews = event.reviews

    total_reviews = len(reviews)

    if total_reviews > 0:
        total_rating = sum(review.rating for review in reviews)
        avg_rating = round(total_rating / total_reviews, 1)
    else:
        avg_rating = 0

    for p in participations:
        user = User.query.get(p.user_id)
        if user:
            participants.append(user)

    return render_template(
        "host_event_detail.html",
        event=event,
        participants=participants,
        avg_rating=avg_rating
    )


@app.route("/event/<int:event_id>/review", methods=["POST"])
def submit_review(event_id):

    if session.get("role") != "user":
        flash("Only logged in users can submit reviews.", "danger")
        return redirect(url_for("login"))

    user_id = session.get("user_id")

    event = Event.query.get_or_404(event_id)

    # Prevent duplicate review
    existing_review = Review.query.filter_by(
        user_id=user_id,
        event_id=event_id
    ).first()

    if existing_review:
        flash("You have already reviewed this event.", "warning")
        return redirect(url_for(
            "event_detail",
            event_type=event.type_of_event,
            event_id=event.id
        ))

    rating = request.form.get("rating")
    review_text = request.form.get("review_text")

    review = Review(
        rating=int(rating),
        review_text=review_text,
        user_id=user_id,
        event_id=event_id
    )

    db.session.add(review)
    db.session.commit()

    flash("Review submitted successfully.", "success")

    return redirect(url_for(
        "event_detail",
        event_type=event.type_of_event,
        event_id=event.id
    ))

@app.route("/event/<event_type>/<int:event_id>/reviews")
def review_page(event_type, event_id):

    event = Event.query.filter_by(
        id=event_id,
        type_of_event=event_type
    ).first_or_404()

    # 🔥 If host tries to access review form
    if session.get("role") == "host":
        flash("Hosts cannot submit reviews.", "warning")
        return redirect(url_for(
            "event_detail",
            event_type=event.type_of_event,
            event_id=event.id
        ))

    # 🔥 If not logged in
    if session.get("role") != "user":
        flash("Please login to submit a review.", "warning")
        return redirect(url_for("login"))

    user_id = session.get("user_id")

    # 🔥 If user already reviewed → redirect to review list
    existing_review = Review.query.filter_by(
        user_id=user_id,
        event_id=event_id
    ).first()

    if existing_review:
        flash("You have already submitted a review.", "info")
        return redirect(url_for(
            "reviews_list",
            event_type=event.type_of_event,
            event_id=event.id
        ))

    return render_template(
        "reviews.html",
        event=event
    )

@app.route("/event/<event_type>/<int:event_id>/reviews/list")
def reviews_list(event_type, event_id):

    event = Event.query.filter_by(
        id=event_id,
        type_of_event=event_type
    ).first_or_404()

    reviews = event.reviews

    return render_template(
        "reviews_list.html",
        event=event,
        reviews=reviews
    )


def generate_host_analytics(host_id):
    """Generate analytics charts for host events"""
    events = Event.query.filter_by(host_id=host_id).all()

    if not events:
        return None

    # Create a single figure with 3 subplots
    fig = plt.figure(figsize=(16, 5))

    # 1. Event Type Distribution (Pie Chart) - Left
    ax1 = plt.subplot(1, 3, 1)
    event_types = [e.type_of_event for e in events]
    type_counts = Counter(event_types)

    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
    ax1.pie(type_counts.values(), labels=type_counts.keys(), autopct='%1.1f%%',
            startangle=90, colors=colors)
    ax1.set_title('Event Type Distribution', fontsize=14, fontweight='bold')

    # 2. Total Participants by Event Type (Bar Chart) - Middle
    ax2 = plt.subplot(1, 3, 2)
    type_participants = {}
    for event in events:
        event_type = event.type_of_event
        if event_type not in type_participants:
            type_participants[event_type] = 0
        type_participants[event_type] += (event.attending or 0)

    types = list(type_participants.keys())
    participants = list(type_participants.values())

    bars = ax2.bar(types, participants, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'])
    ax2.set_ylabel('Total Participants', fontsize=12)
    ax2.set_title('Total Participants by Event Type', fontsize=14, fontweight='bold')

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2., height,
                 f'{int(height)}', ha='center', va='bottom')

    # 3. Events Timeline (Line Chart) - Right
    ax3 = plt.subplot(1, 3, 3)
    events_by_month = {}
    for event in events:
        month_key = event.start_date.strftime('%Y-%m')
        events_by_month[month_key] = events_by_month.get(month_key, 0) + 1

    sorted_months = sorted(events_by_month.keys())
    month_counts = [events_by_month[m] for m in sorted_months]

    ax3.plot(range(len(sorted_months)), month_counts, marker='o',
             linewidth=2, markersize=8, color='#FF6B6B')
    ax3.set_xlabel('Month', fontsize=12)
    ax3.set_ylabel('Number of Events', fontsize=12)
    ax3.set_title('Events Timeline', fontsize=14, fontweight='bold')
    ax3.set_xticks(range(len(sorted_months)))
    ax3.set_xticklabels(sorted_months, rotation=45, ha='right')
    ax3.grid(True, alpha=0.3)

    # Adjust layout to prevent overlap
    plt.tight_layout()

    # Convert to base64
    analytics_chart = fig_to_base64(fig)
    plt.close(fig)

    return {'combined_chart': analytics_chart}


def fig_to_base64(fig):
    """Convert matplotlib figure to base64 string"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return img_base64

@app.route("/preferences", methods=["GET"])
def preferences_page():

    if session.get("role") != "user":
        flash("Please login as user to set preferences.", "warning")
        return redirect(url_for("login"))

    return render_template("contact-preferences.html")


@app.route("/preferences", methods=["POST"])
def save_preferences():

    if session.get("role") != "user":
        flash("Only users can set preferences.", "danger")
        return redirect(url_for("login"))

    user_id = session.get("user_id")

    event_types = request.form.getlist("event_types")
    skills = request.form.getlist("skills")
    frequency = request.form.get("frequency")

    event_types_str = ",".join(event_types)
    skills_str = ",".join(skills)

    existing_pref = UserPreference.query.filter_by(user_id=user_id).first()

    if existing_pref:
        existing_pref.event_types = event_types_str
        existing_pref.skills = skills_str
        existing_pref.frequency = frequency
    else:
        new_pref = UserPreference(
            user_id=user_id,
            event_types=event_types_str,
            skills=skills_str,
            frequency=frequency
        )
        db.session.add(new_pref)

    db.session.commit()

    flash("Preferences saved successfully!", "success")
    return redirect(url_for("profile"))

def notify_users_about_event(event):

    from flask_mail import Message

    preferences = UserPreference.query.all()

    for pref in preferences:

        user = pref.user

        if not user:
            continue

        # 🔥 Only send if user selected DAILY
        if pref.frequency != "daily":
            continue

        # Match event type
        if pref.event_types:
            preferred_types = pref.event_types.split(",")

            if "all" not in preferred_types and event.type_of_event not in preferred_types:
                continue

        # Match skills
        if pref.skills and event.skills:
            preferred_skills = pref.skills.split(",")
            event_skills = event.skills.split(",")

            if not any(skill.strip() in preferred_skills for skill in event_skills):
                continue

        msg = Message(
            subject=f"New {event.type_of_event.title()} Just Posted 🚀",
            recipients=[user.email]
        )

        msg.body = f"""
Hi {user.full_name},

A new {event.type_of_event} matching your interests has just been posted!

Title: {event.title}
Skills: {event.skills}
Start Date: {event.start_date}

Visit EventIQ now to explore.

Best,
Team EventIQ
"""

        mail.send(msg)

@app.route("/review-us")
def review_us():

    user_id = session.get("user_id")

    if not user_id:
        flash("Please login to give review", "warning")
        return redirect(url_for("login"))

    return render_template("website_review.html")

@app.route("/submit-web-review", methods=["POST"])
def submit_web_review():

    user_id = session.get("user_id")

    if not user_id:
        flash("Please login first", "warning")
        return redirect(url_for("login"))

    # 🔥 Using EXACT form names
    rating = int(request.form.get("rating"))
    review_text = request.form.get("review_text")

    # Save to DB
    review = WebsiteReview(
        user_id=user_id,
        rating=rating,
        comment=review_text
    )

    existing = WebsiteReview.query.filter_by(user_id=user_id).first()

    if existing:
        flash("You already submitted a review", "info")
        return redirect(url_for("index"))

    db.session.add(review)
    db.session.commit()

    flash("Thank you for your review! ⭐", "success")
    return redirect(url_for("index"))

import secrets

@app.route("/login/google")
def google_login():

    nonce = secrets.token_urlsafe(16)
    session["google_nonce"] = nonce

    redirect_uri = url_for("google_callback", _external=True)
    return google.authorize_redirect(
        redirect_uri,
        nonce=nonce
    )


@app.route("/google/callback")
def google_callback():

    token = google.authorize_access_token()
    nonce = session.get("google_nonce")
    user_info = google.parse_id_token(token, nonce=nonce)

    email = user_info.get("email")
    name = user_info.get("name")

    if not email:
        flash("Google login failed.", "danger")
        return redirect(url_for("login"))

    # Check if already registered as user
    user = User.query.filter_by(email=email).first()

    if user:
        # Login existing user
        session["user_id"] = user.id
        session["role"] = "user"
        session["name"] = user.full_name

        flash("Logged in successfully with Google!", "success")
        return redirect(url_for("index"))

    # Check if email used by host
    host = Host.query.filter_by(email=email).first()
    if host:
        flash("This email is already registered as host.", "warning")
        return redirect(url_for("login"))

    # New user → store in session temporarily
    session["google_email"] = email
    session["google_name"] = name

    return redirect(url_for("signup_google"))

@app.route("/signup/google", methods=["GET", "POST"])
def signup_google():

    if "google_email" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        full_name = request.form.get("full_name")
        password = request.form.get("password")
        is_host = request.form.get("is_host")

        email = session["google_email"]

        # 🔥 Prevent duplicate email
        if User.query.filter_by(email=email).first() or Host.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("login"))

        # HOST SIGNUP
        if is_host:

            logo_filename = None
            logo_file = request.files.get("company_logo")

            if logo_file and allowed_file(logo_file.filename):
                filename = secure_filename(logo_file.filename)
                logo_filename = f"{int(datetime.utcnow().timestamp())}_{filename}"
                logo_path = os.path.join(app.config["UPLOAD_FOLDER"], logo_filename)
                logo_file.save(logo_path)

            host = Host(
                full_name=full_name,
                email=email,
                company_name=request.form.get("company_name"),
                company_logo=logo_filename,  # ✅ SAVE IMAGE NAME
                website=request.form.get("website"),
                city=request.form.get("city"),
                state=request.form.get("state"),
                created_at=datetime.utcnow(),
                last_login=None
            )

            host.set_password(password)

            db.session.add(host)
            db.session.commit()

            session.pop("google_email", None)
            session.pop("google_name", None)

            session["host_id"] = host.id
            session["role"] = "host"
            session["name"] = host.full_name

            flash("Host account created via Google!", "success")
            return redirect(url_for("index"))

        # NORMAL USER SIGNUP

        skills_list = request.form.getlist("skills")
        skills_str = ",".join(skills_list)

        user = User(
            full_name=full_name,
            email=email,
            description=request.form.get("description"),
            college=request.form.get("college"),
            course=request.form.get("course"),
            year=request.form.get("year"),
            skills=skills_str,
            created_at=datetime.utcnow(),
            last_login=None,
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        session.pop("google_email", None)
        session.pop("google_name", None)

        session["user_id"] = user.id
        session["role"] = "user"
        session["name"] = user.full_name

        send_welcome_email(user)

        flash("Account created successfully via Google!", "success")
        return redirect(url_for("index"))

    return render_template(
        "signup_google.html",
        email=session.get("google_email"),
        name=session.get("google_name")
    )

@app.route("/term_of_service")
def term_of_service():
    return render_template("terms_of_service.html")

@app.route("/privacy_policy")
def privacy_policy():
    return render_template("privacy_policy.html")

@app.route("/help_center")
def help_center():
    return render_template("help_center.html")

# @app.route("/contact_us")
# def contact_us():
#     return render_template("contact_us.html")

@app.route("/contact-us", methods=["GET", "POST"])
def contact_us():



    user_id = session.get("user_id")
    user = User.query.get(user_id)

    if request.method == "POST":

        subject = request.form.get("subject")
        message = request.form.get("message")

        msg = Message(
            subject=f"Contact Form: {subject}",
            recipients=["eventiq2026@gmail.com"]
        )

        msg.body = f"""
New Contact Message from EventIQ

User Name: {user.full_name}
User Email: {user.email}

Subject: {subject}

Message:
{message}
"""

        mail.send(msg)

        flash("Your message has been sent successfully!", "success")
        return redirect(url_for("contact_us"))

    return render_template("contact_us.html")

from datetime import date

from datetime import date

def update_event_status():
    today = date.today()

    events = Event.query.all()

    for event in events:

        if event.start_date and event.end_date:

            if today < event.start_date:
                event.status = "upcoming"

            elif event.start_date <= today <= event.end_date:
                event.status = "live"

            elif today > event.end_date:
                event.status = "completed"

    db.session.commit()
