from flask import Flask, render_template, url_for, redirect, request
from flask_wtf import Form
from wtforms import FileField, SelectField, SubmitField
import os
from werkzeug import secure_filename
from webui import WebUI
import json
import csv
from return_keyphrases import *
from bs4 import BeautifulSoup
import requests
import urllib.parse

app = Flask(__name__)
ui = WebUI(app, debug=True)
app.config['SECRET_KEY'] = 'hackathon'
data_file = 'data.json'

def read_data(f):
	with open(f, 'r') as df:
		return json.loads(df.read())
def dump_data(f, d):
	with open(f, 'w') as df:
		json.dump(d, df, indent=4)

def fetch_first_url(query):
	urlquery = urllib.parse.quote(query)
	page = requests.get("https://www.google.com/search?"+urlquery)
	if(page.status_code==200):
		soup = BeautifulSoup(page.content, "html.parser")
		h3 = soup.find("h3",class_="LC20lb")
		a = h3.parent
		return a["href"]

class UploadForm(Form):
	file = FileField('Txt File')

class SubmitForm(Form):
	button = SubmitField('Save Cache')



@app.route('/', methods=['GET', 'POST'])
def index():
	data = read_data(data_file)
	upload_form = UploadForm()
	save_cache = SubmitForm()

	if upload_form.validate_on_submit() and upload_form.file.data:
		filename = secure_filename(upload_form.file.data.filename)
		upload_form.file.data.save('files/{}'.format(filename))
		data = read_data(data_file)
		data.append(filename)
		dump_data(data_file, data)
	if save_cache.validate_on_submit():
		f = str(data_file[0])
		directory = '../files/{}'.format(f)
		phrases = keyphrases(f)
		for phrase in phrases:
			url = fetch_first_url(phrase)
			print(url)
			r = requests.get(url, allow_redirects=True)
			open('site' + str(phrase), 'wb').write(r.content)
	
	return render_template('index.html', upload_form=upload_form, data=data, save_cache=save_cache)



if __name__ == '__main__':
	ui.run()

