from flask_mongoengine import MongoEngine, Document
from flask_login import UserMixin
from mongoengine import StringField, DateTimeField, ReferenceField, FloatField, EmailField, BooleanField, IntField
from datetime import datetime

class User(UserMixin,Document):
    username = StringField()
    customer_id = StringField()
    email = EmailField(unique=True,required=True)
    db_user_id = StringField(required=True)
    mobile_number = StringField()
    isd_number = StringField()
    password = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    def __str__(self):
        return self.username

    def to_json(self):
        return {"name": self.name,
                "email": self.email}

class Coupon(Document):
    coupon_code = StringField(unique=True)
    valid_from = DateTimeField(default=datetime.utcnow)
    valid_to = DateTimeField(required=True)
    valid = BooleanField(default=True)
    quantity = IntField(default=True)

    def __str__(self):
        return self.coupon_code


class CouponUsage(Document):
    user = ReferenceField('User',required=True)
    coupon = ReferenceField('Coupon',required=True)
    usage_date = DateTimeField(default=datetime.utcnow)

    def __str__(self):
        return self.user.username + '-' + self.coupon.coupon_code

class Payment(Document):
    status = BooleanField(required=True)
    user = ReferenceField('User',required=True)
    customer_id = StringField()
    payment_date = DateTimeField(required=True)
    amount = FloatField(required=True)
    payment_method = StringField()
    transaction_id = StringField(required=True)
    def __str__(self):
        return self.user.username + ':' + self.amount