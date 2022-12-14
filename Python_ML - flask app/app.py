# Flask Packages
from flask import Flask,render_template,request
from flask_bootstrap import Bootstrap 
from flask_uploads import UploadSet,configure_uploads,ALL


from werkzeug.utils import secure_filename
import os
import datetime
import time


# EDA Packages
import pandas as pd 


# ML Packages
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC





app = Flask(__name__)
Bootstrap(app)


# Configuration for File Uploads
files = UploadSet('files',ALL)
app.config['UPLOADED_FILES_DEST'] = 'static/uploadsDB'
configure_uploads(app,files)



#--------I want to add it but still in dev --------

# from flask_sqlalchemy import SQLAlchemy 
# db = SQLAlchemy()
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///static/uploadsDB/filestorage.db'

# Saving Data To Database Storage                

# class FileContents(db.Model):
# 	id = db.Column(db.Integer,primary_key=True)
# 	name = db.Column(db.String(300))
# 	modeldata = db.Column(db.String(300))
# 	data = db.Column(db.LargeBinary)
		
# Saving Results of Uploaded Files  to Sqlite DB
# newfile = FileContents(name=file.filename,data=file.read(),modeldata=msg)
# db.session.add(newfile)
# db.session.commit()		

#--------------======--------------

@app.route('/')
def index():
	return render_template('index.html')

# Route for our Processing and Details Page
@app.route('/dataupload',methods=['GET','POST'])
def dataupload():
	if request.method == 'POST' and 'csv_data' in request.files:
		file = request.files['csv_data']
		filename = secure_filename(file.filename)
		# os.path.join is used so that paths work in every operating system
        # file.save(os.path.join("wherever","you","want",filename))
		file.save(os.path.join('static/uploadsDB',filename))
		fullfile = os.path.join('static/uploadsDB',filename)

		# For Time
		date = str(datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S"))

		# EDA function
		df = pd.read_csv(os.path.join('static/uploadsDB',filename))
		df_size = df.size
		df_shape = df.shape
		df_columns = list(df.columns)
		df_targetname = df[df.columns[-1]].name
		df_columns[0:-1] # select all columns till last column
		df_Xfeatures = df.iloc[:,0:-1] 
		df_Ylabels = df[df.columns[-1]] # Select the last column as target
		# same as above df_Ylabels = df.iloc[:,-1]
		

		# Model Building
		X = df_Xfeatures
		Y = df_Ylabels
		
		# prepare models
		models = []
		models.append(('LR', LogisticRegression()))
		models.append(('LDA', LinearDiscriminantAnalysis()))
		models.append(('KNN', KNeighborsClassifier()))
		models.append(('CART', DecisionTreeClassifier()))
		models.append(('NB', GaussianNB()))
		models.append(('SVM', SVC()))
		# evaluate each model in turn
		

		results = []
		names = []
		allmodels = []
		scoring = 'accuracy'
		for name, model in models:
			kfold = model_selection.KFold(n_splits=10, random_state=None)
			cv_results = model_selection.cross_val_score(model, X, Y, cv=kfold, scoring=scoring)
			results.append(cv_results)
			names.append(name)
			msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
			allmodels.append(msg)
			results
			names 
			

		
	return render_template('details.html',filename=filename,date=date,
		df_size=df_size,
		df_shape=df_shape,
		df_columns =df_columns,
		df_targetname =df_targetname,
		model_results = allmodels,
		model_names = names,
		fullfile = fullfile,
		dfplot = df
		)


if __name__ == '__main__':
	app.run(host="0.0.0.0", port=8080, debug=True)