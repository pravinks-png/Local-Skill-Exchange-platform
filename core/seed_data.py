import bcrypt
from datetime import datetime
from .db import get_users_collection, get_skills_collection, get_appointments_collection

def hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed_database():
    users_col = get_users_collection()
    skills_col = get_skills_collection()
    appts_col = get_appointments_collection()

    # Clear existing collections
    users_col.delete_many({})
    skills_col.delete_many({})
    appts_col.delete_many({})

    # 1. Users
    demo_users = [
        {
            "name": "Alex Rivera",
            "email": "alex@example.com",
            "password_hash": hash_pw("demo123"),
            "bio": "Full stack developer & UI enthusiast",
            "skills_offered": ["UI/UX Design", "Sound Design", "Audio Mixing"],
            "skills_wanted": ["Python", "Machine Learning"],
            "rating": 4.9,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "name": "pravin",
            "email": "pravin@gmail.com",
            "password_hash": hash_pw("pravin123"),
            "bio": "Python backend developer & tech explorer",
            "skills_offered": ["Python", "Django", "REST APIs"],
            "skills_wanted": ["UI/UX Design", "Figma"],
            "rating": 5.0,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "name": "vignesh",
            "email": "vignesh@gmail.com",
            "password_hash": hash_pw("vignesh123"),
            "bio": "Frontend enthusiast and music lover",
            "skills_offered": ["Acoustic Guitar", "Music Theory"],
            "skills_wanted": ["Python", "Django"],
            "rating": 4.8,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "name": "Sarah Chen",
            "email": "sarah@example.com",
            "password_hash": hash_pw("demo123"),
            "bio": "Senior Product Designer with 6+ years experience",
            "skills_offered": ["Figma", "UI/UX Design", "Design Systems"],
            "skills_wanted": ["Spanish", "Audio Editing"],
            "rating": 5.0,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "name": "Marcus Vance",
            "email": "marcus@example.com",
            "password_hash": hash_pw("demo123"),
            "bio": "Audio engineer & podcast producer with 10+ years experience",
            "skills_offered": ["Podcast Audio", "Voice-Over Mixing", "Sound Design"],
            "skills_wanted": ["SEO", "Marketing"],
            "rating": 4.9,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "name": "Elena Rostova",
            "email": "elena@example.com",
            "password_hash": hash_pw("demo123"),
            "bio": "Polyglot and certified Spanish & French language instructor",
            "skills_offered": ["Conversational Spanish", "French", "Grammar"],
            "skills_wanted": ["Web Development", "Python"],
            "rating": 4.9,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "name": "David Miller",
            "email": "david@example.com",
            "password_hash": hash_pw("demo123"),
            "bio": "Startup growth consultant & business strategy mentor",
            "skills_offered": ["Business Strategy", "Pitch Decks", "Marketing"],
            "skills_wanted": ["UI/UX Design", "Product Analytics"],
            "rating": 4.8,
            "created_at": datetime.utcnow().isoformat()
        }
    ]

    inserted_users = {}
    for u in demo_users:
        res = users_col.insert_one(u)
        inserted_users[u['email']] = {
            "id": str(res.inserted_id),
            "name": u['name'],
            "email": u['email']
        }

    # 2. Skills
    demo_skills = [
        {
            "title": "python",
            "category": "Programming",
            "description": "python",
            "level": "Intermediate",
            "exchange_type": "Both (Learn or Get Work Done)",
            "offered_by": inserted_users["pravin@gmail.com"],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "title": "sound",
            "category": "Music",
            "description": "nothing",
            "level": "Intermediate",
            "exchange_type": "Both (Learn or Get Work Done)",
            "offered_by": inserted_users["alex@example.com"],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "title": "design",
            "category": "Programming",
            "description": "nothing",
            "level": "Intermediate",
            "exchange_type": "Both (Learn or Get Work Done)",
            "offered_by": inserted_users["alex@example.com"],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "title": "Podcast & Voice-Over Audio Post-Production",
            "category": "Audio/Video",
            "description": "Send me your raw audio and I will remove background noise, level vocals, and deliver studio-quality files.",
            "level": "Expert",
            "exchange_type": "Both (Learn or Get Work Done)",
            "offered_by": inserted_users["marcus@example.com"],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "title": "Acoustic Guitar - Chords & Song Playing",
            "category": "Music",
            "description": "Learn your favorite songs in 30 days! Step-by-step finger picking, rhythm strumming, and chord transitions.",
            "level": "Beginner",
            "exchange_type": "Learn Skill (Teaching / Mentoring)",
            "offered_by": inserted_users["vignesh@gmail.com"],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "title": "High-Conversion UI/UX Design in Figma",
            "category": "Design",
            "description": "Book 1-on-1 tutoring on Figma auto-layout and design systems, OR have me review and redesign your web application screens.",
            "level": "All Levels",
            "exchange_type": "Both (Learn or Get Work Done)",
            "offered_by": inserted_users["sarah@example.com"],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "title": "Master Python & REST APIs with Django",
            "category": "Programming",
            "description": "I can teach you Python fundamentals, Django REST architecture, or build custom API endpoints for your frontend apps.",
            "level": "Beginner to Advanced",
            "exchange_type": "Both (Learn or Get Work Done)",
            "offered_by": inserted_users["pravin@gmail.com"],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "title": "Conversational Spanish for Beginners & Travelers",
            "category": "Languages",
            "description": "Practice speaking Spanish with a native-level speaker. Focus on real-world conversations, travel vocabulary, and daily dialogues.",
            "level": "Beginner",
            "exchange_type": "Learn Skill (Teaching / Mentoring)",
            "offered_by": inserted_users["elena@example.com"],
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "title": "Startup Pitch Deck & Business Model Strategy",
            "category": "Business",
            "description": "1-on-1 mentoring to structure your pitch deck, identify customer segments, and build an investor-ready business model.",
            "level": "Intermediate",
            "exchange_type": "Get Things Done (Task / Project)",
            "offered_by": inserted_users["david@example.com"],
            "created_at": datetime.utcnow().isoformat()
        }
    ]

    inserted_skills = {}
    for s in demo_skills:
        res = skills_col.insert_one(s)
        inserted_skills[s['title']] = str(res.inserted_id)

    # 3. Appointments
    demo_appts = [
        {
            "skill_id": inserted_skills["design"],
            "skill_title": "design",
            "provider": inserted_users["alex@example.com"],
            "requester": inserted_users["pravin@gmail.com"],
            "session_date": "2026-10-09",
            "session_time": "10:00 AM",
            "type": "LEARN SKILL SESSION",
            "note": "Mentoring on user interface design principles and layout structure.",
            "status": "Pending",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "skill_id": inserted_skills["High-Conversion UI/UX Design in Figma"],
            "skill_title": "High-Conversion UI/UX Design in Figma",
            "provider": inserted_users["sarah@example.com"],
            "requester": inserted_users["alex@example.com"],
            "session_date": "2026-10-13",
            "session_time": "10:00 AM",
            "type": "LEARN SKILL SESSION",
            "note": "Want to learn Figma auto-layout best practices.",
            "status": "Pending",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "skill_id": inserted_skills["python"],
            "skill_title": "python",
            "provider": inserted_users["pravin@gmail.com"],
            "requester": inserted_users["vignesh@gmail.com"],
            "session_date": "2026-10-09",
            "session_time": "10:00 AM",
            "type": "LEARN SKILL SESSION",
            "note": "Guidance on Django setup and REST view endpoints.",
            "status": "Pending",
            "created_at": datetime.utcnow().isoformat()
        }
    ]

    for a in demo_appts:
        appts_col.insert_one(a)

    return {
        "users_count": len(demo_users),
        "skills_count": len(demo_skills),
        "appointments_count": len(demo_appts)
    }
