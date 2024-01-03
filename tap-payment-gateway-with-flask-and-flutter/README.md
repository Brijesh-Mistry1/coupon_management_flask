
## Tap Payment with Flask and Flutter

The Admin Dashboard for Coupon Management and Payment Tracking is a versatile web application built using Flask, MongoDB, and the MongoEngine ODM (Object-Document Mapper). It provides a robust solution for businesses to efficiently manage coupons, record payment transactions, and analyze coupon usage data.




## Features

- Coupon Creation: Easily create coupons by defining expiry date.
- Payment Recording: Record payment transactions, including customer information, transaction amount, date, and payment method.
- Coupon Usage Tracking: Monitor coupon usage in real-time. Gain insights into which coupons are popular, and their impact on sales.

## Installation

#### Create the project Directory and navigate there

```bash
  mkdir tap_payment_project

  cd tap_payment_project
```

#### Installing with virtualenv

Create virtualenv for python3.6

```bash
  python3.6 -m venv env

  . env/bin/activate
```

Clone the project

```bash
  git clone -b master https://gitlab.codetrade.io/python-projects/tap-payment-gateway-with-flask-and-flutter.git
```
Install dependencies

```bash
  cd tap-payment-gateway-with-flask-and-flutter #navigate to project directory

  pip install -r requirements.txt
```

Required Installaliation

```bash
  Please make sure that hou have installed mongoshell inside your system.

```

Export flask app

```bash
  cd .. # Go back to parent directory for running the flask app
  export FLASK_APP=tap-payment-gateway-with-flask-and-flutter
```



Start the server

```bash
  flask run
```
    
## Environment Variables

To run this project, you will need to add .env file in project directory and need to add the following environment variables to your .env file

`DATABASE_NAME`

`DATABASE_HOST`

`DATABASE_PORT`

`SECRET_KEY`

