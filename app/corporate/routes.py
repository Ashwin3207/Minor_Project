"""Corporate routes for job posting and candidate access."""
from flask import render_template, redirect, url_for, flash, request, session
from datetime import datetime

from app import db
from app.models import User, Opportunity, Application, CorporateProfile, StudentProfile
from app.corporate import bp
from app.auth.decorators import corporate_required


@bp.route('/dashboard')
@corporate_required
def dashboard():
    """Corporate dashboard."""
    corporate_profile = CorporateProfile.query.filter_by(user_id=session['user_id']).first()
    
    # Get statistics
    total_posted = Opportunity.query.filter(
        Opportunity.company_name == corporate_profile.company_name
    ).count()
    
    total_applications = Application.query.join(Opportunity).filter(
        Opportunity.company_name == corporate_profile.company_name
    ).count()
    
    selected_candidates = Application.query.join(Opportunity).filter(
        Opportunity.company_name == corporate_profile.company_name,
        Application.status == 'Selected'
    ).count()
    
    # Get access validity
    days_left = corporate_profile.days_until_expiry()
    
    stats = {
        'company_name': corporate_profile.company_name,
        'total_posted': total_posted,
        'total_applications': total_applications,
        'selected_candidates': selected_candidates,
        'days_left': days_left,
        'access_expires': corporate_profile.access_until.strftime('%Y-%m-%d'),
    }
    
    return render_template('corporate/dashboard.html', 
                          stats=stats, 
                          corporate_profile=corporate_profile)


@bp.route('/post_opportunity', methods=['GET', 'POST'])
@corporate_required
def post_opportunity():
    """Post a job opportunity."""
    corporate_profile = CorporateProfile.query.filter_by(user_id=session['user_id']).first()
    
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            opp_type = request.form.get('type', '').strip()  # Job, Internship, etc.
            description = request.form.get('description', '').strip()
            requirements = request.form.get('requirements', '').strip()
            ctc = request.form.get('ctc', '').strip()
            min_cgpa = float(request.form.get('min_cgpa', 0))
            allowed_branches = request.form.get('allowed_branches', '').strip()
            deadline_str = request.form.get('deadline', '')
            mode = request.form.get('mode', 'Online').strip()  # Online, Offline, Hybrid
            
            if not all([title, opp_type, description, ctc, deadline_str]):
                flash('All required fields must be filled.', 'danger')
                return redirect(url_for('corporate.post_opportunity'))
            
            deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
            
            # Create opportunity
            opportunity = Opportunity(
                title=title,
                type=opp_type,
                company_name=corporate_profile.company_name,
                organizer=corporate_profile.contact_person,
                description=description,
                requirements=requirements,
                ctc=ctc,
                min_cgpa=min_cgpa,
                allowed_branches=allowed_branches,
                deadline=deadline,
                mode=mode,
                created_at=datetime.utcnow()
            )
            db.session.add(opportunity)
            db.session.commit()
            
            flash(f'Job opportunity "{title}" posted successfully!', 'success')
            return redirect(url_for('corporate.view_opportunities'))
        
        except ValueError as e:
            flash(f'Invalid input: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error posting opportunity: {str(e)}', 'danger')
    
    return render_template('corporate/post_opportunity.html')


@bp.route('/view_opportunities')
@corporate_required
def view_opportunities():
    """View company's posted opportunities."""
    corporate_profile = CorporateProfile.query.filter_by(user_id=session['user_id']).first()
    
    opportunities = Opportunity.query.filter_by(
        company_name=corporate_profile.company_name
    ).order_by(Opportunity.deadline.desc()).all()
    
    return render_template('corporate/view_opportunities.html',
                          opportunities=opportunities)


@bp.route('/view_candidates/<int:opportunity_id>')
@corporate_required
def view_candidates(opportunity_id):
    """View candidates who applied for a job."""
    opportunity = Opportunity.query.get(opportunity_id)
    corporate_profile = CorporateProfile.query.filter_by(user_id=session['user_id']).first()
    
    if not opportunity or opportunity.company_name != corporate_profile.company_name:
        flash('Opportunity not found or access denied.', 'danger')
        return redirect(url_for('corporate.view_opportunities'))
    
    # Get applications
    applications = Application.query.filter_by(opportunity_id=opportunity_id).all()
    
    # Get student details
    candidate_list = []
    for app in applications:
        student = User.query.get(app.student_id)
        profile = StudentProfile.query.filter_by(user_id=app.student_id).first()
        match_score = opportunity.calculate_match_score(profile) if profile else None
        
        candidate_list.append({
            'application': app,
            'student': student,
            'profile': profile,
            'match_score': match_score
        })
    
    return render_template('corporate/view_candidates.html',
                          opportunity=opportunity,
                          candidates=candidate_list)


@bp.route('/update_application_status/<int:application_id>', methods=['POST'])
@corporate_required
def update_application_status(application_id):
    """Update application status."""
    try:
        corporate_profile = CorporateProfile.query.filter_by(user_id=session['user_id']).first()
        application = Application.query.get(application_id)
        
        if not application:
            flash('Application not found.', 'danger')
            return redirect(url_for('corporate.view_opportunities'))
        
        # Verify this is corporate's opportunity
        opportunity = Opportunity.query.get(application.opportunity_id)
        if not opportunity or opportunity.company_name != corporate_profile.company_name:
            flash('Access denied.', 'danger')
            return redirect(url_for('corporate.view_opportunities'))
        
        new_status = request.form.get('status')  # Shortlisted, Selected, Rejected
        if new_status not in ['Shortlisted', 'Selected', 'Rejected']:
            flash('Invalid status.', 'danger')
            return redirect(url_for('corporate.view_candidates', opportunity_id=opportunity.id))
        
        application.status = new_status
        application.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash(f'Application status updated to {new_status}.', 'success')
        return redirect(url_for('corporate.view_candidates', opportunity_id=opportunity.id))
    
    except Exception as e:
        flash(f'Error updating status: {str(e)}', 'danger')
        return redirect(url_for('corporate.view_opportunities'))


@bp.route('/profile')
@corporate_required
def view_profile():
    """View corporate profile."""
    corporate_profile = CorporateProfile.query.filter_by(user_id=session['user_id']).first()
    return render_template('corporate/profile.html', corporate_profile=corporate_profile)


@bp.route('/access_info')
@corporate_required
def access_info():
    """View access information and validity."""
    corporate_profile = CorporateProfile.query.filter_by(user_id=session['user_id']).first()
    
    info = {
        'company_name': corporate_profile.company_name,
        'access_from': corporate_profile.access_from.strftime('%Y-%m-%d %H:%M'),
        'access_until': corporate_profile.access_until.strftime('%Y-%m-%d %H:%M'),
        'days_left': corporate_profile.days_until_expiry(),
        'is_valid': corporate_profile.is_access_valid(),
        'status': 'Active' if corporate_profile.is_access_valid() else 'Expired/Revoked'
    }
    
    return render_template('corporate/access_info.html', access_info=info)
