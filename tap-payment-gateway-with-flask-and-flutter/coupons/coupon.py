from ..models.models import User, Coupon, CouponUsage
from datetime import datetime
import random, string, shortuuid
from flask import Blueprint, request, redirect, url_for, jsonify, render_template

coupon = Blueprint('coupon',__name__)

@coupon.route('/')
def index():
    return redirect(url_for('main.get_coupons'))


@coupon.route('/api/coupon_create', methods=['POST'])
def create_coupon():
    if request.method == 'POST':
        to_date = request.form['to-date']
        quantity = request.form['quantity']
        if not to_date:
            return redirect(url_for('main.get_coupons'))
        selected_date = datetime.strptime(to_date, '%Y-%m-%d')
        coupon_code = generate_coupon_code()
        coupon = Coupon(coupon_code=coupon_code,valid_to=selected_date,quantity=quantity)
        try:
            coupon.save()
        except OverflowError as e:
            return render_template('main/coupons.html', success=False, error='Please enter feasible quantity!'), 400
        return redirect(url_for('main.get_coupons'))
    else:
        response = {
            'message': 'يُسمح فقط بطريقة النشر' # Only POST method allowed.
        }
        return jsonify(response), 405


def generate_coupon_code(length=8):
    characters = string.ascii_uppercase + string.digits
    coupon_code = ''.join(random.choice(characters) for _ in range(length))
    return coupon_code


@coupon.route('/api/validate_coupon', methods=['POST'])
def coupon_validation():
    if request.method == 'POST':
        code = request.form['coupon_code']
        username = request.form['user_name']
        email = request.form['user_email']
        db_user_id = request.form['user_id'] or shortuuid.ShortUUID().random(length=24)

        user_obj = User.objects(email=email).first()
        if not user_obj:
            try:
                user_obj = User(username=username, email=email, db_user_id=db_user_id)
                user_obj.save()
            except:
                response = {
                'message': 'عنوان بريد إلكتروني غير صالح' # Invalid email address.
                }
                return jsonify(response), 400

        coupon_obj = Coupon.objects(coupon_code=code).first()
        if not coupon_obj:
            response = {
                'message': 'رمز القسيمة غير صالح' #Coupon code is not valid.
            }
            return jsonify(response), 400

        valid_to_date = coupon_obj.valid_to.replace(hour=23, minute=59, second=59, microsecond=999999)
        if datetime.now() > valid_to_date:
            response = {
                'message': 'انتهت صلاحية القسيمة' # The coupon has expired.
            }
            return jsonify(response), 400

        user_coupon_usage_obj = CouponUsage.objects(user=user_obj,coupon=coupon_obj).first()
        if user_coupon_usage_obj:
            response = {
                'message': 'هذه القسيمة مستخدمة بالفعل في حسابك' # This coupon has already been used on your account.
            }
            return jsonify(response), 400

        coupon_usage_count = CouponUsage.objects(coupon=coupon_obj).count()
        if coupon_usage_count >= coupon_obj.quantity:
            coupon_obj.valid = False
            coupon_obj.save()
            response = {
                'message': "تم الوصول إلى حد استخدام القسيمة" # The coupon usage limit has been reached.
            }
            return jsonify(response), 400

        coupon_usage_entry = CouponUsage(user=user_obj,coupon=coupon_obj)
        coupon_usage_entry.save()

        response = { 'message': 'success' }
        return jsonify(response), 200
    else:
        response = {
            'message': 'يُسمح فقط بطريقة النشر' # Only POST method allowed.
        }
        return jsonify(response), 405
