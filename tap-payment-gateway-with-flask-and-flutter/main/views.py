# from app import app
from ..models.models import User, Coupon, CouponUsage, Payment
from datetime import datetime, timedelta
import random
import string
from mongoengine import Q
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_user, login_required, current_user
from flask_mongoengine import Document

main = Blueprint('main',__name__,template_folder='templates',static_folder='static', static_url_path='/assets')

@main.route('/')
def index():
    return redirect(url_for('main.get_coupons'))

@main.route('/reports', strict_slashes=False, methods=['GET'])
@login_required
def admin():
    payment_page = request.args.get('payment_page', 1, type=int)  # Get the current page from the query parameter
    coupon_usage_page = request.args.get('coupons_usage_page', 1, type=int)
    per_page = 5
    coupons = Coupon.objects(valid=True)
    for coupon in coupons:
        coupon.formatted_date = coupon.valid_to.strftime("%d %b %Y")
    coupons_usage = CouponUsage.objects.paginate(page=coupon_usage_page,per_page=per_page)
    payments = Payment.objects.paginate(page=payment_page,per_page=per_page)
    total_amount = Payment.objects.aggregate([
        {
            '$group': {
                '_id': None,
                'total': {'$sum': '$amount'}
            }
        }
    ])
    total_amount = next(total_amount, None)
    if total_amount:
        total = total_amount['total']
    else:
        total = 0.0
    return render_template('main/admin.html', name=current_user.username,coupons=coupons,
                           coupon_use_count=CouponUsage.objects().count(), total_payment=total,coupons_usage=coupons_usage,payments=payments)

def generate_query(data, type):
    query = Q()
    status_mapping = {
    'Success': True,
    'Failed': False,
    }
    if 'date' in data:
        date = data.get('year') + '-' + data.get('month') + '-' + data.get('date')
        date_object = datetime.strptime(date, '%Y-%m-%d')
        start_of_day = date_object
        end_of_day = (date_object + timedelta(days=1))
        if type == 'usage':
            query &= Q(usage_date__gte=start_of_day, usage_date__lt=end_of_day)
        else:
            query &= Q(payment_date__gte=start_of_day, payment_date__lt=end_of_day)

    elif 'month' in data:
        month = int(data.get('month'))
        year = int(data.get('year'))
        start_date = datetime(year, month, 1)
        end_date = start_date + timedelta(days=32)
        if type == 'usage':
            query &= Q(usage_date__gte=start_date, usage_date__lt=end_date)
        else:
            query &= Q(payment_date__gte=start_date, payment_date__lt=end_date)

    elif 'year' in data:
        year = int(data.get('year'))
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)
        if type == 'usage':
            query &= Q(usage_date__gte=start_date, usage_date__lt=end_date)
        else:
            query &= Q(payment_date__gte=start_date, payment_date__lt=end_date)

    if 'status' in data:
        status_value = status_mapping.get(data.get('status'))
        query &= Q(status=status_value)

    if 'coupon' in data:
        query &= Q(coupon=data.get('coupon'))

    return query


@main.route('/api/payments_data', methods=['GET'])
def get_payment_data():
    page = request.args.get('page', 1, type=int)
    # date_string = request.args.get('date')
    status_string = request.args.get('status')
    page_requested = request.args.get('page_data')
    per_page = 20
    username = request.args.get('username')
    user = User.objects(username__icontains=username)
    if username:
        payments =Payment.objects.filter(user__in=user).order_by('-payment_date')
    else:
        payments = Payment.objects().order_by('-payment_date')

    query = generate_query(request.args,'payment')
    if query:
        count = payments(query).count()
        payments = payments(query).paginate(page=page,per_page=per_page)
    else:
        count = payments.count()
        payments = payments.paginate(page=page,per_page=per_page)

    payment_data = []
    for payment in payments.items:
        username = payment.user.username if payment.user.username else '-'

        payment_json = {
        'id': str(payment.id),
        'amount': payment.amount,
        'date': payment.payment_date.strftime('%Y-%m-%d') if payment.payment_date else '-',  # Format the date as needed
        'username': username,  # Include the username
        'status': payment.status,
        }

        payment_data.append(payment_json)

    response_data = {
        'page': page,
        'total_pages': payments.pages,
        'data': payment_data,
        'has_prev':payments.has_prev,
        'has_next':payments.has_next,
        'count': count
    }

    return jsonify(response_data)

@main.route('/api/coupons_usage_data', methods=['GET'])
def get_coupons_usage_data():
    page = request.args.get('page', 1, type=int)
    page_requested = request.args.get('page_data')
    per_page = 20
    username = request.args.get('username')
    user = User.objects(username__icontains=username)
    if username:
        coupons_usage = CouponUsage.objects.filter(user__in=user).order_by('-usage_date')
    else:
        coupons_usage = CouponUsage.objects().order_by('-usage_date')
    query = generate_query(request.args,'usage')
    if query:
        count = coupons_usage(query).count()

        coupons_usage = coupons_usage(query).paginate(page=page,per_page=per_page)
    else:
        count = coupons_usage.count()
        coupons_usage = coupons_usage.paginate(page=page,per_page=per_page)
    usage_data = []
    for usage in coupons_usage.items:
        username = usage.user.username if usage.user.username else '-'
        coupon = usage.coupon.coupon_code

        usage_json = {
        'id': str(usage.id),
        'date': usage.usage_date.strftime('%Y-%m-%d') if usage.usage_date else '-',  # Format the date as needed
        'username': username,
        'coupon_code': coupon,
        }

        usage_data.append(usage_json)
    response_data = {
        'page': page,
        'total_pages': coupons_usage.pages,
        'data': usage_data,
        'has_prev':coupons_usage.has_prev,
        'has_next':coupons_usage.has_next,
        'count': count
    }

    return jsonify(response_data)

@main.route('/api/payments_filters', methods=['GET'])
def payment_filters():
    result = {}
    if 'month' in request.args:
        year = int(request.args.get('year'))
        month = int(request.args.get('month'))
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)

        payments = Payment.objects(payment_date__gte=start_date, payment_date__lte=end_date)
        days = set()
        for payment in payments:
            day = payment.payment_date.day
            days.add(f'{day:02}')
        days = list(days)
        days.sort()
        result['days'] = days

    elif 'year' in request.args:
        year = request.args.get('year')
        start_date = datetime(int(year), 1, 1)
        end_date = datetime(int(year), 12, 31, 23, 59, 59)
        payments = Payment.objects(payment_date__gte=start_date, payment_date__lte=end_date)
        months = set()
        for payment in payments:
            month = payment.payment_date.month
            months.add(f'{month:02}')
        months = list(months)
        months.sort()
        result['months'] = months

    else:
        year_vals = []
        payments = Payment.objects()
        for date in payments:
            if date.payment_date and date.payment_date.year not in year_vals:
                year_vals.append(date.payment_date.year)

        result['years'] = year_vals
    return jsonify(result)

@main.route('/api/coupons_usage_filters', methods=['GET'])
def coupons_usage_filters():
    result = {}
    if 'month' in request.args:
        year = int(request.args.get('year'))
        month = int(request.args.get('month'))
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)

        usage_obj = CouponUsage.objects(usage_date__gte=start_date, usage_date__lte=end_date)
        days = set()
        for coupon in usage_obj:
            day = coupon.usage_date.day
            days.add(f'{day:02}')
        days = list(days)
        days.sort()
        result['days'] = days

    elif 'year' in request.args:
        year = request.args.get('year')
        start_date = datetime(int(year), 1, 1)
        end_date = datetime(int(year), 12, 31, 23, 59, 59)
        usage_obj = CouponUsage.objects(usage_date__gte=start_date, usage_date__lte=end_date)
        months = set()
        for coupon in usage_obj:
            month = coupon.usage_date.month
            months.add(f'{month:02}')
        months = list(months)
        months.sort()
        result['months'] = months

    else:
        year_vals = []
        usage_obj = CouponUsage.objects()
        for date in usage_obj:
            if date.usage_date and date.usage_date.year not in year_vals:
                year_vals.append(date.usage_date.year)

        result['years'] = year_vals

    usage_obj = CouponUsage.objects()
    coupon_list = [(str(coupon.coupon.id), coupon.coupon.coupon_code) for coupon in usage_obj]
    coupon_list = list(set(coupon_list))
    result['coupons'] = coupon_list
    return jsonify(result)

@main.route('/coupons')
@login_required
def get_coupons():
    return render_template('main/coupons.html', name=current_user.username)


@main.route('/api/coupons_data', methods=['GET'])
def all_coupon():
    current_date = datetime.utcnow()
    coupons = Coupon.objects(valid=True)
    expired_coupons = Coupon.objects(valid_to__lt=current_date)
    serialized_coupons = []
    for coupon in coupons:
        formatted_date = coupon.valid_to.strftime("%d %b %Y")
        coupon_usage_count = CouponUsage.objects(coupon= coupon).count()
        serialized_coupon = {
            'coupon_code': coupon.coupon_code,
            'valid': coupon.valid,
            'valid_from': coupon.valid_from,
            'valid_to': formatted_date,
            'quantity':(coupon.quantity)-coupon_usage_count,
            'usage_total':coupon_usage_count,
            '_id': str(coupon.id)
        }
        serialized_coupons.append(serialized_coupon)

    return jsonify(serialized_coupons)

@main.route('/api/usage_chart_data', methods=['GET'])
def coupons_usage_chart_data():

    result = {}
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
        9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    try:
        year = int(request.args.get('year'))
    except:
        response = {
            'message': 'Year is not selected'
            }
        return jsonify(response), 400
    counts_by_month = CouponUsage.objects(
    Q(usage_date__gte=datetime(year, 1, 1, 0, 0, 0)) &
    Q(usage_date__lt=datetime(year + 1, 1, 1, 0, 0, 0))
    ).aggregate(
        [
            {
                '$project': {
                    'month_number': {'$month': '$usage_date'},
                }
            },
            {
                '$group': {
                    '_id': '$month_number',
                    'count': {'$sum': 1},
                }
            },
            {
                '$sort': {
                    '_id': 1
                }
            }
        ]
    )
    months = []
    months_count = []
    for item in counts_by_month:
        months.append(month_names[item['_id']])
        months_count.append(item['count'])
    result['months'] = months
    result['months_count'] = months_count
    return jsonify(result)


@main.route('/api/payment_chart_data', methods=['GET'])
def payment_chart_data():
    result = {}
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
        9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    try:
        year = int(request.args.get('year'))
    except:
        response = {
            'message': 'Year is not selected'
            }
        return jsonify(response), 400
    pipeline = [
        {
            '$match': {
                'payment_date': {
                    '$gte': datetime(year, 1, 1, 0, 0, 0),
                    '$lt': datetime(year + 1, 1, 1, 0, 0, 0)
                }
            }
        },
        {
            '$group': {
                '_id': {
                    'month': {'$month': '$payment_date'},
                },
                'total_amount': {'$sum': '$amount'}
            }
        },
        {
            '$sort': {
                '_id.month': 1
            }
        }
    ]
    payment_by_month = list(Payment.objects.aggregate(*pipeline))
    months = []
    ttl_amount_month = []
    for item in payment_by_month:
        months.append(month_names[item['_id']['month']])
        ttl_amount_month.append(item['total_amount'])
    result['months'] = months
    result['total_amount'] = ttl_amount_month
    return jsonify(result)