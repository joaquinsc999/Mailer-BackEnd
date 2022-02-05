from flask import Blueprint, request, current_app, g
from .db import get_db
from flask_cors import cross_origin
import sendgrid
from sendgrid.helpers.mail import *

bp = Blueprint('mail', __name__, url_prefix='/mails')

@bp.route('/', methods=['GET'])
def index():

    db, c = get_db()

    c.execute('select * from email')

    result = c.fetchall()

    return {
        'data': result
    }

@bp.route('/upload', methods=['POST'])
@cross_origin(supports_credentials=True)
def upload():
    db, c = get_db()

    email = request.get_json()['email']
    subject = request.get_json()['subject']
    content = request.get_json()['content']

    

    if (email and subject and content):

        send(email, subject, content)
        
        sql = 'insert into email (email, subject, content) values (%s, %s, %s)'
        values = (email, subject, content)
        c.execute(sql, values)
        db.commit()

        return {
            'msg': 'Success'
        }
    
    return  {
        'msg': 'ERROR: Some values were blank'
    }
    

def send(to, subject, content):
    print(current_app.config['SENDGRID_KEY'])
    sg = sendgrid.SendGridAPIClient(api_key=current_app.config['SENDGRID_KEY'])
    from_email = Email(current_app.config['FROM_EMAIL'])
    to_email = To(to)
    content_email = Content('text/plain', content)
    mail = Mail(from_email, to_email, subject, content_email)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response)


@bp.route('/search', methods=['POST'])
def search():
    db, c = get_db()
    thingToSearch = request.get_json()['thingToSearch']
    if thingToSearch:
        c.execute('SELECT * from email where content like %s', ('%' + thingToSearch + '%',))
    else:
        c.execute('SELECT * from email')

    mails = c.fetchall()

    return {
        'data': mails
    }
