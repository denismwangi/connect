import base64
from email import message
from dns.message import Message
from flask import Flask, render_template, url_for, request, redirect,flash,session
from flask.scaffold import F
from flask_pymongo import PyMongo
from flask_wtf.form import FlaskForm
from pymongo import MongoClient
import passlib
from passlib.context import CryptContext
from passlib.hash import bcrypt_sha256,argon2,ldap_salted_md5,md5_crypt
import time
from datetime import timedelta
import smtplib
from email.message import EmailMessage
import socket,os
from functools import wraps
from gridfs import*
from bson import ObjectId
from flask_recaptcha import ReCaptcha
from flask_wtf import RecaptchaField,FlaskForm
from wtforms import *
from wtforms.validators import EqualTo, InputRequired
from flask_wtf.csrf import CSRFProtect, CsrfProtect
from wtforms.csrf.session import SessionCSRF 
from datetime import timedelta
import email_validator 
import random
#from flask_mail import Mail,Message
import base64
from bson.binary import Binary
from werkzeug.utils import secure_filename
#mpsa imports
#from flask_mpesa import MpesaAPI

ip = socket. gethostbyname(socket. gethostname())
ipst = str(ip)
application = Flask(__name__)

#mpesa configs
#mpesa_api = MpesaAPI(application)
application.config["API_ENVIRONMENT"] = "sandbox"
application.config["APP_KEY"] = "..." 
application.config["APP_SECRET"] = "..." 


#images
upload_folder = 'static/images'
application.config['UPLOAD_FOLDER'] = upload_folder
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

#recaptcha configs
recaptcha = ReCaptcha(application = application)
application.config['RECAPTCHA_PUBLIC_KEY'] =  "6Lf2-MIaAAAAAKhR8vc-wUo6PyWIXtevEN3R7HpY"
application.config['RECAPTCHA_PRIVATE_KEY'] = "6Lf2-MIaAAAAACzF1Nmhmq0dGEGdf9jQJyIqOEmS"
application.config['RECAPTCHA_DATA_ATTRS'] = {'theme': 'dark'}
application.config['TESTING'] = True
#csrf protection
csrf = CSRFProtect(application)
application.config['WTF_CSRF_SECRET_KEY'] = 'edfdfgdfgdfgfghdfggfg'
SECRET_KEY = "dsfdsjgdjgdfgdfgjdkjgdg"
SECRET = "secret"

#mongoDB configs
application.config['MONGO_DBNAME'] = 'users'
# application.config['MONGO_URI'] = 'mongodb://'+ipst+':27017/users'
application.config['MONGO_URI'] = 'mongodb://localhost:27017/users'

mongo = PyMongo(application)


#FlaskMailConfigs

application.config['MAIL_SERVER'] = "smtp.gmail.com"
application.config['TESTING'] = True
application.config['MAIL_PORT'] = 465
application.config['MAIL_USE_TLS'] = False
application.config['MAIL_USE_SSL'] = True
application.config['MAIL_DEBUG'] = True
application.config['MAIL_USERNAME']  = "jacksonmuta123@gmail.com"
application.config['MAIL_PASSWORD'] =  "aqlxhzaziujnllzi"
application.config['MAIL_DEFAULT_SENDER'] = "Reset Password Server "
application.config['MAIL_SUpplicationRESS_SEND'] = False
application.config['MAX_EMAIL'] = None
application.config['MAIL_ASCII_ATTATCHMENTS'] = False

#Post_guy = Mail(application)


client = MongoClient('localhost', 27017)
db_pic = client.users
gfs = GridFS(db_pic)






#'mongodb://'+ipst+':27017/kamp_users'
#'mongodb://localhost:27017/kamp_users'
#'mongodb+srv://jackson:@hbcall.ihz6j.azure.mongodb.net/kamp_users?retryWrites=true&w=majority'
#'mongodb://jackson:mutamuta@hbcall-shard-00-00.ihz6j.azure.mongodb.net:27017,hbcall-shard-00-01.ihz6j.azure.mongodb.net:27017,hbcall-shard-00-02.ihz6j.azure.mongodb.net:27017/kamp_users?ssl=true&replicaSet=atlas-aykvid-shard-0&authSource=admin&retryWrites=true&w=majority'
application.permanent_session_lifetime = timedelta(days=30)


Hash_passcode = CryptContext(schemes=["sha256_crypt" ,"des_crypt"],sha256_crypt__min_rounds=131072)


mongo = PyMongo(application)

users = mongo.db.users
link_db = mongo.db.links

def login_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if "login_user" in session:
            return f(*args,**kwargs,)
        else:
            time.sleep(2)
            return redirect(url_for('index'))
    return wrap


class Base_form(Form):
    
    class Meta:
        csrf = True 
        csrf_class = SessionCSRF 
        csrf_secret = "fhgfjgygkgchfjfjfdumbo"
        csrf_time_limit = timedelta(minutes=25)
        
class login_form(Base_form):
        
        email = StringField("Email",[validators.email()])
        
        passc = PasswordField("Password" , [validators.Length(min = 8 , max = 15 , message = "Minimum Length Is 8 Characters")]) 
           
@application.route('/',methods = ["POST","GET"])
@csrf.exempt
def home():
    form = login_form()
    if request.method == "POST" and form.validate():
        email = form.email.data
        existing_user  = users.find_one({'email':email} )
        if existing_user:
                passcode = form.passc.data

                existing_pass = existing_user['password']
                if Hash_passcode.verify(passcode,existing_pass):
                    username = existing_user['username']
                    if username in session:
                        fa = existing_user['tags']
                        if len(fa) < 5:
                             return redirect(url_for('choose_tags'))
                        else:
                            return redirect(url_for('main_page'))
                    else:    
                        session_time = request.form.get("session_time") 
                        if  session_time == 2:
                            session.parmanent = True
                        session['login_user'] = email
                        fa = existing_user['tags']
                        if len(fa) < 5:
                            return redirect(url_for('choose_tags'))
                        else:    
                            return redirect(url_for('main_page'))   
    return render_template("main/middle.html" , form = form)


def reset_session_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if "login_user" in session:
            return f(*args,**kwargs,)
        else:
            time.sleep(2)
            return redirect(url_for('reset_pass'))
    return wrap
@application.route('/reset_pass/', methods = ['POST','GET'])
@csrf.exempt
def  reset_pass():
    if request.method == "POST":
        email = request.form['email']
        reset_db = mongo.db.pass_reset
        
        code = random.randint(145346 , 976578)
        code = str(code)
        
        existing = users.find_one({'email':email} )
        
        if existing:
            mess = Message( "Hi Password Reset Request" , recipients = [email])
            messo = "Hi Password Reset Request"
            mess.html =  render_template("email_template.html" , code = code , mes = messo)
            Post_guy.send(mess)
            r_now = time.time()
            reset_db.insert_one({"email" : email , "code" : code , "time_in" : r_now})
            return redirect(url_for("enter_code" , email = email))
            
        else:
            return redirect(url_for('register'))
    return render_template('auth/reset_pass.html',  form = form)

@application.route('/enter_code/' , methods = ['POST','GET'])
@csrf.exempt
def enter_code(email = "jacksonmuta123@gmail.com"):
    if request.method == "POST":
        reset_db = mongo.db.reset_pass
        code = request.form['code']
        mailed = email
        legit = reset_db.find_one({"email" : email})
        if legit:
            legit_code = legit["code"]
            now = time.time()
            req_time = legit['time_in']
            diff = now - req_time
            if code == legit_code and diff < 10:
                  return redirect(url_for('new_pass' , email = mailed))
                
            if diff > 10:
                return redirect(url_for('reset_pass' ))
        else:
            return redirect(url_for('register'))
        
    return render_template('auth/enter_code.html',form=form)

class New_pass(Base_form):
      
        pass1 = PasswordField("Password" , [validators.Length(min = 8 , max = 15 , message = "Minimum Length Is 8 Characters")]) 
           
        pass2 = PasswordField("Confirm Password" , [validators.Length(min = 8,max=15 , message="8 To 15 Characters") , EqualTo("passc",message="Must Be Same To The Input Above") , InputRequired()])
        
        

@application.route('/new_pass/' , methods = ['POST','GET'])
@csrf.exempt
def new_pass(email):
    form = New_pass()
    if request.method == "POST" and form.validate():
        users = mongo.db.users
        
        target_account = email
        
        
        pass1 = form.pass1.data
        
        pass2 = form.pass2.data
        
        
        if pass1 == pass2 and len(pass2) > 8 and len(pass2) < 15 :
            
            passcode = Hash_passcode.hash(pass2)
            
            the_user = users.find_one({"email" : email})
             
            users.find_one_and_update({"email" :target_account} , { 'set' : {"password" : passcode} })
    return render_template('new_pass.html' , form = form)
class Base_form(FlaskForm):
    
    class Meta:
        csrf = True 
        csrf_class = SessionCSRF 
        csrf_secret = b"cffhgfghfgjgherydumbo"
        csrf_time_limit = timedelta(minutes=25)
        
class login_form(Base_form):
        
        email = StringField("Email",[validators.email()])
        
        passc = PasswordField("Password" , [validators.Length(min = 8 , max = 15 , message = "Minimum Length Is 8 Characters")])            
@application.route('/login/' , methods = ['POST','GET'])
@csrf.exempt
def login():
    form = login_form()
    if request.method == "POST" and form.validate():
        email = form.email.data
        existing_user  = users.find_one({'email':email} )
        if existing_user:
                passcode = form.passc.data

                existing_pass = existing_user['password']
                if Hash_passcode.verify(passcode,existing_pass):
                    username = existing_user['username']
                    if username in session:
                        fa = existing_user['tags']
                        if len(fa) < 5:
                             return redirect(url_for('choose_tags'))
                        else:
                            return redirect(url_for('main_page'))
                    else:    
                        session_time = request.form.get("session_time") 
                        if  session_time == 2:
                            session.parmanent = True
                        session['login_user'] = email
                        fa = existing_user['tags']
                        if len(fa) < 5:
                            return redirect(url_for('choose_tags'))
                        else:    
                            return redirect(url_for('main_page'))
    return render_template('auth/login.html' , form = form)


class Base_form(FlaskForm):
    
    class Meta:
        csrf = False
        csrf_class = SessionCSRF 
        csrf_secret = "dfgdfgtryfhgfhhgfhdxhd"
        csrf_time_limit = timedelta(minutes=25)
        
class register_form(Base_form):
        
        email = StringField("Email",[validators.email()])
        
        username = StringField("Username" , [validators.InputRequired(message="A Nickname or your most known Name")])
        
        passc = PasswordField("Password" , [validators.Length(min = 8 , max = 15 , message = "Minimum Length Is 8 Characters")]) 
           
        passc2 = PasswordField("Confirm Password" , [validators.Length(min = 8) , EqualTo("passc") , InputRequired()])
    
@application.route('/register/',methods = ['POST','GET'])
@csrf.exempt
def register():
    form = register_form()
    if request.method == "POST" and "img" in request.files:
        
        pic = request.files['img']
        
        email = form.email.data
        
        username =  form.username.data
        
        passc = form.passc.data
        
        passc2 = form.passc2.data
        
        hashed = Hash_passcode.hash(passc2)
        
        filename = pic.filename
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
            
        if allowed_file(filename):
            pic.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
            image = upload_folder +  "/" + filename
            with open(image , "rb") as image2string:
                converted_string = base64.b64encode(image2string.read())
                uploa = converted_string.decode('utf-8')
        registered = users.find_one({"email":email})
        if registered:
            mess = "You are already registered,please Log in"
            return redirect(url_for('home'))
        if passc == passc2  and not registered:
            mess = "Registerd Successfully" 
            favs = []
            tags = []
            users.insert_one({"email":email ,'username':username , "password":hashed , 
                            "profile" : uploa , "favs" : favs , "tags" : tags })
            if users.find_one({"email":email}):
                return redirect(url_for('home'))
    return render_template('auth/register.html',form = form)

@application.route('/main_page/' , methods = ['POST','GET'])
@csrf.exempt
def main_page():
    link_db = mongo.db.links
    user = mongo.db.users
    trending_db = mongo.db.trending
    render_array = []
    #based on following people
    user_email = session['login_user']
    the_user = users.find_one({"email" : user_email})
    favs = the_user["favs"]
    fav_arr = []
    if len(favs) <10:
        count = 2
    else:
        count = 1
    for x in favs:         
        user = x
        documentz = list(link_db.find({"owner" : user }).limit(count))
        fav_arr.extend(documentz)        
    render_array.extend(fav_arr)

    #based on tags
    my_tags = the_user["tags"]
    for y in my_tags:
        indiv_tags  = y
        #relevant = trending_db.find({"tags" : tags})
        arr1 = []
        all_posts= list(link_db.find({}))
        for x in all_posts:
            tags = x['tags']
            if indiv_tags in tags:
                if not  x in render_array: 
                    arr1.append(x)        
        render_array.extend(arr1)
        
        #like and comment methods
    #view link functionality
    if request.method == "POST":
        the_id = request.form['id']
        if request.form['sub'] == "View Link": 
            session["linky"] = the_id
            return redirect(url_for('view_link' ))
                
        if request.form['sub'] == "Like":
            the_post = link_db.find_one({"post_id" : the_id})
            likes= the_post['likes']
            total_likes = len(likes)
            clicker = session['login_user']
            if clicker in likes:
                likes.remove(clicker)
                link_db.find_one_and_update({"post_id" : the_id} ,{ '$set' :  {"likes": likes}} )
                b_color = "red"
            else:
                likes.append(clicker) 
                link_db.find_one_and_update({"post_id" : the_id} ,{ '$set' :  {"likes": likes}} )
                b_color = "less" 
                
        if request.form['sub'] == "Comment":
            the_post = link_db.find_one({"post_id" : the_id})
            comments = the_post['comments']
            
              
            
    return render_template('main/middle.html' , arr = render_array , email = user_email)

@application.route('/profile/' , methods = ['POST','GET'])  
@csrf.exempt
def profile():
    me = session['login_user']
    the_arr = ["electric car" , "rap" , "football"]
    acc = users.find_one({"email" : me})
    favs = acc['favs']
    tags = acc['tags']
    user = acc['username']
    profile_pic = acc['profile']
    name = me
    new_name2 = "/" +  name
    new_name = name
    os.mkdir(upload_folder  + new_name2)
    my_folder = upload_folder + new_name2
    filename = new_name + ".jpg"
    def create_image():
        decodeit = open(my_folder + "/" + new_name + ".jpg", 'wb')
        image_folder = os.path.join(my_folder ,  filename )
        decodeit.write(base64.b64decode((profile_pic)))
        decodeit.close()
    create_image()        
    imga = str(my_folder + "/"+ filename)
    
    if request.method == " POST":
        tag = request.form['sub']
        tag = tag.lower()
        all_posts= list(link_db.find({})).limit(1000)
        for x in all_posts:
            tags = x['tags']
            if tag in tags:
                the_arr.append(x)
                
            #users.find_one_and_update({"email" : me} ,{ '$set' :  {"on_tags" : the_arr}})      
            return redirect(url_for('post_on_tags' , arr = the_arr , tag = tag))
    
    return render_template('profile.html' , me = me , favs = favs , tags = tags)

@application.route('/post_on_tags/' , methods = ['POST','GET'])
@csrf.exempt
def post_on_tags():
    
    
    return render_template('post_on_tags.html')
@application.route('/view_link/' , methods = ['POST','GET'])
@csrf.exempt
def view_link():
    link = session['linky']
    link_db = mongo.db.links
    render_arr = []
    all_posts = list(link_db.find({}))
    post_in = link_db.find({"post_id" : link})
    post_in_2 =  link_db.find_one({"post_id" : link})
    post_tags = post_in_2['tags']
    for k in post_tags:
        em_tags = k
        for x  in all_posts:
            tags = x['tags']
            if em_tags in tags:
                if x in render_arr:
                    pass
                else:
                    render_arr.append(x)
    return render_template('view_link.html' , taged = render_arr ,  item = post_in , link = link)

@application.route('/advert/' , methods = ['POST','GET'])
@csrf.exempt
def advert():
    advert_db = mongo.db.adverts 
    if request.method == "POST":
        
        title = request.form['title']
        
        description = request.form['description']

        pic = request.files['img']
        
        plan = request.form.get("plan")
        if plan == "1":
            the_plan = "two_dollar"
        if plan == "2":
            the_plain = "five_dollar"
        if plan == "3":
            the_plan  = "12_dollar"
        if plan == "4":
            the_plain = "fifty_dollar"
        
        filename = secure_filename(pic.filename)
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS       
        if allowed_file(filename):
            pic.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
            image = upload_folder +  "/" + filename
            with open(image , "rb") as image2string:
                converted_string = base64.b64encode(image2string.read())
                uploa = converted_string.decode('utf-8')        
        advert_db.insert_one({"title" : title , "desc" : description , "ad_pic" : uploa , 
                             "plan" : the_plain })        
    
    return render_template('ads/advert.html')
@application.route('/mpesa/' , methods = ['POST','GET'])
def mpesa():
    
    
    
    
    
    return render_template('mpesa.html')




@application.route('/transact/b2b')
def b2b_transact():
    data={"initiator": "[Initiator]",
            "security_credential": "[SecurityCredential]",#from developers portal
            "amount": "1000",
            "command_id":"[command_id]",
            "sender_identifier_type":"[SenderIdentifierType]",
            "receiver_identifier_type":"[ReceiverIdentifierType]",
            "party_a": "[PartyA]",
            "party_b": "[PartyB]",
            "remarks": "[Remarks]",
            "queue_timeout_url": "YOUR_URL" ,
            "result_url": "YOUR_URL",
            "account_reference": "[AccountReference]"
    }
    mpesa_api.B2B.transact(**data)  # ** unpacks the dictionary



main_class = [
    "Science And Technology",
    "Celebrities And Gossip",
    "Vaccation , Wildlife and Earth",
    "Mortage , Property And House Items",
    "Investments And Business",
    "Relationships , Marriage and Parenting",
    "Health And Nutrition" ,
    "Agriculture and Food Security",
    "Sports"
    "Entertainment"
    ]
    
tech =[
"TECHNOLOGY",
"Computing Information Technology", 
"Medical Technology And Equipment" ,
"Communications Technology" ,
"Industrial and Manufacturing Technology" ,
"Education Technology" ,
"Construction Technology" ,
"Aerospace Technology" ,
"Biotechnology" ,
"Agriculture Technology" ,
"Electronics Technology" ,
"Military Technology" ,
"Robotics Technology" ,
"Artificial Intelligence Technology" ,
"Assistive Technology" ,
"Entertainment Technology" ,
"Sports Technology" ,
"Vehicle Technology" ,
"Environmental Technology" ,
"3D Printing Technology" ,
    
]

enta =[
"ENTERTAINMENT",
"Movies and TV shows",
"Video Games",
"Books",
"Comedy,Circus and theater",
"Concerts",
"Travel And Road Trips",
"Music",
"Gambling",
"Boeard Games",
"Children Content"
    
]

sports = [
"SPORTS",
"MotorSports",
"FootBall",
"Boxing",
"Wrestling",
"Martial Arts",
"Net Games",
"Cricket",
"American Football",
"Indoor Games"    
]
health_nutr_agric = [
"HEALTH AND NUTRITION",
"KitchenWare and Tech",
"Recipes",
"Niutrition",
"Deseases"

]

agric_green = [
"GO GREEN AND AGRICULTURE",
"Vaccations",
"Energy",
"Wildlife",
"Forestry",
"Agricultural Technology",
"Food Security",
"water",
"Global Warming"



]

rel_life_style = [
"LIFESTYLE AND RELATIONS",
"Fashion",
"Shoes",
"Women Wear",
"Weddings",
"Men Wear",
"Hair Beauty",
"Marriage",
"Sex and Relationships",
"Parenting",
"Devorce"                 
]

buss_invest = [
"BUSINESS AND INVESTMENT",
"CryptoCurrency",
"Sports Betting",
"Banking",
"Stock_Exchange",
"Online Business",

]

mortage_property = [
"MORTAGE AND PROPERTY",
"Land",
"Houses",
"Applicationartments",
"Family Transport",
"Furniture and House Equipment",
"Cars"
    ]


@application.route('/post/' , methods = ['POST','GET'])
@csrf.exempt
def post():
    
   
    
    if request.method == "POST":
            
        link_db = mongo.db.links
        
        post_class = request.form.get('post_class')
        
         
        desc = request.form['desc']
        
        link = request.form['link']
        
        title = request.form['title']
        
        post_id = md5_crypt.hash(title)
        
        sec1  = request.form['sec1']
        
        sec2 = request.form['sec2']
        
        pic = request.files['img']
        
       # sec3 = request.form['sec3']
        
        sec_arr = []
        
        if not sec1 == "" and not  len(sec1) >100 and  not sec1 in sec_arr and not len(sec1) < 0:
                
            sec_arr.append(sec1)
            
        if not sec2 == "" and not len(sec2) >100 and not sec2 in sec_arr and not len(sec1) < 0 :
            
            sec_arr.append(sec2)
            
       # if not sec3 == "" and len(sec3) >100 and sec3 in sec_arr:
            
            #sec_arr.applicationend(sec3)
            
        tag1 = request.form['tag1']
        
        tag2 = request.form['tag2']
    
       # tag3 = request.form['tag3']
        
       # tag4 = request.form['tag4']
        
        #tag5 = request.form['tag5']
       
        
        tag_arr = []
        
        tag_arr.append(tag1)
        tag_arr.append(tag2)
        
      
        #if not tag3 == "" and len(tag3) >15 and tag3 in tag_arr:
            
         #   tag_arr.applicationend(tag3)
            
        #if not tag4 == "" and len(tag4) >15 and tag4 in tag_arr:
            
         #   tag_arr.applicationend(tag4)
        
        #if not tag5 == "" and len(tag5) >15 and tag5 in tag_arr:
            
            #tag_arr.applicationend(tag5)
        owner = session['login_user']
        like_arr = [owner]
        comments = []
        filename = secure_filename(pic.filename)
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
            
        if allowed_file(filename):
            pic.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
            image = upload_folder +  "/" + filename
            with open(image , "rb") as image2string:
                converted_string = base64.b64encode(image2string.read())
                uploa = converted_string.decode('utf-8')
        
        link_db.insert_one({"owner" : owner , "link" : link , "secondary" : sec_arr, "likes" : like_arr , "comments" : comments ,
                            "tags" : tag_arr , "title" : title , "description" : desc , "class" : post_class , "post_id" : post_id ,
                            "post_pic" : uploa })
        return redirect(url_for('main_page'))
    return render_template('post.html' , main_class = main_class , tech = tech)



@application.route('/choose_tags/' , methods = ['POST','GET'])
@csrf.exempt
def choose_tags():
    user_email = session['login_user']
    if request.method == "POST":
        aaction = request.form['sub']
        user_db = mongo.db.users
        user = user_db.find_one({"email" : user_email})
        em_tags = user['tags']
        em_tags.append(aaction)
        user_db.find_one_and_update({"email" : user_email} ,{ '$set' :  {"tags": em_tags}} )
      
      
    return render_template('main/choose_tags.html' , mail = user_email , mains = main_class,
                           tech =  tech , ent = enta, mains2 = [tech,enta,sports,buss_invest,rel_life_style,agric_green , health_nutr_agric,mortage_property],
                           
                           
                           )


    
if __name__ == "__main__":
    application.secret_key = "Fuckoffmen"
    application.run(debug = True)

    
