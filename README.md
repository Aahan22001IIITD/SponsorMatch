# SponsorMatch

## Project Overview

This project is a web application designed to manage campaigns between sponsors and influencers. It allows sponsors to create campaigns, influencers to apply, and admins to oversee activities and manage flagged content.

## Folder Structure

.
├── code/
│ ├── app.py
│ ├── er.png # ER Diagram of the Database
│ ├── platform.sqlite3 # SQLite Database File
│ └── [Other Python Files]
├── templates/
│ ├── acceptedinfl.html
│ ├── admin_dashboard.html
│ ├── all_influencers.html
│ ├── campaign_analysis.html
│ ├── create_campaign.html
│ ├── delete_campaign.html
│ ├── edit_profile.html
│ ├── error.html
│ ├── flag_user.html
│ ├── infl.html
│ ├── influencers.html
│ ├── login.html
│ ├── manage_requests.html
│ ├── negotiate_campaign.html
│ ├── profile.html
│ ├── register.html
│ ├── request_influencer.html
│ ├── requests.html
│ ├── search_influencers.html
│ ├── search_results.html
│ ├── select_campaign.html
│ ├── select_campaign_to_delete.html
│ ├── sponsor.html
│ ├── view_admin_campaigns.html
│ ├── view_campaigns.html
│ ├── view_flagged_users.html
│ ├── view_influencers.html
│ ├── view_ongoing_campaigns.html
│ ├── view_requests.html
│ └── view_sponsors.html

## Features

- **Database Design:** Manages sponsors, influencers, campaigns, ongoing campaigns, requests, flagged users, and rejected campaigns.
- **Backend Development:** Flask-based web application with RESTful APIs for data manipulation and retrieval.
- **Frontend Development:** Responsive user interfaces created with Bootstrap.
- **Admin Panel:** Dashboard for monitoring users, campaigns, and managing flagged content.

## Frameworks and Libraries

- **Flask:** Web framework for server-side logic.
- **SQLAlchemy:** ORM for database management.
- **Bootstrap:** For styling and responsive design.
- **SQLite:** Database engine for development.

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Aahan22001IIITD/https://github.com/Aahan22001IIITD/SponsorMatch
   python code/app.py
   ```
Usage
Register as a sponsor or influencer.
Login to manage campaigns and requests.
Admin can view dashboards and manage flagged content.
