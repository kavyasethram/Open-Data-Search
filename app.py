from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from elasticsearch import Elasticsearch
from firebase import firebase
from werkzeug.utils import secure_filename
from boto.s3.key import Key
import os
import boto3
import certifi


firebase = firebase.FirebaseApplication('https://open-data-search-56086.firebaseio.com/', None)

AWS_KEY = 'AKIAIKXY2T7DXZ76XVUA'
AWS_SECRET = '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'

# s3_client = boto3.client('s3', aws_access_key_id = AWS_KEY, aws_secret_access_key = AWS_SECRET)
s3_resource = boto3.resource('s3', aws_access_key_id = AWS_KEY, aws_secret_access_key = AWS_SECRET)



es = Elasticsearch('https://search-opendatasearch-t7hkxgopq34revfqh6bgi5r4kq.us-east-2.es.amazonaws.com',
                    ca_certs=certifi.where())

app = Flask(__name__, static_folder='templates', static_url_path='')

Upload_folder = 'upload_folder'
app.config['UPLOAD_FOLDER'] = Upload_folder


@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        database_email = request.values['user_email'].replace('@', '_at_').replace('.', '_dot_')
        secure_pass = generate_password_hash(request.values['user_password'])
        signup_result = firebase.get('/Users', database_email)
        if signup_result is None:
            json_data = {'Name':request.values['user_name'],'email':request.values['user_email'],'password':secure_pass}
            firebase.patch('/Users',{database_email:json_data})
            signup_updated_result = firebase.get('/Users',database_email)
            session['auth'] = True
            session['user'] = signup_updated_result
            return redirect(url_for('upload'))
        else:
            flash('User Already Exists!')
            return redirect(url_for('login'))
    else:
        return render_template('signup.html')

@app.route("/logout")
def logout():
    session['auth'] = False
    session['user'] = None
    return redirect(url_for('home'))

@app.route('/dataset/<dataset_id>')
def dataset_page(dataset_id):
    res = es.search(index="datasets",
                    body={"query":
                              {"match":
                                   {"_id":dataset_id
                                    }
                               }
                          })
    return redirect(res['hits']['hits'][0]['_source']['Link'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        given_email = request.values['user_email']
        database_email = given_email.replace('@','_at_').replace('.','_dot_')
        login_result = firebase.get('/Users',database_email)

        if login_result!=None:
            if check_password_hash(login_result['password'], request.values['user_password']):
                session['auth'] = True
                session['user'] = login_result
                return redirect(url_for('upload'))
            else:
                flash('Invalid Username/Password')
                return render_template('login.html')
        else:
            return redirect(url_for('signup'))

    else:
        if not session.get('auth'):
            return render_template('login.html')
        else:
            flash('Already Logged In')
            return redirect(url_for('home'))



@app.route("/upload", methods=['GET','POST'])
def upload():
    if request.method == 'GET':
        if not session.get('auth'):
            return redirect(url_for('login'))
        else:
            return render_template('upload.html',user = session['user'])

    else:
        if 'file' not in request.files:
            flash('No file!')
            return redirect(request.url)
        file = request.files['file']


        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            f = file.read()
            filename = secure_filename(file.filename).split(".")
            filename = filename[0]+"_"+session['user']['email']+"."+filename[1]
            s3_resource.Object('opendatasearch',filename).put(Body = f)

            object_acl = s3_resource.ObjectAcl('opendatasearch', filename)
            response = object_acl.put(ACL='public-read')
            if str(response['ResponseMetadata']['HTTPStatusCode']) == '200':
                doc = {
                    'Name': request.values['dataset_name'],
                    'Associated_Tasks': request.values['dataset_type'],
                    'Number_of_Instances':request.values['instances'],
                    'Number_of_Attributes':request.values['attributes'],
                    'Data_Set_Information':request.values['information'],
                    'Attribute_Information':request.values['att_information'],
                    'Link':'http://opendatasearch.s3.amazonaws.com/{}'.format(filename)
                }
                res = es.index(index="datasets", doc_type='dataset', body=doc)
                flash('Upload successful!')
                return redirect(url_for('home'))

@app.route("/result", methods=['POST'])
def result():
    query = request.values['query']
    res = es.search(index="datasets",
                    body={"query": 
                                {"multi_match": 
                                    {"query": query, 
                                     "fields":["Name^2", "Associated_Tasks","Data_Set_Information", "Attribute_Information"]
                                    }
                                }
                        })
    return jsonify(res)

if __name__ == "__main__":
     app.secret_key = os.urandom(12)
     app.run()
