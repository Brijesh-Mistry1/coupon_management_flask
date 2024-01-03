from ..models.models import User, Payment
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_user, login_required, current_user
from decouple import config
import shortuuid

payment = Blueprint('payment',__name__)

@payment.route('/api/save_payment', methods=['POST'])
def store_payment():
    email = request.form['user_email']
    first_name = request.form['first_name']
    username = first_name
    if request.form['last_name']:
        username = first_name + ' ' + request.form['last_name']
    mobile_number = request.form.get('phone')
    isd_number = request.form.get('country_code')
    amount = request.form.get('amount')
    transaction_id = request.form.get('charge_id')
    customer_id = request.form.get('customer_id')
    db_user_id = request.form.get('user_id') or shortuuid.ShortUUID().random(length=24)
    try:
        amount = float(amount)
    except:
        response = {
            'message': 'المبلغ غير صالح' # invalid amount.
            }
        return jsonify(response), 400
    payment_date_string = request.form['payment_date']
    try:
        payment_date = datetime.strptime(payment_date_string, "%Y-%m-%d %H:%M:%S")
    except:
        response = {
            'message': 'أدخل التاريخ غير صالح' # Invalid date enter.
            }
        return jsonify(response), 400
    payment_method = request.form['payment_method']
    status = True if request.form['payment_status'].lower() == 'success' else False


    user_obj = User.objects(email=email).first()
    if not user_obj:
        try:
            user_obj = User(username=username, email=email, db_user_id=db_user_id)
            if customer_id:
                user_obj.customer_id = customer_id
            if mobile_number:
                user_obj.mobile_number = mobile_number
            if isd_number:
                user_obj.isd_number = isd_number
            user_obj.save()
        except:
            response = {
            'message': 'عنوان بريد إلكتروني غير صالح' # Invalid email address.
            }
            return jsonify(response), 400
    else:
        if not user_obj.customer_id:
            user_obj.customer_id = customer_id
            user_obj.save()

    payment_obj = Payment(user=user_obj, amount=amount, payment_date=payment_date, status=status, transaction_id=transaction_id)

    if payment_method:
        payment_obj.payment_method = payment_method
    if customer_id:
        payment_obj.customer_id = customer_id

    try:
        payment_obj.save()
    except:
        response = {
            'message': 'حدث خطأ ما أثناء حفظ كائن الدفع' # An error occurred while saving the payment object.
            }
        return jsonify(response), 400
    response = {
            'message': 'Success'
            }
    return jsonify(response), 200


@payment.route('/api/pre_payment_data', methods=['GET'])
def pre_payment_data():
    response = {}
    response['data'] = {}
    response['data']['keys'] = {}
    response['data']['customer'] = {}
    response['data']['paymentsitems'] = {}
    email = request.args.get('email')
    user_obj = User.objects(email=email).first()

    if not user_obj:
        first_name = request.args.get('first_name') or ''
        last_name = request.args.get('last_name') or ''
        db_user_id = request.args.get('user_id') or shortuuid.ShortUUID().random(length=24)
        user_obj = User.objects.create(username=first_name+last_name, email=email, db_user_id=db_user_id)
        # response = {
        #     'message': 'failure', # Invalid email address.
        #     'data' : 'User with this email not found',
        #     'success': False
        #     }
        # return jsonify(response), 400

    username = user_obj.username
    first_name = username.split(' ')[0]
    last_name = ''
    if len(username.split(' ')) > 1:
        last_name = username.split(' ')[1]
    response['data']['amount'] = 10.0
    response['data']['keys']['androidTestKey'] = config('androidTestKey')
    response['data']['keys']['redirectUrl'] = config('redirectUrl')
    response['data']['keys']['androidProductionKey'] = config('androidProductionKey')
    response['data']['keys']['iosTestKey'] = config('iosTestKey')
    response['data']['keys']['iosProductionKey'] = config('iosProductionKey')
    response['data']['keys']['androidBundleId'] = config('androidBundleId')
    response['data']['keys']['iosBundleId'] = config('iosBundleId')
    response['data']['keys']['isSandbox'] = True if config('isSandbox').lower() == 'true' else False

    response['data']['customer']['customerId'] = user_obj.customer_id
    response['data']['customer']['email'] = user_obj.email
    response['data']['customer']['isdNumber'] = user_obj.isd_number
    response['data']['customer']['firstName'] = first_name
    response['data']['customer']['middleName'] = ''
    response['data']['customer']['lastName'] = last_name
    response['data']['customer']['mobileNumber'] = user_obj.mobile_number

    response['data']['paymentsitems']['name'] = ''
    response['data']['paymentsitems']['totalAmount'] = 10.0
    response['data']['paymentsitems']['amountPerUnit'] = 10.0
    response['data']['paymentsitems']['quantity'] = 1
    response['data']['paymentsitems']['discount'] = 0.0
    response['data']['paymentsitems']['description'] = ''
    response['message'] = 'success'
    response['success'] = True

    return jsonify(response), 200