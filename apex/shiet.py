
import flask
from flask import Flask , request , render_template , redirect , url_for,session , Markup
import markupsafe
from flask import sessions
import markupsafe
from werkzeug.utils import redirect
import wtforms
import gridfs
from wtforms import FileField , StringField,Form , validators , TextAreaField
from pymongo import MongoClient
from flask_wtf import FlaskForm
import base64
from bson.binary import Binary
from werkzeug.utils import secure_filename
import os
url = "localhost:27017"
client = MongoClient(url)
database = client['Kip']
coll =database['pics']
fs = gridfs.GridFS(database)
application = Flask(__name__)
    
upload_folder = 'static/images'
application.config['UPLOAD_FOLDER'] = upload_folder
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])



user = "jack"

@application.route('/' , methods = ["POST" , "GET"])
def home():
    if request.method == "POST":
        if "img" in request.files:
            
        
            name = request.form['name']    
        
            pic = request.files['img']
            
            filename = pic.filename
            def allowed_file(filename):
                return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
            
            if allowed_file(filename):
                
                
                pic.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
                
                image = upload_folder +  "/" + filename
                
                #with open(image, "rb") as f:
                    #encoded = Binary(f.read())
                
                with open(image , "rb") as image2string:
                    converted_string = base64.b64encode(image2string.read())
                    
                    uploa = converted_string.decode('utf-8')
                    

                
                coll.insert_one({"filename" : filename , "image" : uploa , "name" : name , "owner" : user})
                
                os.remove(image)
         
            
            #fs.put(datas, filename = name)
            #return redirect(url_for('view_pic'))
    
    
    return render_template("add_pic.html")

@application.route('/get_em/' , methods = ["POST" , "GET"])
def get_em():
    the_image = coll.find_one({"name" : "yeah"})
    bina = the_image['image']
    name = the_image['name']
    user = "/" + "jack"
    new_name = name
    filename = new_name + ".jpg"
    def query():
        os.mkdir(upload_folder + user)
        my_folder = upload_folder + user
        decodeit = open(my_folder + "/" + new_name + ".jpg", 'wb')
        image_folder = os.path.join(my_folder ,  filename )
        decodeit.write(base64.b64decode((bina)))
        decodeit.close()
        return filename
    query()
    
    return redirect(url_for('view_pic'))

@application.route('/view_pic/')
def view_pic():
    the_image = coll.find_one({"name" : "yeah"})
    bina = the_image['image']
    name = the_image['name']
    user = "/" + "jack"
    new_name = name
    filename = new_name + ".jpg"
    imga = str("images" + user +  "/"+ filename)

    viiii = str("static/images" + user + "/" + filename)
    
    vr = Markup("{{ url_for('static', filename='images/jack/yeah.jpg') }}")
    
    vr2 = Markup(viiii)
    
    return render_template("view_pic.html")

@application.route('/view_basic')
def view_basic():
    
    line2 = "/static/images/jack/yeah.jpg"
    
    
    
    return render_template("view_basic.html"  , line = line2)

if __name__ == '__main__':
    application.secret_key == "wassupmfsdsgf"    
    application.run(debug = True  , port = 5001)
