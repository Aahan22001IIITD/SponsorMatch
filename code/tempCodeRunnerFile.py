@app.route('/search_influencers', methods=['GET', 'POST'])
def search_influencers():
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
        return render_template('search_influencers.html', influencers=influencers)
    
    return render_template('search_influencers.html', influencers=[])