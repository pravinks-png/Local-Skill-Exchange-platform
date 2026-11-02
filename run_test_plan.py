import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:8000"

def req(path, method="GET", data=None):
    url = BASE_URL + path
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data else None
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))
    except Exception as e:
        return 0, str(e)

print("--- TESTING SKILLEXCHANGE ENDPOINTS ---")

# 0. Check Homepage HTML
try:
    with urllib.request.urlopen(BASE_URL + "/") as r:
        html = r.read().decode("utf-8")
        print(f"Homepage HTTP Status: {r.status}, HTML length: {len(html)} bytes")
        assert "SkillExchange" in html
        assert "ng-app=\"skillExchangeApp\"" in html
        print("[PASS] Homepage renders successfully with AngularJS app template!")
except Exception as e:
    print("[FAIL] Homepage failed:", e)

# T1: Register new user
t1_status, t1_res = req("/api/auth/register/", "POST", {
    "name": "Test User",
    "email": "testuser_unique_2@example.com",
    "password": "SecretPassword123",
    "bio": "Testing registration",
    "skills_offered": "Testing, QA",
    "skills_wanted": "Django, MongoDB"
})
print(f"T1 (Register): HTTP {t1_status}, Success: {t1_res.get('success')}")

# T2: Login valid and invalid
t2_valid_status, t2_valid_res = req("/api/auth/login/", "POST", {
    "email": "testuser_unique_2@example.com",
    "password": "SecretPassword123"
})
t2_invalid_status, t2_invalid_res = req("/api/auth/login/", "POST", {
    "email": "testuser_unique_2@example.com",
    "password": "WrongPassword"
})
print(f"T2 (Login Valid): HTTP {t2_valid_status}, Success: {t2_valid_res.get('success')}")
print(f"T2 (Login Invalid): HTTP {t2_invalid_status}, Error: {t2_invalid_res.get('error')}")

# T3: Filter skills by category and search keyword
t3_prog_status, t3_prog_skills = req("/api/skills/?category=Programming")
t3_search_status, t3_search_skills = req("/api/skills/?search=python")
print(f"T3 (Filter Category 'Programming'): Found {len(t3_prog_skills)} skills")
print(f"T3 (Search 'python'): Found {len(t3_search_skills)} skills")

# T4: Publish a new skill listing
t4_status, t4_res = req("/api/skills/", "POST", {
    "title": "Automated Testing with Selenium",
    "category": "Programming",
    "level": "Intermediate",
    "exchange_type": "Both (Teach or Get Things Done)",
    "description": "Learn hands-on end-to-end testing with Selenium and Python.",
    "user": {
        "id": t2_valid_res["user"]["id"],
        "name": t2_valid_res["user"]["name"],
        "email": t2_valid_res["user"]["email"]
    }
})
new_skill_id = t4_res["skill"]["id"] if t4_res.get("success") else None
print(f"T4 (Publish Skill): HTTP {t4_status}, Skill ID: {new_skill_id}")

# T5: Book a session on another user's skill (e.g. Alex's skill 'sound')
_, all_s = req("/api/skills/")
alex_skills = [s for s in all_s if s.get("offered_by", {}).get("email") == "alex@example.com"]
alex_skill = alex_skills[0]

t5_status, t5_res = req("/api/appointments/", "POST", {
    "skill_id": alex_skill["id"],
    "skill_title": alex_skill["title"],
    "requester": {
        "user_id": t2_valid_res["user"]["id"],
        "name": t2_valid_res["user"]["name"],
        "email": t2_valid_res["user"]["email"]
    },
    "provider": alex_skill["offered_by"],
    "session_date": "2026-10-15",
    "session_time": "11:00 AM",
    "type": "LEARN SKILL SESSION",
    "note": "Interested in audio mentoring session."
})
appt_id = t5_res["appointment"]["id"] if t5_res.get("success") else None
print(f"T5 (Book Session): HTTP {t5_status}, Status: {t5_res.get('appointment', {}).get('status')}")

# T6: Attempt to book one's own listing
t6_status, t6_res = req("/api/appointments/", "POST", {
    "skill_id": new_skill_id,
    "skill_title": "Automated Testing with Selenium",
    "requester": {
        "user_id": t2_valid_res["user"]["id"],
        "name": t2_valid_res["user"]["name"],
        "email": t2_valid_res["user"]["email"]
    },
    "provider": {
        "user_id": t2_valid_res["user"]["id"],
        "name": t2_valid_res["user"]["name"],
        "email": t2_valid_res["user"]["email"]
    },
    "session_date": "2026-10-15",
    "session_time": "11:00 AM",
    "type": "LEARN SKILL SESSION",
    "note": "Self booking attempt"
})
print(f"T6 (Self-Booking Attempt): HTTP {t6_status}, Blocked: {t6_res.get('error')}")

# T7: Provider accepts request
t7_status, t7_res = req(f"/api/appointments/{appt_id}/status/", "POST", {
    "status": "Confirmed"
})
print(f"T7 (Provider Confirms Request): HTTP {t7_status}, New Status: {t7_res.get('status')}")

# T8: Complete confirmed appointment
t8_status, t8_res = req(f"/api/appointments/{appt_id}/status/", "POST", {
    "status": "Completed"
})
print(f"T8 (Mark Completed): HTTP {t8_status}, Final Status: {t8_res.get('status')}")
