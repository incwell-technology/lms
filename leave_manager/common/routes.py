from leave_manager.common.check_leave_admin import is_leave_issuer
from django.urls import reverse_lazy

all_navigation_routes = [
    # {
    #     'title': 'dashboard',
    #     'url': reverse_lazy('leave_manager_dashboard'),
    #     'admin': False,
    #     'active': False,
    #      'password': False,
    #     'icon': 'pe-7s-home'
    # },

    {
        'title': 'register user',
        'url': reverse_lazy('user-register'),
        'admin': True,
        'active': False,
        'password': False,
        'icon': 'pe-7s-add-user'
    },
    {
        'title': 'my profile',
        'url': reverse_lazy('leave_manager_my_profile'),
        'admin': False,
        'active': False,
        'password': False,
        'icon': 'pe-7s-user'
    },
    {
        'title': 'users',
        'url': reverse_lazy('leave_manager_users'),
        'admin': False,
        'active': False,
        'password': False,
        'icon': 'pe-7s-users'
    },
    {
        'title': 'leave today',
        'url': reverse_lazy('leave_manager_leave_today'),
        'admin': False,
        'active': False,
        'password': False,
        'icon': 'pe-7s-plane'
    },
    {
        'title': 'apply leave',
        'url': reverse_lazy('leave_manager_apply_leave'),
        'admin': False,
        'active': False,
        'password': False,
        'icon': 'pe-7s-paper-plane'
    },
    {
        'title': 'birthdays',
        'url': reverse_lazy('leave_manager_get_birthday_today'),
        'admin': False,
        'active': False,
        'password': False,
        'icon': 'pe-7s-gift'
    },
    {
        'title': 'leave requests',
        'url': reverse_lazy('leave_manager_leave_requests'),
        'admin': True,
        'active': False,
        'password': False,
        'icon': 'pe-7s-bandaid',
        'popup':'badge badge-light'
    },
    {
        'title': 'leave report',
        'url': reverse_lazy('leave-report'),
        'admin': True,
        'active': False,
        'password': False,
        'icon': 'pe-7s-note2'
    },
    {
        'title': 'company holidays',
        'url': reverse_lazy('company-holiday'),
        'admin': False,
        'active': False,
        'password': False,
        'icon': 'pe-7s-power'
    },
    {
        'title': 'rhymes',
        'url': reverse_lazy('rhymes'),
        'admin': True,
        'active': False,
        'password': False,
        'icon': 'pe-7s-headphones'
    },
    {
        'title': 'my leave history',
        'url': reverse_lazy('leave-history'),
        'admin': False,
        'active': False,
        'password': False,
        'icon': 'pe-7s-graph',
        'pop':'badge badge-light'

    },
    {
        'title': 'apply compensation',
        'url': reverse_lazy('leave_manager_apply_compensationLeave'),
        'admin': False,
        'active': False,
        'password': False,
        'icon': 'pe-7s-pin'
    },
    {
        'title': 'password reset',
        'url': reverse_lazy('password-change'),
        'admin': False,
        'active': False,
        'password': True,
        'icon': 'pe-7s-pin'
    },

]

non_admin_navigation_routes = [route for route in all_navigation_routes if not route['admin'] and not route['password']]
admin_navigation_routes = [route for route in all_navigation_routes if not route['password']]

def get_routes(user):
    if is_leave_issuer(user):
        return admin_navigation_routes
    return non_admin_navigation_routes


def get_formatted_routes(routes, active_page):
    formatted_routes = []
    for route in routes:
        route['active'] = False
        if route['title'] == active_page:
            route['active'] = True
        formatted_routes.append(route)
    return formatted_routes
