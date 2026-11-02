var app = angular.module('skillExchangeApp', []);

app.controller('SkillExchangeController', ['$scope', '$http', '$timeout', function($scope, $http, $timeout) {
    // Current Active View: 'explore', 'appointments', 'login', 'register'
    $scope.currentView = 'explore';
    $scope.categories = ['All', 'Programming', 'Design', 'Music', 'Audio/Video', 'Languages', 'Business'];
    $scope.activeCategory = 'All';
    $scope.searchQuery = '';
    
    $scope.skills = [];
    $scope.appointments = [];
    $scope.appointmentCount = 0;
    
    $scope.showOfferModal = false;
    $scope.showBookingModal = false;
    $scope.selectedSkill = null;
    
    // Auth State
    $scope.currentUser = null;
    var savedUser = localStorage.getItem('skillExchangeUser');
    if (savedUser) {
        try {
            $scope.currentUser = JSON.parse(savedUser);
        } catch(e) {
            $scope.currentUser = null;
        }
    }

    // Forms
    $scope.loginForm = { email: 'alex@example.com', password: 'demo123' };
    $scope.registerForm = {
        name: '',
        email: '',
        password: '',
        bio: '',
        skills_offered: '',
        skills_wanted: ''
    };

    $scope.newSkill = {
        title: '',
        category: 'Programming',
        level: 'Intermediate',
        exchange_type: 'Both (Teach or Get Things Done)',
        description: ''
    };

    $scope.bookingData = {
        skill_id: '',
        skill_title: '',
        provider: null,
        type: 'I want to Learn this skill (Mentoring / Teaching Session)',
        session_date: '2026-10-09',
        session_time: '10:00 AM',
        note: ''
    };

    $scope.toast = null;

    $scope.showToast = function(msg, type) {
        $scope.toast = { message: msg, type: type || 'success' };
        $timeout(function() {
            $scope.toast = null;
        }, 3500);
    };

    // Navigation
    $scope.setView = function(view) {
        $scope.currentView = view;
        if (view === 'appointments') {
            if (!$scope.currentUser) {
                $scope.currentView = 'login';
                $scope.showToast('Please log in to view your appointments', 'info');
                return;
            }
            $scope.loadAppointments();
        } else if (view === 'explore') {
            $scope.loadSkills();
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    // Load Skills
    $scope.loadSkills = function() {
        var params = {};
        if ($scope.activeCategory && $scope.activeCategory !== 'All') {
            params.category = $scope.activeCategory;
        }
        if ($scope.searchQuery) {
            params.search = $scope.searchQuery;
        }

        $http.get('/api/skills/', { params: params })
            .then(function(res) {
                $scope.skills = res.data;
            }, function(err) {
                console.error('Failed to load skills:', err);
                $scope.showToast('Could not load skills catalog', 'error');
            });
    };

    // Category Filter
    $scope.selectCategory = function(cat) {
        $scope.activeCategory = cat;
        $scope.loadSkills();
    };

    // Search input change
    $scope.onSearch = function() {
        $scope.loadSkills();
    };

    // Auth Actions
    $scope.login = function() {
        if (!$scope.loginForm.email || !$scope.loginForm.password) {
            $scope.showToast('Please enter both email and password', 'error');
            return;
        }

        $http.post('/api/auth/login/', $scope.loginForm)
            .then(function(res) {
                if (res.data.success) {
                    $scope.currentUser = res.data.user;
                    localStorage.setItem('skillExchangeUser', JSON.stringify(res.data.user));
                    $scope.showToast('Welcome back, ' + $scope.currentUser.name + '!', 'success');
                    $scope.setView('explore');
                    $scope.loadAppointments();
                } else {
                    $scope.showToast(res.data.error || 'Login failed', 'error');
                }
            }, function(err) {
                var msg = (err.data && err.data.error) ? err.data.error : 'Login error. Check your credentials.';
                $scope.showToast(msg, 'error');
            });
    };

    $scope.register = function() {
        if (!$scope.registerForm.name || !$scope.registerForm.email || !$scope.registerForm.password) {
            $scope.showToast('Full name, email, and password are required', 'error');
            return;
        }

        $http.post('/api/auth/register/', $scope.registerForm)
            .then(function(res) {
                if (res.data.success) {
                    $scope.currentUser = res.data.user;
                    localStorage.setItem('skillExchangeUser', JSON.stringify(res.data.user));
                    $scope.showToast('Account created successfully! Welcome to SkillExchange.', 'success');
                    $scope.setView('explore');
                } else {
                    $scope.showToast(res.data.error || 'Registration failed', 'error');
                }
            }, function(err) {
                var msg = (err.data && err.data.error) ? err.data.error : 'Registration failed. Try again.';
                $scope.showToast(msg, 'error');
            });
    };

    $scope.logout = function() {
        $scope.currentUser = null;
        localStorage.removeItem('skillExchangeUser');
        $scope.appointments = [];
        $scope.appointmentCount = 0;
        $scope.showToast('You have been logged out.', 'info');
        $scope.setView('explore');
    };

    $scope.quickFillDemo = function(email, pass) {
        $scope.loginForm.email = email;
        $scope.loginForm.password = pass;
    };

    // Check if skill belongs to logged in user
    $scope.isOwnSkill = function(skill) {
        if (!$scope.currentUser || !skill || !skill.offered_by) return false;
        var myId = $scope.currentUser.id;
        var myEmail = ($scope.currentUser.email || '').toLowerCase();
        var provId = skill.offered_by.user_id;
        var provEmail = (skill.offered_by.email || '').toLowerCase();

        return (myId && provId && myId === provId) || (myEmail && provEmail && myEmail === provEmail);
    };

    // Offer Skill Modal
    $scope.openOfferModal = function() {
        if (!$scope.currentUser) {
            $scope.setView('login');
            $scope.showToast('Please sign in first to offer a skill listing.', 'info');
            return;
        }
        $scope.newSkill = {
            title: '',
            category: 'Programming',
            level: 'Intermediate',
            exchange_type: 'Both (Teach or Get Things Done)',
            description: ''
        };
        $scope.showOfferModal = true;
    };

    $scope.closeOfferModal = function() {
        $scope.showOfferModal = false;
    };

    $scope.publishSkill = function() {
        if (!$scope.newSkill.title) {
            $scope.showToast('Please enter a title for your skill', 'error');
            return;
        }

        var payload = {
            title: $scope.newSkill.title,
            category: $scope.newSkill.category,
            level: $scope.newSkill.level,
            exchange_type: $scope.newSkill.exchange_type,
            description: $scope.newSkill.description,
            user: {
                id: $scope.currentUser.id,
                name: $scope.currentUser.name,
                email: $scope.currentUser.email
            }
        };

        $http.post('/api/skills/', payload)
            .then(function(res) {
                if (res.data.success) {
                    $scope.showToast('Skill published successfully!', 'success');
                    $scope.showOfferModal = false;
                    $scope.loadSkills();
                } else {
                    $scope.showToast(res.data.error || 'Failed to publish skill', 'error');
                }
            }, function(err) {
                var msg = (err.data && err.data.error) ? err.data.error : 'Failed to publish skill.';
                $scope.showToast(msg, 'error');
            });
    };

    // Booking Appointment Modal
    $scope.openBookingModal = function(skill) {
        if (!$scope.currentUser) {
            $scope.setView('login');
            $scope.showToast('Please sign in first to book an appointment.', 'info');
            return;
        }

        if ($scope.isOwnSkill(skill)) {
            $scope.showToast('You cannot book your own skill listing.', 'error');
            return;
        }

        $scope.selectedSkill = skill;
        
        // Format tomorrow's date by default
        var d = new Date();
        d.setDate(d.getDate() + 1);
        var yyyy = d.getFullYear();
        var mm = String(d.getMonth() + 1).padStart(2, '0');
        var dd = String(d.getDate()).padStart(2, '0');
        var defaultDate = yyyy + '-' + mm + '-' + dd;

        $scope.bookingData = {
            skill_id: skill.id,
            skill_title: skill.title,
            provider: skill.offered_by,
            type: 'I want to Learn this skill (Mentoring / Teaching Session)',
            session_date: defaultDate,
            session_time: '10:00 AM',
            note: ''
        };
        $scope.showBookingModal = true;
    };

    $scope.closeBookingModal = function() {
        $scope.showBookingModal = false;
        $scope.selectedSkill = null;
    };

    $scope.confirmBooking = function() {
        if (!$scope.bookingData.session_date) {
            $scope.showToast('Please select a date for the session', 'error');
            return;
        }

        var apptType = ($scope.bookingData.type.indexOf('Learn') !== -1)
            ? 'LEARN SKILL SESSION'
            : 'GET THINGS DONE SESSION';

        var payload = {
            skill_id: $scope.bookingData.skill_id,
            skill_title: $scope.bookingData.skill_title,
            requester: {
                user_id: $scope.currentUser.id,
                name: $scope.currentUser.name,
                email: $scope.currentUser.email
            },
            provider: $scope.bookingData.provider,
            session_date: $scope.bookingData.session_date,
            session_time: $scope.bookingData.session_time,
            type: apptType,
            note: $scope.bookingData.note
        };

        $http.post('/api/appointments/', payload)
            .then(function(res) {
                if (res.data.success) {
                    $scope.showToast('Appointment request sent successfully!', 'success');
                    $scope.showBookingModal = false;
                    $scope.loadAppointments();
                    $scope.setView('appointments');
                } else {
                    $scope.showToast(res.data.error || 'Failed to book appointment', 'error');
                }
            }, function(err) {
                var msg = (err.data && err.data.error) ? err.data.error : 'Failed to book appointment.';
                $scope.showToast(msg, 'error');
            });
    };

    // Load Appointments for Current User
    $scope.loadAppointments = function() {
        if (!$scope.currentUser) return;

        var params = {
            user_id: $scope.currentUser.id,
            email: $scope.currentUser.email
        };

        $http.get('/api/appointments/', { params: params })
            .then(function(res) {
                $scope.appointments = res.data;
                $scope.appointmentCount = res.data.length;
            }, function(err) {
                console.error('Failed to load appointments:', err);
            });
    };

    // Provider check
    $scope.isProvider = function(appt) {
        if (!$scope.currentUser || !appt || !appt.provider) return false;
        var myId = $scope.currentUser.id;
        var myEmail = ($scope.currentUser.email || '').toLowerCase();
        return (appt.provider.user_id && appt.provider.user_id === myId) ||
               (appt.provider.email && appt.provider.email.toLowerCase() === myEmail);
    };

    // Requester check
    $scope.isRequester = function(appt) {
        if (!$scope.currentUser || !appt || !appt.requester) return false;
        var myId = $scope.currentUser.id;
        var myEmail = ($scope.currentUser.email || '').toLowerCase();
        return (appt.requester.user_id && appt.requester.user_id === myId) ||
               (appt.requester.email && appt.requester.email.toLowerCase() === myEmail);
    };

    // Update Status: Confirmed, Cancelled, Completed
    $scope.updateAppointmentStatus = function(appt, newStatus) {
        $http.post('/api/appointments/' + appt.id + '/status/', { status: newStatus })
            .then(function(res) {
                if (res.data.success) {
                    appt.status = newStatus;
                    $scope.showToast('Appointment marked as ' + newStatus, 'success');
                } else {
                    $scope.showToast(res.data.error || 'Could not update status', 'error');
                }
            }, function(err) {
                var msg = (err.data && err.data.error) ? err.data.error : 'Could not update status.';
                $scope.showToast(msg, 'error');
            });
    };

    // Initial Load
    $scope.loadSkills();
    if ($scope.currentUser) {
        $scope.loadAppointments();
    }
}]);
