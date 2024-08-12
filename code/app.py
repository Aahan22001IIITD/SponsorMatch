from flask import Flask, request, redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import os 

app = Flask(__name__)
current_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "platform.sqlite3")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
app.secret_key = 'supersecretkey'
db = SQLAlchemy(app)

class SponsorInfo(db.Model):
    __tablename__ = 'SponsorInfo'
    Spons_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    industry = db.Column(db.String, nullable=False)
    Name = db.Column(db.String, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String, nullable=False)
    pass_ = db.Column(db.String, nullable=False) 

class Campaign(db.Model):
    __tablename__ = 'Campaign'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    desc = db.Column(db.String, nullable=False)
    s_date = db.Column(db.String, nullable=False)
    e_date = db.Column(db.String, nullable=False)
    niche = db.Column(db.String, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    visibility = db.Column(db.Integer, nullable=False)
    way = db.Column(db.Integer, nullable=False)
    SponId = db.Column(db.Integer, db.ForeignKey('SponsorInfo.Spons_id'), nullable=False)

class OngoingCamp(db.Model):
    __tablename__ = 'ongoing_camp'
    cid = db.Column(db.Integer, db.ForeignKey('Campaign.id'), primary_key=True)
    iid = db.Column(db.Integer, db.ForeignKey('Influencer.inflid'), primary_key=True)
    reqid = db.Column(db.Integer)
class FlaggedUsers(db.Model):
    __tablename__ = 'FlaggedUsers'
    
    user_id = db.Column(db.Integer, nullable=False)
    user_type = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'user_type'),
    )


class Influencer(db.Model):
    __tablename__ = 'Influencer'
    inflid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String, nullable=False)
    Category = db.Column(db.String, nullable=False)
    Niche = db.Column(db.String, nullable=False)
    Reach = db.Column(db.Integer, nullable=False)
    profilephoto = db.Column(db.String)
    username = db.Column(db.String, nullable=False)
    pass_ = db.Column(db.Integer, nullable=False)  

class Request(db.Model):
    __tablename__ = 'Request'
    reqid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campid = db.Column(db.Integer, db.ForeignKey('Campaign.id'), nullable=False)
    inflid = db.Column(db.Integer, db.ForeignKey('Influencer.inflid'), nullable=False)
    way = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String)
    requirements = db.Column(db.String, nullable=False)
    amount = db.Column(db.Integer, nullable=False)

class RejectedCampaigns(db.Model):
    __tablename__ = 'RejectedCampaigns'
    cid = db.Column(db.Integer, db.ForeignKey('Campaign.id'), nullable=False, primary_key=True)
    iid = db.Column(db.Integer, db.ForeignKey('Influencer.inflid'), nullable=False, primary_key=True)

@app.route('/influencers')
def show_influencers():
    influencers = Influencer.query.all()
    return render_template('influencers.html', influencers=influencers)

@app.route('/search')
def search():
    category = request.args.get('category')
    budget_min = request.args.get('budget_min', type=int)
    budget_max = request.args.get('budget_max', type=int)
    
    rejected_campaigns = RejectedCampaigns.query.all()
    rejected_campaign_ids = [r.cid for r in rejected_campaigns]
    ongoing_campaigns = OngoingCamp.query.all()
    ongoing_campaign_ids = [o.cid for o in ongoing_campaigns]
    query = Campaign.query.filter(Campaign.visibility == 1).filter(~Campaign.id.in_(rejected_campaign_ids)).filter(~Campaign.id.in_(ongoing_campaign_ids))

    if category:
        query = query.filter(Campaign.niche.ilike(f'%{category}%'))
    if budget_min is not None:
        query = query.filter(Campaign.budget >= budget_min)
    if budget_max is not None:
        query = query.filter(Campaign.budget <= budget_max)
    
    campaigns = query.all()
    camplist = []
    for c in campaigns:
        sponsor = SponsorInfo.query.filter_by(Spons_id=c.SponId).first()
        camplist.append([c, sponsor])
    
    return render_template('search_results.html', campaigns=camplist)


@app.route('/infl/<int:inflid>/inflreq')
def influencer_requests(inflid):
    influencer = Influencer.query.get_or_404(inflid)

    rejected_campaigns = RejectedCampaigns.query.filter_by(iid=inflid).all()
    rejected_campaign_ids = [r.cid for r in rejected_campaigns]

    requests = Request.query.filter_by(inflid=inflid, way=0).filter(Request.campid.notin_(rejected_campaign_ids)).all()
    
    return render_template('requests.html', influencer=influencer, requests=requests)


@app.route('/infl/<int:inflid>/camp/<int:cid>/accept', methods=['POST'])
def accept_campaign(inflid, cid):
    influencer = Influencer.query.get_or_404(inflid)
    campaign = Campaign.query.get_or_404(cid)
    request = Request.query.filter_by(campid=cid, inflid=inflid).first()
    visibility = campaign.visibility
    if campaign.way == 0:
        if(request is None):
            ongoing_campaign  = OngoingCamp(cid = cid , iid = inflid )
        else:
            ongoing_campaign = OngoingCamp(cid=cid, iid=inflid, reqid=request.reqid)
        db.session.add(ongoing_campaign)
        
        if request:
            db.session.delete(request)
        db.session.commit()
        flash('Campaign accepted successfully!')
    else:
        flash('Invalid campaign or unable to accept.')

    return redirect(url_for('profile', infl_id=inflid))
@app.route('/infl/<int:inflid>/request/<int:cid>/accept', methods=['POST'])
def accept_request(inflid, cid):
    influencer = Influencer.query.get_or_404(inflid)
    campaign = Campaign.query.get_or_404(cid)
    request = Request.query.filter_by(campid=cid, inflid=inflid).first()
    visibility = campaign.visibility
    if campaign.way == 0:
        if(request is None):
            ongoing_campaign  = OngoingCamp(cid = cid , iid = inflid )
        else:
            ongoing_campaign = OngoingCamp(cid=cid, iid=inflid, reqid=request.reqid)
        db.session.add(ongoing_campaign)
        
        if request:
            db.session.delete(request)
        db.session.commit()
        flash('Campaign accepted successfully!')
    else:
        flash('Invalid campaign or unable to accept.')

    return redirect(url_for('profile', infl_id=inflid))
@app.route('/analyse_campaign/<int:spons_id>', methods=['GET', 'POST'])
def analyse_campaign(spons_id):
    sponsor = SponsorInfo.query.get_or_404(spons_id)
    campaigns = Campaign.query.filter_by(SponId=spons_id).all()

    if request.method == 'POST':
        camp_id = request.form.get('campaign_id')
        campaign = Campaign.query.get_or_404(camp_id)
        
        requested_count = Request.query.filter_by(campid=camp_id).count()
        
        accepted_count = OngoingCamp.query.filter_by(cid=camp_id).count()
        
        rejected_count = RejectedCampaigns.query.filter_by(cid=camp_id).count()
        currently_working_count = OngoingCamp.query.filter_by(cid=camp_id).count()
        
        total_spent = Request.query.filter_by(campid=camp_id).filter(Request.way == 0).with_entities(db.func.sum(Request.amount)).scalar() or 0

        return render_template('campaign_analysis.html', sponsor=sponsor, campaign=campaign,
                               requested_count=requested_count, accepted_count=accepted_count,
                               rejected_count=rejected_count, currently_working_count=currently_working_count,
                               total_spent=total_spent)

    return render_template('select_campaign.html', sponsor=sponsor, campaigns=campaigns)
@app.route('/select_campaign_to_delete/<int:spons_id>', methods=['GET', 'POST'])
def select_campaign_to_delete(spons_id):
    sponsor = SponsorInfo.query.get_or_404(spons_id)
    
    if request.method == 'POST':
        camp_id = request.form['campaign']
        return redirect(url_for('delete_campaign', spons_id=spons_id, camp_id=camp_id))

    campaigns = Campaign.query.filter_by(SponId=spons_id).all()
    return render_template('select_campaign_to_delete.html', sponsor=sponsor, campaigns=campaigns)

@app.route('/delete_campaign/<int:spons_id>/<int:camp_id>', methods=['GET' , 'POST'])
def delete_campaign(spons_id, camp_id):
    sponsor = SponsorInfo.query.get_or_404(spons_id)

    OngoingCamp.query.filter_by(cid=camp_id).delete()
    RejectedCampaigns.query.filter_by(cid=camp_id).delete()
    Request.query.filter_by(campid=camp_id).delete()
    Campaign.query.filter_by(id=camp_id).delete()
    
    db.session.commit()
    flash('Campaign deleted successfully!')
    return redirect(url_for('sponsor_dashboard', spons_id=spons_id))
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        registration_type = request.form['registration_type']
        if registration_type == 'influencer':
            name = request.form['name']
            category = request.form['category']
            niche = request.form['niche']
            reach = request.form['reach']
            profilephoto = request.form['profilephoto']
            username = request.form['username']
            password = request.form['password']
            
            new_influencer = Influencer(Name=name, Category=category, Niche=niche, Reach=reach, profilephoto=profilephoto, username=username, pass_=password)
            db.session.add(new_influencer)
            db.session.commit()
            flash('Influencer registered successfully!')
            return redirect(url_for('index'))
        
        else:
            flash('Invalid registration type.')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/manage_requests/<int:spons_id>', methods=['GET', 'POST'])
def manage_requests(spons_id):
    sponsor = SponsorInfo.query.get_or_404(spons_id)
    if request.method == 'POST':
        req_id = request.form.get('request_id')
        action = request.form.get('action')

        request_obj = Request.query.get_or_404(req_id)
        if action == 'accept':
            ongoing_campaign = OngoingCamp(cid=request_obj.campid, iid=request_obj.inflid, reqid=req_id)
            db.session.add(ongoing_campaign)
            db.session.delete(request_obj)
        elif action == 'reject':
            rejected_campaign = RejectedCampaigns(cid=request_obj.campid, iid=request_obj.inflid)
            db.session.add(rejected_campaign)
            db.session.delete(request_obj)

        db.session.commit()
        flash('Request processed successfully!')
        return redirect(url_for('manage_requests', spons_id=spons_id))
    requests = Request.query.filter_by(way=1).all()
    return render_template('manage_requests.html', sponsor=sponsor, requests=requests)

@app.route('/infl/<int:inflid>/request/<int:reqid>/reject', methods=['POST'])
def reject_request(inflid, reqid):
    req = Request.query.get_or_404(reqid)
    if req.inflid != inflid:
        flash('Invalid request.')
        return redirect(url_for('influencer_requests', inflid=inflid))
    new_rejected = RejectedCampaigns(iid=inflid, cid=req.campid)
    db.session.add(new_rejected)
    db.session.delete(req) 
    db.session.commit()
    
    flash('Request rejected successfully!')
    return redirect(url_for('influencer_requests', inflid=inflid))

@app.route('/infl/<int:inflid>/camp/<int:cid>/reject', methods=['POST'])
def reject_campaign(inflid, cid):
    campaign = Campaign.query.get_or_404(cid)
    request = Request.query.filter_by(campid=cid, inflid=inflid).first()
    
    if campaign.visibility == 1 and campaign.way == 0:
        if request:
            db.session.delete(request)
        rejected_campaign = RejectedCampaigns(cid=cid, iid=inflid)
        db.session.add(rejected_campaign)
        db.session.commit()
        flash('Campaign rejected successfully!')
    else:
        flash('Invalid campaign or unable to reject.')

    return redirect(url_for('influencer_dashboard' , inflid = inflid))


@app.route('/profile/<int:infl_id>')
def profile(infl_id):
    influencer = Influencer.query.get_or_404(infl_id)
    ongoing_campaigns = OngoingCamp.query.filter_by(iid=infl_id).all()
    campaigns = []
    for oc in ongoing_campaigns:
        campaign = Campaign.query.filter_by(id=oc.cid).first()
        sponsor = SponsorInfo.query.filter_by(Spons_id=campaign.SponId).first() if campaign else None
        campaigns.append({
                'campaign': campaign,
                'sponsor': sponsor,
                'reqid': oc.reqid
            })
    public_campaigns = Campaign.query.filter_by(visibility=1, way=0).all()
    accepted_campaign_ids = [oc.cid for oc in ongoing_campaigns]
    public_campaigns = [c for c in public_campaigns if c.id not in accepted_campaign_ids]
    return render_template('profile.html', influencer=influencer, campaigns=campaigns, public_campaigns=public_campaigns)
@app.route('/profile/<int:infl_id>/edit', methods=['GET', 'POST'])
def edit_profile(infl_id):
    influencer = Influencer.query.get_or_404(infl_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        niche = request.form.get('niche')
        reach = request.form.get('reach')
        profilephoto = request.form.get('profilephoto')  
        username = request.form.get('username')
        password = request.form.get('password')
        
        influencer.Name = name
        influencer.Category = category
        influencer.Niche = niche
        influencer.Reach = reach
        influencer.profilephoto = profilephoto
        influencer.username = username
        influencer.pass_ = password
        
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('profile', infl_id=infl_id))
    
    return render_template('edit_profile.html', influencer=influencer)
@app.route('/create_campaign/<int:spons_id>', methods=['GET', 'POST'])
def create_campaign(spons_id):
    sponsor = SponsorInfo.query.get_or_404(spons_id)
    if request.method == 'POST':
        desc = request.form.get('desc')
        s_date = request.form.get('s_date')
        e_date = request.form.get('e_date')
        niche = request.form.get('niche')
        budget = request.form.get('budget')
        visibility = request.form.get('visibility', type=int)
        way = request.form.get('way', type=int)
        new_campaign = Campaign(
            desc=desc,
            s_date=s_date,
            e_date=e_date,
            niche=niche,
            budget=budget,
            visibility=visibility^1,
            way=way,
            SponId=spons_id
        )
        db.session.add(new_campaign)
        db.session.commit()
        flash('Campaign created successfully!')
        return redirect(url_for('view_campaigns', spons_id=spons_id))
    
    return render_template('create_campaign.html', sponsor=sponsor)


@app.route('/negotiate_campaign/<int:inflid>/<int:cid>', methods=['GET', 'POST'])
def negotiate_campaign(inflid, cid):
    influencer = Influencer.query.get_or_404(inflid)
    campaign = Campaign.query.get_or_404(cid)

    if request.method == 'POST':
        message = request.form.get('message')
        amount = request.form.get('amount')
        existing_request = Request.query.filter_by(campid=cid, inflid=inflid).first()
        if existing_request:
            existing_request.message = message
            existing_request.amount = amount
            existing_request.way = 1
        else:
            render_template('error.html')
        db.session.commit()
        flash('Negotiation request sent successfully!')
        return redirect(url_for('profile', infl_id=inflid))
    
    return render_template('negotiate_campaign.html', influencer=influencer, campaign=campaign)

@app.route('/view_campaigns/<int:spons_id>')
def view_campaigns(spons_id):
    sponsor = SponsorInfo.query.get_or_404(spons_id)
    campaigns = Campaign.query.filter_by(SponId=spons_id).all()
    return render_template('view_campaigns.html', sponsor=sponsor, campaigns=campaigns)

@app.route('/search_influencers/<int:spons_id>', methods=['GET', 'POST'])
def search_influencers(spons_id):
    sponsor = SponsorInfo.query.get_or_404(spons_id)
    
    if request.method == 'POST':
        category = request.form.get('category')
        niche = request.form.get('niche')
        min_reach = request.form.get('min_reach', type=int)
        query = Influencer.query
        if category:
            query = query.filter(Influencer.Category.ilike(f'%{category}%'))
        if niche:
            query = query.filter(Influencer.Niche.ilike(f'%{niche}%'))
        if min_reach is not None:
            query = query.filter(Influencer.Reach >= min_reach)
        influencers = query.all()
        return render_template('search_influencers.html', influencers=influencers, spons=sponsor)
    
    return render_template('search_influencers.html', influencers=[], spons=sponsor)

@app.route('/sponsor/<int:spons_id>')
def sponsor_dashboard(spons_id):
    sponsor = SponsorInfo.query.get_or_404(spons_id)
    return render_template('sponsor.html', spons=sponsor)
@app.route('/all_influencers/<int:spons_id>')
def all_influencers(spons_id):
    sponsor = SponsorInfo.query.get_or_404(spons_id)
    influencers = Influencer.query.all()
    return render_template('all_influencers.html', sponsor=sponsor, influencers=influencers)
@app.route('/request_influencer/<int:spons_id>/<int:infl_id>', methods=['GET', 'POST'])
def request_influencer(spons_id, infl_id):
    sponsor = SponsorInfo.query.get_or_404(spons_id)
    influencer = Influencer.query.get_or_404(infl_id)
    
    if request.method == 'POST':
        camp_id = request.form.get('campaign_id')
        message = request.form.get('message')
        amount = request.form.get('amount')
        requirements = request.form.get('requirements')  
        
        new_request = Request(campid=camp_id, inflid=infl_id, way=0, message=message, requirements=requirements, amount=amount)
        db.session.add(new_request)
        db.session.commit()

        flash('Request sent successfully!')
        return redirect(url_for('all_influencers', spons_id=spons_id))
    
    campaigns = Campaign.query.filter_by(SponId=spons_id).all()
    return render_template('request_influencer.html', sponsor=sponsor, influencer=influencer, campaigns=campaigns)

@app.route('/infl/<int:inflid>')
def influencer_dashboard(inflid):
    user = Influencer.query.get_or_404(inflid)
    camp = Campaign.query.all()
    camplist = []
    requests = Request.query.filter_by(inflid=user.inflid).all()
    rejected_campaigns = RejectedCampaigns.query.filter_by(iid=user.inflid).all()
    rejected_campaign_ids = [r.cid for r in rejected_campaigns]

    for c in camp:
        cid = c.id
        ongoingc = OngoingCamp.query.filter_by(cid=cid, iid=user.inflid).first()
        if ongoingc is not None:
            continue
    
        if cid in rejected_campaign_ids:
            continue
        sid = c.SponId
        sponsor = SponsorInfo.query.filter_by(Spons_id=sid).first()
        camplist.append([c, sponsor])
    
    return render_template("infl.html", influencer=user, allcamp=camplist, requests=requests)

@app.route('/admin/admin_dashboard')
def admin_dashboard():
    total_infl = Influencer.query.count()
    total_spons = SponsorInfo.query.count()
    total_campaigns = Campaign.query.count()
    public_campaigns = Campaign.query.filter_by(visibility=1).count()
    private_campaigns = Campaign.query.filter_by(visibility=0).count()
    all_requests = Request.query.count()
    ongoing_camps = OngoingCamp.query.count()
    flagged_campaign = FlaggedUsers.query.filter_by(user_type='sponsor').count()
    flagged_influencers = FlaggedUsers.query.filter_by(user_type='influencer').count()
    stats = {
        'total_infl': total_infl,
        'total_spons': total_spons,
        'total_campaigns': total_campaigns,
        'public_campaigns': public_campaigns,
        'private_campaigns': private_campaigns,
        'all_requests': all_requests,
        'ongoing_camps': ongoing_camps,
        'flagged_campaign': flagged_campaign,
        'flagged_influencers': flagged_influencers,
    }

    return render_template('admin_dashboard.html', stats=stats)

@app.route('/admin/view_influencers')
def view_admin_influencers():
    influencers = Influencer.query.all()
    return render_template('view_influencers.html', influencers=influencers)

@app.route('/admin/view_sponsors')
def view_admin_sponsors():
    sponsors = SponsorInfo.query.all()
    return render_template('view_sponsors.html', sponsors=sponsors)

@app.route('/admin/view_campaigns')
def view_admin_campaigns():
    campaigns = Campaign.query.all()
    return render_template('view_admin_campaigns.html', campaigns=campaigns)

@app.route('/admin/view_requests')
def view_admin_requests():
    requests = Request.query.all()
    return render_template('view_requests.html', requests=requests)

@app.route('/admin/view_ongoing_campaigns')
def view_admin_ongoing_campaigns():
    ongoing_camps = OngoingCamp.query.all()
    return render_template('view_ongoing_campaigns.html', ongoing_camps=ongoing_camps)

@app.route('/admin/view_flagged_users')
def view_admin_flagged_users():
    flagged_campaigns = db.session.query(
        FlaggedUsers.user_id,
        FlaggedUsers.reason,
        Campaign.desc.label('campaign_name')
    ).join(Campaign, (FlaggedUsers.user_id == Campaign.id) & (FlaggedUsers.user_type == 'campaign')).all()

    flagged_influencers = db.session.query(
        FlaggedUsers.user_id,
        FlaggedUsers.reason,
        Influencer.Name.label('influencer_name')
    ).join(Influencer, (FlaggedUsers.user_id == Influencer.inflid) & (FlaggedUsers.user_type == 'influencer')).all()

    return render_template('view_flagged_users.html', flagged_campaigns=flagged_campaigns, flagged_influencers=flagged_influencers)


@app.route('/admin/flag_user', methods=['GET', 'POST'])
def flag_user():
    if request.method == 'POST':
        user_id = request.form['user_id']
        user_type = request.form['user_type']
        reason = request.form['reason']
        
        if user_type == 'campaign':
            campaign = Campaign.query.get(user_id)
            if not campaign:
                flash('Campaign not found.')
                return redirect(url_for('flag_user'))
        elif user_type == 'influencer':
            influencer = Influencer.query.get(user_id)
            if not influencer:
                flash('Influencer not found.')
                return redirect(url_for('flag_user'))
        else:
            flash('Invalid user type.')
            return redirect(url_for('flag_user'))
        
        existing_flag = FlaggedUsers.query.filter_by(user_id=user_id, user_type=user_type).first()
        if existing_flag:
            existing_flag.reason = reason
        else:
            flagged_user = FlaggedUsers(user_id=user_id, user_type=user_type, reason=reason)
            db.session.add(flagged_user)
        
        db.session.commit()
        flash('User flagged successfully!')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('flag_user.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_type = request.form['user_type']
        username = request.form['username']
        password = request.form['password']

        if user_type == 'user':
            user = Influencer.query.filter_by(username=username, pass_=password).first()
            if user:
                return redirect(url_for('influencer_dashboard', inflid=user.inflid))
            else:
                flash('Invalid username or password for user.')

        elif user_type == 'sponsor':
            user = SponsorInfo.query.filter_by(username=username, pass_=password).first()
            
            if user:
                return redirect(url_for('sponsor_dashboard', spons_id=user.Spons_id))
            else:
                flash('Invalid username or password for sponsor.')

        elif user_type == 'admin':
            check = False
            if username == "admin" and password == "adminpass":
                check = True
            if(check):
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid username or password for admin.')

        else:
            flash('Invalid user type.')

    return render_template('login.html')



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
