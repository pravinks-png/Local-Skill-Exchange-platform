import json
import bcrypt
from datetime import datetime
from bson import ObjectId

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .db import (
    get_users_collection,
    get_skills_collection,
    get_appointments_collection,
    serialize_doc
)
from .seed_data import seed_database

def index_view(request):
    return render(request, 'index.html')

@csrf_exempt
def api_register(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid JSON body'}, status=400)
    
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    bio = (data.get('bio') or '').strip()
    skills_offered_raw = data.get('skills_offered', '')
    skills_wanted_raw = data.get('skills_wanted', '')

    if not name or not email or not password:
        return JsonResponse({'success': False, 'error': 'Name, email, and password are required'}, status=400)

    users_col = get_users_collection()
    if users_col.find_one({'email': email}):
        return JsonResponse({'success': False, 'error': 'User with this email already exists'}, status=400)

    # Hash password with bcrypt
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Parse skills
    if isinstance(skills_offered_raw, str):
        skills_offered = [s.strip() for s in skills_offered_raw.split(',') if s.strip()]
    else:
        skills_offered = skills_offered_raw

    if isinstance(skills_wanted_raw, str):
        skills_wanted = [s.strip() for s in skills_wanted_raw.split(',') if s.strip()]
    else:
        skills_wanted = skills_wanted_raw

    user_doc = {
        'name': name,
        'email': email,
        'password_hash': hashed,
        'bio': bio,
        'skills_offered': skills_offered,
        'skills_wanted': skills_wanted,
        'rating': 5.0,
        'created_at': datetime.utcnow().isoformat()
    }

    res = users_col.insert_one(user_doc)
    user_id = str(res.inserted_id)

    return JsonResponse({
        'success': True,
        'message': 'Account created successfully',
        'user': {
            'id': user_id,
            'name': name,
            'email': email,
            'bio': bio,
            'skills_offered': skills_offered,
            'skills_wanted': skills_wanted,
            'rating': 5.0
        }
    }, status=201)

@csrf_exempt
def api_login(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid JSON body'}, status=400)
    
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return JsonResponse({'success': False, 'error': 'Email and password are required'}, status=400)

    users_col = get_users_collection()
    user = users_col.find_one({'email': email})

    if not user:
        return JsonResponse({'success': False, 'error': 'Invalid email or password'}, status=401)

    password_hash = user.get('password_hash', '')
    if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
        return JsonResponse({'success': False, 'error': 'Invalid email or password'}, status=401)

    return JsonResponse({
        'success': True,
        'message': 'Login successful',
        'user': {
            'id': str(user['_id']),
            'name': user.get('name', ''),
            'email': user.get('email', ''),
            'bio': user.get('bio', ''),
            'skills_offered': user.get('skills_offered', []),
            'skills_wanted': user.get('skills_wanted', []),
            'rating': user.get('rating', 5.0)
        }
    })

@csrf_exempt
def api_skills(request):
    skills_col = get_skills_collection()

    if request.method == 'GET':
        category = request.GET.get('category', '').strip()
        search = request.GET.get('search', '').strip()

        query = {}
        if category and category.lower() != 'all':
            query['category'] = {'$regex': f'^{category}$', '$options': 'i'}

        if search:
            query['$or'] = [
                {'title': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}},
                {'category': {'$regex': search, '$options': 'i'}},
                {'offered_by.name': {'$regex': search, '$options': 'i'}},
                {'offered_by.email': {'$regex': search, '$options': 'i'}}
            ]

        cursor = skills_col.find(query).sort('created_at', -1)
        skills_list = [serialize_doc(doc) for doc in cursor]
        return JsonResponse(skills_list, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            return JsonResponse({'success': False, 'error': 'Invalid JSON body'}, status=400)

        title = (data.get('title') or '').strip()
        category = (data.get('category') or 'Programming').strip()
        description = (data.get('description') or '').strip()
        level = (data.get('level') or 'Intermediate').strip()
        exchange_type = (data.get('exchange_type') or 'Both (Teach or Get Things Done)').strip()
        user_info = data.get('user', {})

        if not title:
            return JsonResponse({'success': False, 'error': 'Skill title is required'}, status=400)

        if not user_info.get('email') and not user_info.get('id'):
            return JsonResponse({'success': False, 'error': 'User must be authenticated to offer a skill'}, status=401)

        skill_doc = {
            'title': title,
            'category': category,
            'description': description,
            'level': level,
            'exchange_type': exchange_type,
            'offered_by': {
                'user_id': user_info.get('id', ''),
                'name': user_info.get('name', 'Community Member'),
                'email': user_info.get('email', '')
            },
            'created_at': datetime.utcnow().isoformat()
        }

        res = skills_col.insert_one(skill_doc)
        skill_doc['id'] = str(res.inserted_id)

        return JsonResponse({
            'success': True,
            'message': 'Skill published successfully',
            'skill': serialize_doc(skill_doc)
        }, status=201)

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_skill_detail(request, skill_id):
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    skills_col = get_skills_collection()
    try:
        doc = skills_col.find_one({'_id': ObjectId(skill_id)})
    except Exception:
        doc = None

    if not doc:
        return JsonResponse({'success': False, 'error': 'Skill not found'}, status=404)

    return JsonResponse(serialize_doc(doc))

@csrf_exempt
def api_appointments(request):
    appts_col = get_appointments_collection()

    if request.method == 'GET':
        user_id = request.GET.get('user_id', '').strip()
        user_email = request.GET.get('email', '').strip().lower()

        query = {}
        conditions = []
        if user_id:
            conditions.extend([
                {'requester.user_id': user_id},
                {'provider.user_id': user_id}
            ])
        if user_email:
            conditions.extend([
                {'requester.email': user_email},
                {'provider.email': user_email}
            ])

        if conditions:
            query['$or'] = conditions

        cursor = appts_col.find(query).sort('created_at', -1)
        appts_list = [serialize_doc(doc) for doc in cursor]
        return JsonResponse(appts_list, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            return JsonResponse({'success': False, 'error': 'Invalid JSON body'}, status=400)

        skill_id = data.get('skill_id', '')
        skill_title = data.get('skill_title', 'General Skill Session')
        requester = data.get('requester', {})
        provider = data.get('provider', {})
        session_date = data.get('session_date', '')
        session_time = data.get('session_time', '')
        appt_type = data.get('type', 'LEARN SKILL SESSION')
        note = data.get('note', '')

        # Enforce self-booking prevention check
        req_id = requester.get('user_id') or requester.get('id')
        prov_id = provider.get('user_id') or provider.get('id')
        req_email = (requester.get('email') or '').lower()
        prov_email = (provider.get('email') or '').lower()

        if (req_id and prov_id and req_id == prov_id) or (req_email and prov_email and req_email == prov_email):
            return JsonResponse({
                'success': False,
                'error': 'Self-booking is not allowed. You cannot book an appointment for your own skill listing.'
            }, status=400)

        appt_doc = {
            'skill_id': str(skill_id),
            'skill_title': skill_title,
            'requester': {
                'user_id': str(req_id),
                'name': requester.get('name', ''),
                'email': requester.get('email', '')
            },
            'provider': {
                'user_id': str(prov_id),
                'name': provider.get('name', ''),
                'email': provider.get('email', '')
            },
            'session_date': session_date,
            'session_time': session_time,
            'type': appt_type,
            'note': note,
            'status': 'Pending',
            'created_at': datetime.utcnow().isoformat()
        }

        res = appts_col.insert_one(appt_doc)
        appt_doc['id'] = str(res.inserted_id)

        return JsonResponse({
            'success': True,
            'message': 'Appointment booked successfully',
            'appointment': serialize_doc(appt_doc)
        }, status=201)

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_appointment_status(request, appt_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid JSON body'}, status=400)

    new_status = data.get('status')
    if new_status not in ['Confirmed', 'Cancelled', 'Completed', 'Pending']:
        return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)

    appts_col = get_appointments_collection()
    try:
        res = appts_col.update_one({'_id': ObjectId(appt_id)}, {'$set': {'status': new_status}})
        if res.matched_count == 0:
            return JsonResponse({'success': False, 'error': 'Appointment not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({
        'success': True,
        'message': f'Appointment status updated to {new_status}',
        'status': new_status
    })

@csrf_exempt
def api_seed(request):
    try:
        stats = seed_database()
        return JsonResponse({
            'success': True,
            'message': 'Sample users, skills, and appointments initialized successfully',
            'stats': stats
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
