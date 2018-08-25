import csv
import json
import random
import string

# import pythoncom
# import win32com.client as win32
# from bokeh.embed import components
from flask import render_template, jsonify, Response
from flask import request, make_response

from app import db
# from app.main.plots import vertical_bar_chart_from_data_frame2
from app.models import User, Project, Email
from config import basedir
from . import main

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import pandas as pd
import numpy as np
import os
import secrets


@main.route('/')
def index():
    assets_img = os.path.join(os.path.sep, basedir, 'app', 'static', 'img', 'carousel')
    image_urls = os.listdir(assets_img)
    im = [os.path.join(os.path.sep, 'static', 'img', 'carousel', img) for img in image_urls]
    captions = ['Welcome to my webapp', 'I studied at the Technical University of Crete.',
                'My home is Ikaria, the island were people forget to die.']
    return render_template('boot_studio/landing_page.html', image_urls=im, captions=captions)


def gallery(location='static/img/gallery'):
    gallery_categories = os.path.join(os.path.sep, basedir, 'app', *location.split('/'))

    categories = os.listdir(gallery_categories)
    # remove json
    categories = [category for category in categories if '.json' not in category]
    images_full_path = []
    for category in categories:
        images = os.path.join(os.path.sep, basedir, 'app', *location.split('/'), category)
        for image in os.listdir(images):
            image_path = os.path.join(*location.split('/'), category, image)
            images_full_path.append([category, image_path])
    return categories, images_full_path, os.path.join(os.path.sep, gallery_categories, 'hrefs.json')


@main.route('/projects')
def projects():
    categories, images_full_path, hrefs = gallery()
    with open(hrefs) as f:
        data = json.load(f)
    urls = []
    names = []
    for category in categories:
        for image in images_full_path:
            # cat = data[category.lower()]
            if category in image:
                image_file_name = image[1].split(os.path.sep)[-1]
                url = data[category][image_file_name]['url']
                name = data[category][image_file_name]['name']
                urls.append(url)
                names.append(name)

    return render_template('boot_studio/projects.html', categories=categories, images_full_path=images_full_path,
                           hrefs=urls, names=names)


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# @main.route('stats')
# def general_stats():
#     items = [list(row2dict(result).values()) for result in db.session.query(Project).all()]
#     # print(request.method)
#     params = ['project_title', 'year_1', 'year_2', 'year_3', 'year_4', 'year_5', 'justification', 'comments']
#
#     fields = params[:]
#     fields.insert(0, 'id')
#     data = pd.DataFrame(items, columns=fields)
#     # print(data.head())
#     nans = np.round(data.isnull().sum() / data.shape[0], 2).to_frame()
#     nans.columns = ['Percent']
#     plot = vertical_bar_chart_from_data_frame2(nans, column='Percent', title='test')
#     script, div = components(plot)
#     feature_names = nans.index.values.tolist()
#     return render_template("main/basic_analysis.html", script=script, div=div, feature_names=feature_names)


# @main.route('/table1', methods=['GET', 'POST'])
# def table1():
#     name = "Suez Budget Data Collection"
#     model = 'project'
#     items = [list(row2dict(result).values()) for result in db.session.query(Project).all()]
#     # print(request.method)
#     params = ['project_title', 'year_1', 'year_2', 'year_3', 'year_4', 'year_5', 'justification', 'comments']
#
#     fields = params[:]
#     fields.insert(0, 'id')
#     try:
#         data = pd.DataFrame(items, columns=fields)
#         # print(data.head())
#         nans = np.round(data.isnull().sum() / data.shape[0], 2).to_frame()
#         nans.columns = ['Percent']
#         plot = vertical_bar_chart_from_data_frame2(nans, column='Percent', title='test')
#         script, div = components(plot)
#     except:
#         script, div = None, None
#
#     if request.method == 'POST':  # this block is only entered when the form is submitted
#         project_id = request.args.get('project_id', None, int)
#         project_create_update(params, project_id)
#     return render_template('main/index.html', headers=fields, script=script, div=div, name=name, model=model)
#     # else:
#     #     return render_template('main/index.html', headers=fields, script=script, div=div)


def project_create_update(params, project_id):
    if isinstance(project_id, int):
        project = Project.query.get(project_id)
    else:
        project = Project()
    print('project_id', project_id)
    print('POST: ')
    # project = Project()
    fields = []
    for param in params:
        field = request.form.get(param, None)
        if not field:
            field = None
        fields.append(field)
    if all(f is None for f in fields):
        pass
    else:
        # https://stackoverflow.com/questions/3253966/python-string-to-attribute
        project.project_title = fields[0]
        project.year_1 = fields[1]
        project.year_2 = fields[2]
        project.year_3 = fields[3]
        project.year_4 = fields[4]
        project.year_5 = fields[5]
        project.justification = fields[6]
        project.comments = fields[7]
        if isinstance(project_id, int):
            db.session.commit()
        else:
            db.session.add(project)
            db.session.commit()


from flask_datatables import utils


def row2dict(row):
    """Given a row, it returns a dict."""
    d = {}
    for column in row.__table__.columns:
        d[column.name] = getattr(row, column.name)
    return d


@main.route('/get_data/<string:table>')
def get_data(table):
    if table == "project":
        model = Project
    elif table == "email":
        model = Email
    items = [list(row2dict(result).values()) for result in db.session.query(model).all()]
    return jsonify(items=items)


@main.route('/update_email_token', methods=['POST'])
def update_email_tokens():
    for email in Email.query.all():
        # email = Email.query.get(row2dict(row)['id'])
        email.token = secrets.token_hex(16)
        db.session.commit()
    return jsonify(status='ok')


@main.route('/email', methods=['GET', 'POST'])
def email():
    return utils.render_table(session=db.session, model=Email)


# @csrf.exempt
@main.route('/delete_data/<string:table>/<int:param>', methods=['DELETE'])
def delete_data(table, param):
    if table == "project":
        model = Project
    elif table == "email":
        model = Email
    project = model.query.filter_by(id=param).first()
    db.session.delete(project)
    db.session.commit()
    return jsonify(status=True)


@main.route('login')
def add_user():
    user = User(email=id_generator(), username=id_generator())
    db.session.add(user)
    db.session.commit()
    return render_template('main/index.html')


def randString():
    return ''.join(random.choice())


@main.route('/download', methods=['GET'])
def download():
    items = [list(row2dict(result).values()) for result in db.session.query(Project).all()]
    si = StringIO()
    cw = csv.writer(si)
    cw.writerows(items)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output


# @main.route('/send_emails', methods=['POST'])
# def send_emails():
#     pythoncom.CoInitialize()
#     outlook = win32.Dispatch('outlook.application')
#     items = [email for email in db.session.query(Email).all()]
#     domain = '127.0.0.1:5000'
#     for email in items:
#         mail = outlook.CreateItem(0)
#         mail.To = email.email
#         mail.Subject = 'Budget Login links Testing Web App'
#         mail.Body = 'Message body'
#         mail.HTMLBody = '<h2>{0}?token={1}</h2>'.format(domain, email.token)  # this field is optional
#
#         mail.Send()
#     # def generate():
    #     x = 0
    #     for i in range(10):
    #         print('SENDING')
    #         print((i/100)*100)
    #         email = items[i]
    #         print(email.email)
    #         x=x+100
    #         # yield "data:" + str(x) + "\n\n"
    #         # mail = outlook.CreateItem(0)
    #         # mail.To = email.email
    #         # mail.Subject = 'Budget Login links'
    #         # mail.Body = 'Message body'
    #         # mail.HTMLBody = '<h2>{0}</h2>'.format(email.token) #this field is optional
    #         # # To attach a file to the email (optional):
    #         # # attachment  = "Path to the attachment"
    #         # # mail.Attachments.Add(attachment)

    #         # mail.Send()
    #         time.sleep(0.5)

    #         return "data:" + str(x) + "\n\n"

    # return Response(generate(), mimetype= 'text/event-stream')
    return jsonify(status='ok')


import time


@main.route('/progress')
def progress():
    def generate():
        x = 0
        while x <= 100:
            yield "data:" + str(x) + "\n\n"
            x = x + 10
            time.sleep(0.5)

    return Response(generate(), mimetype='text/event-stream')

# # @main.route('/send_emails', methods = ['GET','POST'])
# @main.route('/progress', methods = ['GET','POST'])
# def progress2():
#     # emails = [email for email in db.session.query(Email).all()]
#     # import pythoncom
#     # pythoncom.CoInitialize()
#     # import win32com.client as win32
#     # outlook = win32.Dispatch('outlook.application')
#     def generate():
#         # emails = [email for email in db.session.query(Email).all()]

#         x = 0
#         n=0
#         while x <= 100:
#             yield "data:" + str(x) + "\n\n"

#             # if n-1==len(emails):
#             #     pass
#             # else:
#             #     email=emails[n]
#             #     print(email)
#             #     mail = outlook.CreateItem(0)
#             #     mail.To = email.email
#             #     mail.Subject = 'Budget Login links'
#             #     mail.Body = 'Message body'
#             #     mail.HTMLBody = '<h2>{0}</h2>'.format(email.token) #this field is optional
#             #     # # To attach a file to the email (optional):
#             #     # # attachment  = "Path to the attachment"
#             #     # # mail.Attachments.Add(attachment)

#             #     mail.Send()
#             #     print('EMAIL')
#             x = x + 10
#             time.sleep(0.5)
#             n+=1

#     return Response(generate(), mimetype= 'text/event-stream')
