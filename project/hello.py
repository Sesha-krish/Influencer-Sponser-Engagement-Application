from flask import Flask,render_template,request,redirect,url_for,session,flash
import os
from model import db,User,Campaign,AdRequest,Message
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from sqlalchemy import or_

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from flask import Flask, render_template_string

from flask import jsonify
app=Flask(__name__)
app.secret_key='secrettt-key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.sqlite3'
db.init_app(app)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
admincredentials={
    'username':'seshakrish',
    'password':'123',
    'role':'admin'
}
ongoing_campaigns = [
    {'name': 'messbill', 'progress':40,'status': 'Unpaid'},
    
]

flagged_campaigns = [
    {'name': 'White Hat Jr'},
]

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        role=request.form.get('role')
        user=User.query.filter_by(username=username).first()

        if user and password==user.password:
            session['username']=username
            if role=='influencer':
                return redirect(url_for('influencerdashboard'))
            elif role=='sponsor':
                return redirect(url_for('sponsordashboard'))
        else:
            flash('invalid credentials')
        if role=='admin':
            if username==admincredentials['username'] and password==admincredentials['password']:
                session['username']=username
                return redirect(url_for('admindashboard'))
            else:
                flash('invalid credentials da pnda')
                return redirect(url_for('login'))
        
    return render_template('login.html')


@app.route("/influencersignup", methods=["GET", "POST"])
def influencersignup():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        platform = request.form.get('platform')
        email = request.form.get('email')
        niche = request.form.get('niche')

        print(f"Received data - Username: {username}, Email: {email}, Platform: {platform}, Niche: {niche}")
        
        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            flash('Username already taken', 'error')
            return redirect(url_for('influencersignup'))
        
        if not password or not repassword or not platform or not username or not email:
            flash('Please fill out all required fields', 'error')
            return redirect(url_for('influencersignup'))
        
        if password != repassword:
            flash('Passwords do not match', 'error')
            return redirect(url_for('influencersignup'))
        
        new_user = User(username=username, password=password, role='influencer', platform=platform, email=email, niche=niche)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            print(f"User {username} added successfully as an influencer.")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            print(f"Error occurred: {e}")
            flash('An error occurred while creating your account. Please try again.', 'error')
            return redirect(url_for('influencersignup'))
    
    return render_template("influencersignup.html")


@app.route("/sponsorsignup", methods=["GET", "POST"])
def sponsorsignup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        email = request.form.get('email')
        industry = request.form.get('industry')
        company = request.form.get('company')
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists')
            return redirect(url_for('sponsorsignup'))
        elif password != repassword:
            flash("Passwords don't match")
        else:
            new_user = User(username=username, password=password, role='sponsor', industry=industry, company=company, email=email)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template("sponsorsignup.html")


@app.route("/admindashboard")
def admindashboard():
    if 'username' in session:
        ongoing_campaigns=Campaign.query.filter_by(flagged=None)
        flagged_campaigns=Campaign.query.filter_by(flagged='Flagged')
        return render_template('admindashboard.html', ongoing_campaigns=ongoing_campaigns,flagged_campaigns=flagged_campaigns)
    else:
        flash('login da punda')
        return redirect(url_for('login'))
    
@app.route('/searchh_campaigns', methods=['GET', 'POST'])
def searchh_campaigns():
    search_query = request.form.get('search_query', '')
    campaigns = Campaign.query.filter(Campaign.name.ilike(f'%{search_query}%')).all()
    return render_template('search_campaigns.html', campaigns=campaigns)

@app.route('/searchh_influencers', methods=['GET', 'POST'])
def searchh_influencers():
    search_query = request.form.get('search_query', '')
    influencers = User.query.filter(User.role == 'influencer', User.username.ilike(f'%{search_query}%')).all()
    return render_template('search_influencers.html', influencers=influencers)

@app.route('/searchh_sponsors', methods=['GET', 'POST'])
def searchh_sponsors():
    search_query = request.form.get('search_query', '')
    sponsors = User.query.filter(User.role == 'sponsor', User.username.ilike(f'%{search_query}%')).all()
    return render_template('search_sponsors.html', sponsors=sponsors)
@app.route('/admin_stats')
def admin_stats():
    total_sponsors = User.query.filter_by(role='sponsor').count()
    total_influencers = User.query.filter_by(role='influencer').count()
    total_campaigns = Campaign.query.count()
    total_ad_requests = AdRequest.query.count()

    ad_status_data = {
        'Pending': AdRequest.query.filter_by(ad_status='Pending').count(),
        'Accepted': AdRequest.query.filter_by(ad_status='Accepted').count(),
        'Paid': AdRequest.query.filter_by(ad_status='Paid').count()
    }

    return render_template('admin_stats.html', total_sponsors=total_sponsors, total_influencers=total_influencers, total_campaigns=total_campaigns, total_ad_requests=total_ad_requests, ad_status_data=ad_status_data)

@app.route("/flag_campaign/<int:campaign_id>", methods=["GET", "POST"])
def flag_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if request.method == "POST":
        reason = request.form["reason"]
        campaign.flagged = "Flagged"
        campaign.flagreason = reason
        db.session.commit()
        return redirect(url_for("admindashboard"))
    return render_template("flag_campaign.html", campaign=campaign)

@app.route("/remove_flag/<int:campaign_id>", methods=["POST"])
def remove_flag(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.flagged = None
    campaign.flagreason = None
    db.session.commit()
    return redirect(url_for("admindashboard"))

@app.route("/mark_paid/<int:campaign_id>", methods=["POST"])
def mark_paid(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.status = "Paid"
    db.session.commit()
    return redirect(url_for("admindashboard"))


@app.route("/influencerdashboard")
def influencerdashboard():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        ongoing_campaigns = AdRequest.query.filter(
    AdRequest.ad_status == 'Accepted',
    or_(AdRequest.sender_id == session['username'], AdRequest.receiver_id == session['username'])
).all()
        sent_requests = AdRequest.query.filter_by(sender_id=user.username).all()
        received_requests = AdRequest.query.filter_by(receiver_id=user.username,ad_status='Pending').all()
        return render_template('influencer_dashboard.html', user=user, ongoing_campaigns=ongoing_campaigns, sent_requests=sent_requests, received_requests=received_requests,usrnm='username')
    else:
        flash('Please login first.')
        return redirect(url_for('login'))

@app.route("/find_campaigns", methods=["GET", "POST"])
def find_campaigns():
    if 'username' in session:
        campaigns = Campaign.query.all()
        return render_template('find_campaigns.html', campaigns=campaigns)
    else:
        flash('Please login first.')
        return redirect(url_for('login'))

@app.route("/search_campaigns", methods=["POST"])
def search_campaigns():
    if 'username' in session:
        search_term = request.form.get('search_term')
        campaigns = Campaign.query.filter(Campaign.name.contains(search_term)).all()
        return render_template('find_campaigns.html', campaigns=campaigns)
    else:
        flash('Please login first.')
        return redirect(url_for('login'))

@app.route("/filter_campaigns", methods=["POST"])
def filter_campaigns():
    if 'username' in session:
        filter_type = request.form.get('filter_type')
        if filter_type == 'MR':
            campaigns = Campaign.query.order_by(Campaign.s_date.desc()).all()
        elif filter_type=='LR':
            campaigns = Campaign.query.order_by(Campaign.s_date.asc()).all()
        elif filter_type == 'BH2L':
            campaigns = Campaign.query.order_by(Campaign.budget.desc()).all()
        elif filter_type=="BL2H":
            campaigns= Campaign.query.order_by(Campaign.budget.asc()).all()
        elif filter_type == 'GBC':
            campaigns = Campaign.query.group_by(Campaign.category).all()
        else:
            campaigns=Campaign.query.group_by(Campaign.s_date.desc()).all()
        return render_template('find_campaigns.html', campaigns=campaigns)
    else:
        flash('Please login first.')
        return redirect(url_for('login'))

@app.route("/send_ad_request/<int:campaign_id>", methods=["POST"])
def send_ad_request(campaign_id):
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        campaign = Campaign.query.get_or_404(campaign_id)
        ad_request = AdRequest(ad_name=campaign.name, ad_des=campaign.des, ad_status='Pending', payment=0, progress=0, rating=0, sender_id=user.username, receiver_id=campaign.user_id, campaign_id=campaign_id)
        db.session.add(ad_request)
        db.session.commit()
        flash('Ad request has been sent successfully!','Ad request has been sent successfully')
        return redirect(url_for('find_campaigns'))
    else:
        flash('Please login first.')
        return redirect(url_for('login'))
@app.route('/reject_ad_request_inf/<int:ad_request_id>', methods=['POST'])
def reject_ad_request_inf(ad_request_id):
    ad_request = AdRequest.query.get(ad_request_id)
    
    if ad_request:
        db.session.delete(ad_request)
        db.session.commit()
        flash('Ad request rejected successfully.')
    else:
        flash('Ad request not found.')
    
    return redirect(url_for('influencerdashboard'))
@app.route("/accept_ad_request/<int:ad_request_id>", methods=["POST"])
def accept_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if ad_request.receiver_id == user.username:
            ad_request.ad_status = 'Accepted'
            db.session.commit()
            flash('Ad request accepted!')
        return redirect(url_for('influencerdashboard'))
    else:
        flash('Please login first.')
        return redirect(url_for('login'))



@app.route("/retract_ad_request/<int:ad_request_id>", methods=["POST"])
def retract_ad_request(ad_request_id):
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        ad_request = AdRequest.query.get_or_404(ad_request_id)

        
        if user.role == 'influencer' and ad_request.sender_id == user.username:
            db.session.delete(ad_request)
            db.session.commit()
            flash('Ad request retracted successfully!', 'Ad request retracted successfully!')
        elif user.role == 'sponsor' and ad_request.sender_id == user.username:
            db.session.delete(ad_request)
            db.session.commit()
            flash('Ad request retracted successfully!', 'success')
        else:
            flash('You are not authorized to retract this ad request.', 'You are not authorized to retract this ad request.')
        
        return redirect(url_for('sponsordashboard' if user.role == 'sponsor' else 'influencerdashboard'))
    else:
        flash('Please login first.', 'Please login first.')
        return redirect(url_for('login'))
    
@app.route("/sponsor_profile", methods=["GET", "POST"])
def sponsor_profile():
    if 'username' not in session:
        flash('Please log in', 'danger')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=session['username']).first()
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.company = request.form['company']
        user.industry = request.form['industry']
        
    
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file.filename != '':
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
                file.save(file_path)
                user.profile_picture = file.filename  

        if 'remove_picture' in request.form:
            if user.profile_picture:
                existing_file_path = os.path.join(app.config['UPLOAD_FOLDER'], user.profile_picture)
                if os.path.exists(existing_file_path):
                    os.remove(existing_file_path)
                user.profile_picture = None  
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('sponsor_profile'))

    return render_template('sponsor_profile.html', user=user)


@app.route("/update_progress", methods=["POST"])
def update_progress():
    if 'username' not in session:
        flash('Please log in')
        return redirect(url_for('login'))

    campaign_id = request.form.get('campaign_id')
    new_progress = request.form.get('progress')

    campaign = AdRequest.query.filter_by(id=campaign_id).first()
    if campaign:
        campaign.progress = float(new_progress)
        db.session.commit()
        flash('Campaign progress updated successfully')

    return redirect(url_for('influencerdashboard'))

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if 'username' not in session:
        flash('Please log in')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=session['username']).first()
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.platform = request.form['platform']
        user.niche = request.form['niche']
        
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file.filename != '':
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
                file.save(file_path)
                user.profile_picture = file.filename  

        if 'remove_picture' in request.form:
            if user.profile_picture:
                existing_file_path = os.path.join(app.config['UPLOAD_FOLDER'], user.profile_picture)
                if os.path.exists(existing_file_path):
                    os.remove(existing_file_path)
                user.profile_picture = None  
        db.session.commit()
        flash('Profile updated successfully')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)

@app.route('/messages/<int:ad_request_id>', methods=['GET', 'POST'])
def messages(ad_request_id):
    pl=[]
    mess=''
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if request.method == 'POST':
        content = request.form['content']
        sender_id = session['username']
        receiver_id = ad_request.receiver_id if sender_id == ad_request.sender_id else ad_request.sender_id
        message = Message(content=content, sender_id=sender_id, receiver_id=receiver_id, ad_request_id=ad_request_id, campaign_id=ad_request.campaign_id)
        db.session.add(message)
        db.session.commit()
        flash('Message sent!', 'success')
        return redirect(url_for('messages', ad_request_id=ad_request_id))

    messages = Message.query.filter_by(ad_request_id=ad_request_id).order_by(Message.timestamp).all()
    linksforsponsor=[url_for('sponsordashboard'),url_for('find_influencers')]
    linksforinfluencer=[url_for('influencerdashboard'),url_for('find_campaigns')]
    rec=User.query.filter_by(username=session['username']).first()
    if rec.role=='Sponsor':
        pl=linksforsponsor 
        mess='Find Influencers'
    else:
        pl=linksforinfluencer
        mess='Find Campaigns'
    return render_template('messages.html', ad_request=ad_request, messages=messages,sideb1=pl[0],sideb2=pl[1],mm=mess)

@app.route('/stats')
def stats():
   
    total_campaigns = Campaign.query.count()
    ads = AdRequest.query.all()


    paid_ads = sum(1 for ad in ads if ad.ad_status == 'Paid')
    pending_ads = sum(1 for ad in ads if ad.ad_status == 'Pending')
    accepted_ads = sum(1 for ad in ads if ad.ad_status == 'Accepted')

    return render_template('stats.html', total_campaigns=total_campaigns,
                           paid_ads=paid_ads, pending_ads=pending_ads, accepted_ads=accepted_ads)

@app.route("/sponsordashboard")
def sponsordashboard():
    if 'username' in session:
        sponsor = User.query.filter_by(username=session['username']).first()
        ongoing_campaigns = Campaign.query.filter_by(user_id=session['username']).all()
        for campaign in ongoing_campaigns:
            goal = int(campaign.camp_goal)
            accepted_ads = AdRequest.query.filter_by(campaign_id=campaign.id, ad_status='Accepted').count()
            campaign.progress = (accepted_ads / goal) * 100 if goal > 0 else 0
            db.session.commit()
        ongoingadcampaigns = AdRequest.query.filter(
        AdRequest.ad_status == 'Accepted',
        or_(AdRequest.receiver_id == session['username'], AdRequest.sender_id == session['username'])).all()
        recadrequests=AdRequest.query.filter_by(receiver_id=session['username'],ad_status='Pending').all()
        sentadrequests=AdRequest.query.filter_by(sender_id=session['username'],ad_status='Pending').all()
        print("Ongoing campaigns:", ongoing_campaigns)  
        print('aa')
        return render_template('sponsordashboard.html', ongoing_campaigns=ongoing_campaigns,rec_ad_requests=recadrequests,sent_ad_requests=sentadrequests,ongoingad=ongoingadcampaigns)
    else:
        flash('Please login first.')
        return redirect(url_for('login'))
    

@app.route("/add_campaign", methods=["GET", "POST"])
def add_campaign():
    if 'username' in session:
        if request.method == "POST":
            name = request.form.get('name')
            des = request.form.get('des')
            category = request.form.get('category')
            budget = float(request.form.get('budget'))
            s_date = datetime.strptime(request.form.get('s_date'), '%Y-%m-%d').date()
            e_date = datetime.strptime(request.form.get('e_date'), '%Y-%m-%d').date()
            camp_goal = request.form.get('camp_goal')
            status='Incomplete'

            new_campaign = Campaign(name=name, des=des, category=category, budget=budget, s_date=s_date, e_date=e_date, status=status,camp_goal=camp_goal, user_id=session['username'])
            db.session.add(new_campaign)
            db.session.commit()
            flash('Campaign added successfully!')
            return redirect(url_for('sponsordashboard'))
        return render_template('add_campaign.html')
    else:
        flash('Please login first.')
        return redirect(url_for('login'))
from flask import jsonify

@app.route("/view_campaign/<int:campaign_id>", methods=["GET"])
def view_campaign(campaign_id):
    if 'username' in session:
        campaign = Campaign.query.get(campaign_id)
        if campaign:
            campaign_data = {
                'id': campaign.id,
                'name': campaign.name,
                'des': campaign.des,
                'category': campaign.category,
                'budget': campaign.budget,
                's_date': campaign.s_date.strftime('%Y-%m-%d'),
                'e_date': campaign.e_date.strftime('%Y-%m-%d'),
                'camp_goal': campaign.camp_goal,
                'progress': campaign.progress,
                'status': campaign.status
            }
            return jsonify(campaign_data)
        else:
            flash('Campaign not found!')
            return redirect(url_for('sponsordashboard'))
    else:
        flash('Please login first.')
        return redirect(url_for('login'))

@app.route('/pay_ad/<int:ad_request_id>', methods=['GET', 'POST'])
def pay_ad(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')

        if payment_method == 'upi':
            upi_id = request.form.get('upi_id')
            if not upi_id:
                flash('Please enter a valid UPI ID', 'danger')
                return redirect(url_for('pay_ad', ad_request_id=ad_request_id))
        
        elif payment_method == 'net_banking':
            bank_account = request.form.get('bank_account')
            bank_name = request.form.get('bank_name')
            ifsc_code = request.form.get('ifsc_code')
            if not bank_account or not bank_name or not ifsc_code:
                flash('Please enter all required bank details', 'danger')
                return redirect(url_for('pay_ad', ad_request_id=ad_request_id))

        elif payment_method == 'card':
            card_number = request.form.get('card_number')
            expiry_date = request.form.get('expiry_date')
            cvv = request.form.get('cvv')
            if len(card_number) != 16:
                flash('Enter a valid 16-digit card number', 'danger')
                return redirect(url_for('pay_ad', ad_request_id=ad_request_id))

        # Update ad status to paid
        ad_request.ad_status = 'Paid'
        db.session.commit()

        flash('Payment successful. Ad request marked as Paid.', 'success')
        return redirect(url_for('sponsordashboard'))
    
    return render_template('pay_ad.html', ad_request=ad_request)

@app.route("/accept_ad_request_spon/<int:ad_request_id>",methods=["POST"])
def accept_ad_request_spon(ad_request_id):
    adreq=AdRequest.query.get_or_404(ad_request_id)
    if 'username' in session:
        user=User.query.filter_by(username=session['username']).first()
        if adreq.receiver_id==user.username:
            adreq.ad_status='Accepted'
            db.session.commit()
            flash('Ad request accepted','success')
            return redirect(url_for('sponsordashboard'))
    else:
        flash('Please log in','error')
        return redirect(url_for('login'))
@app.route('/reject_ad_request/<int:ad_request_id>', methods=['POST'])
def reject_ad_request_spon(ad_request_id):
    ad_request = AdRequest.query.get(ad_request_id)
    
    if ad_request:
        db.session.delete(ad_request)
        db.session.commit()
        flash('Ad request rejected successfully.')
    else:
        flash('Ad request not found.')
    
    return redirect(url_for('sponsordashboard'))

@app.route("/update_campaign/<int:campaign_id>", methods=["GET", "POST"])
def update_campaign(campaign_id):
    if 'username' in session:
        campaign = Campaign.query.get(campaign_id)
        if campaign:
            if request.method == "POST":
                name = request.form.get('name')
                des = request.form.get('des')
                category = request.form.get('category')
                budget = request.form.get('budget')
                s_date = request.form.get('s_date')
                e_date = request.form.get('e_date')
                camp_goal = request.form.get('camp_goal')
                status = request.form.get('camp_status')
                progress = request.form.get('progress')

                if name and des and category and budget and s_date and e_date and camp_goal and status:
                    try:
                        campaign.name = name
                        campaign.des = des
                        campaign.category = category
                        campaign.budget = float(budget)
                        campaign.s_date = datetime.strptime(s_date, '%Y-%m-%d').date()
                        campaign.e_date = datetime.strptime(e_date, '%Y-%m-%d').date()
                        campaign.camp_goal = camp_goal
                        campaign.status = status

                        if status == 'Paid':
                            campaign.progress = 100
                        else:
                            campaign.progress = float(progress)

                        db.session.commit()
                        flash('Campaign updated successfully!')
                    except ValueError:
                        flash('Invalid data format.', 'error')
                else:
                    flash('All fields are required.', 'error')

                return redirect(url_for('sponsordashboard'))
            return render_template('update_campaign.html', campaign=campaign)
        else:
            flash('Campaign not found!')
            return redirect(url_for('sponsordashboard'))
    else:
        flash('Please login first.')
        return redirect(url_for('login'))


@app.route("/delete_campaign/<int:campaign_id>",  methods=["GET", "POST"])
def delete_campaign(campaign_id):
    if 'username' in session:
        campaign = Campaign.query.get(campaign_id)
        if campaign:
            db.session.delete(campaign)
            db.session.commit()
            flash('Campaign deleted successfully!')
            return redirect(url_for('sponsordashboard'))
        else:
            flash('Campaign not found!')
            return redirect(url_for('sponsordashboard'))
    else:
        flash('Please login first.')
        return redirect(url_for('login'))
    
@app.route("/find_influencers")
def find_influencers():
    if 'username' in session: 
        influencers=User.query.filter_by(role='influencer').all()
        return render_template('find_influencers.html',influencers=influencers)
    else:
        flash('please log in')
        return redirect(url_for('login'))
    
@app.route("/search_influencers",methods=["POST"])
def search_influencers():
    search_term = request.form.get('search_term')
    influencers=User.query.filter(User.username.contains(search_term),User.role=='influencer').all()
    return render_template('find_influencers.html',influencers=influencers)

@app.route("/send_ad_request_spon/<string:influencer_id>", methods=["GET", "POST"])
def send_ad_request_spon(influencer_id):
    if 'username' in session:
        if request.method == "POST":
            campaign_id = request.form.get('campaignss')
            payment = request.form.get('payment')
            
            if not campaign_id:
                flash('Campaign not selected')
                return redirect(url_for('send_ad_request_spon', influencer_id=influencer_id))

            if not payment:
                flash('Payment amount not provided')
                return redirect(url_for('send_ad_request_spon', influencer_id=influencer_id))

            try:
                payment = float(payment) 
            except ValueError:
                flash('Invalid payment amount')
                return redirect(url_for('send_ad_request_spon', influencer_id=influencer_id))

            singlecampaign = Campaign.query.filter_by(id=campaign_id).first()
            
            if singlecampaign is None:
                flash('Campaign not found')
                return redirect(url_for('send_ad_request_spon', influencer_id=influencer_id))

            if singlecampaign.budget < payment:
                flash('Payment is exceeding the remaining budget of the Campaign')
                return redirect(url_for('send_ad_request_spon', influencer_id=influencer_id))
            else:
                try:
                    singlecampaign.budget -= payment
                    ad_request = AdRequest(
                        ad_name=singlecampaign.name, 
                        ad_des=singlecampaign.des, 
                        ad_status='Pending', 
                        payment=payment, 
                        progress=0, 
                        rating=0, 
                        sender_id=session['username'], 
                        receiver_id=influencer_id, 
                        campaign_id=singlecampaign.id
                    )
                    db.session.add(ad_request)
                    db.session.add(singlecampaign)
                    db.session.commit()
                    flash('Ad request sent successfully!')
                    return redirect(url_for('sponsordashboard'))
                except Exception as e:
                    db.session.rollback()
                    flash('An error occurred: {}'.format(str(e)))
                    return redirect(url_for('send_ad_request_spon', influencer_id=influencer_id))

        Campaigns = Campaign.query.filter_by(user_id=session['username']).all()
        return render_template('sendadreqspon.html', Campaigns=Campaigns)
    
    flash('Please log in')
    return redirect(url_for('login'))

@app.route("/view_influencer/<string:influencer_id>",methods=["GET"])
def view_influencer(influencer_id):
    if 'username' in session:
        influencer=User.query.filter_by(username=influencer_id)
        return render_template('viewinfluencer.html',influencer=influencer)
    else:
        flash('Login please')
        return redirect(url_for('login'))
@app.route('/get_influencer_details/<username>')
def get_influencer_details(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({
            'username': user.username,
            'email': user.email,
            'platform': user.platform,
            'niche': user.niche,
            'profile_picture': user.profile_picture or '/static/default-profile.png'
        })
    return jsonify({'error': 'User not found'}), 404


@app.route("/campaign/stats/<int:sponsor>")
def generate_dummy_data():
    data = {
        'Category': ['A', 'B', 'C', 'D'],
        'Values': [10, 20, 30, 40]
    }
    df = pd.DataFrame(data)
    return df


def create_plot(df):
    fig = px.bar(df, x='Category', y='Values', title='Dummy Data Bar Chart')
    plot_html = pio.to_html(fig, full_html=False)
    return plot_html
@app.route('/logout/<string:username>')
def logout(username):
    if 'username' in session:
        del session['username']
        return redirect(url_for('login'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)