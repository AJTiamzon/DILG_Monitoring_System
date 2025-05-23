from flask import Blueprint, render_template, request, flash, jsonify, url_for, redirect
from flask_login import login_required, current_user
from .models import db, Note, Barangay_Names, Brngy_files4, SubjectLinks3
from sqlalchemy import distinct, func
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 
        
        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user, notes= Note.query.all())


@views.route('/create_barang', methods=['POST', 'GET'])
@login_required
def create_barang():
    if request.method == 'POST':
        barang_names = Barangay_Names.query.all()  # Get all barangay names
        added_by = request.form.get('added_by')
        year = int(request.form.get('year'))
        month = request.form.get('month')
        creating_record = Brngy_files4.query.filter_by(year=year, month=month).first()

        if not added_by or not month or not year:
            flash('Fill Out All Fields!', category='error')

        elif not isinstance(year, int) and year < 2020:
            flash('Year Must Be A Number And At Least 2020!', category='error')
        
        elif creating_record:
            flash('Record Already Exists', category='error')

        else:
            barang_entries = []  # Store all entries first
            for name in barang_names:
                new_barang_month = Brngy_files4(
                    barang_name=name.barang_name,  # Correct way to access name
                    added_by=added_by, 
                    year=year, 
                    month=month,
                    road_clearing='unedited', kp='unedited', vawc='unedited',
                    first_time_job_seeking='unedited', bfdp='unedited',
                    kasambahay='unedited', manila_bay_w1='unedited',
                    manila_bay_w2='unedited', manila_bay_w3='unedited',
                    manila_bay_w4='unedited', manila_bay_w5='unedited',
                    kalinisan_w1='unedited', kalinisan_w2='unedited', kalinisan_w3='unedited',
                    kalinisan_w4='unedited', kalinisan_w5='unedited'
                )
                barang_entries.append(new_barang_month)  # Add entry to list
            
            db.session.bulk_save_objects(barang_entries)  # Bulk insert for better performance
            db.session.commit()  # Commit once
            flash('Barangay added!', category='success')

        return render_template("create_barang.html", user=current_user)

    return render_template("create_barang.html", user=current_user)

@views.route('/barang_list', methods=['POST', 'GET'])
@login_required
def barang_list():
    barang_files = Brngy_files4.query.all()

    # Collecting the year dates
    barang_years1 = []
    for barang in barang_files:
        year_str = str(barang.year)  # Convert year to string first
        if year_str not in barang_years1:
            barang_years1.append(year_str)

    if request.method == 'POST':
        for barangay in barang_files:
            barangay_id = barangay.id
            barangay_to_update = Brngy_files4.query.get(barangay_id)

            if barangay_to_update:
                # Retrieve form data with fallback to existing values
                barangay_to_update.road_clearing = request.form.get(f'road_clearing_{barangay_id}', barangay_to_update.road_clearing)
                barangay_to_update.kp = request.form.get(f'kp_{barangay_id}', barangay_to_update.kp)
                barangay_to_update.vawc = request.form.get(f'vawc_{barangay_id}', barangay_to_update.vawc)
                barangay_to_update.first_time_job_seeking = request.form.get(f'first_time_job_seeking_{barangay_id}', barangay_to_update.first_time_job_seeking)
                barangay_to_update.bfdp = request.form.get(f'bfdp_{barangay_id}', barangay_to_update.bfdp)
                barangay_to_update.kasambahay = request.form.get(f'kasambahay_{barangay_id}', barangay_to_update.kasambahay)

                # Loop through weekly fields dynamically
                for week in range(1, 6):
                    setattr(barangay_to_update, f'manila_bay_w{week}', request.form.get(f'manila_bay_w{week}_{barangay_id}', getattr(barangay_to_update, f'manila_bay_w{week}')))
                    setattr(barangay_to_update, f'kalinisan_w{week}', request.form.get(f'kalinisan_w{week}_{barangay_id}', getattr(barangay_to_update, f'kalinisan_w{week}')))

        db.session.commit()
        flash('Barangay details updated successfully!', category='success')
        return redirect(url_for("views.barang_list"))
    return render_template("barangay_list.html", user=current_user, barang_files=barang_files, barang_years1=barang_years1)

@views.route('/find_barangay', methods=['POST', 'GET'])
@login_required
def find_barangay():
    barang_files = Brngy_files4.query.all()
    barang_names = Barangay_Names.query.all()

    barang_years1 = []
    for barang in barang_files:
        if barang.year not in barang_years1:
            barang_years1.append(barang.year)

    if request.method =='POST':
        year = request.form.get('barangay_year')
        month = request.form.get('barangay_month')
        barangay = request.form.get('barangay_name')

        selected_barang = Brngy_files4.query.filter_by(year=year, month=month, barang_name=barangay).first()

        return render_template("find_barangay.html", user=current_user, barang_years1=barang_years1, barang_names=barang_names, selected_barang=selected_barang)

    return render_template("find_barangay.html", user=current_user, barang_years1=barang_years1, barang_names=barang_names)

@views.route('/barangay_charts', methods=['GET', 'POST'])
@login_required
def barangay_charts():
    #Store the required information into variables
    barang_files = Brngy_files4.query.all()
    barangay_names = Barangay_Names.query.all()
    
    #Setup the months to be used and get the user inputs for whih specific year and month
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    year_req = request.form.get("year_req")
    month_req = request.form.get("month_req")

    #Storing all of the unique years into a variable and set() removes any duplicates
    barang_years1 = list(set([barang.year for barang in barang_files]))  # Get The Unique Years

    #Get all of the barangays with the specified month and year
    if year_req and month_req:
        filtered_barangays = Brngy_files4.query.filter_by(year=year_req, month=month_req).all()
    else:
        filtered_barangays = []

    barangay_chart_data = {}

    # Define fields to check for "Late", "Completed", and "Others"
    fields_to_check = [
        "road_clearing", "kp", "vawc", "first_time_job_seeking",
        "bfdp", "kasambahay", "manila_bay_w1", "manila_bay_w2",
        "manila_bay_w3", "manila_bay_w4", "manila_bay_w5", "kalinisan_w1",
        "kalinisan_w2", "kalinisan_w3", "kalinisan_w4", "kalinisan_w5"
    ]

    #Setup the dictionary by going through each baragay of the proper date and adding them to it
    for barang in filtered_barangays:
        if barang.barang_name not in barangay_chart_data:
            barangay_chart_data[barang.barang_name] = {"Late": 0, "Completed": 0, "Others": 0}

        #After that, we check store each value of the field to check 
        for field in fields_to_check:
            value = getattr(barang, field)

            #Now we start counting values
            #The lower() function removes LATE vs late coplication
            if value and value.lower() == "late":
                barangay_chart_data[barang.barang_name]["Late"] += 1
            elif value and value.lower() == "completed":
                barangay_chart_data[barang.barang_name]["Completed"] += 1
            else:
                barangay_chart_data[barang.barang_name]["Others"] += 1

    return render_template("charts.html",
                           user=current_user,
                           barangay_names=barangay_names,
                           barang_years1=barang_years1,
                           months=months,
                           barangay_chart_data=barangay_chart_data)

@views.route('/barangay_creation_records', methods=['GET', 'POST'])
@login_required
def barangay_creation_records():
    # Get distinct month-year pairs
    subquery = (
        db.session.query(
            Brngy_files4.month,
            Brngy_files4.year,
            func.min(Brngy_files4.id).label("min_id")
        )
        .group_by(Brngy_files4.month, Brngy_files4.year)
        .subquery()
    )

    barang_files = (
        db.session.query(Brngy_files4)
        .join(subquery, Brngy_files4.id == subquery.c.min_id)
        .order_by(Brngy_files4.date.desc())  # This line does the magic
        .all()
    )
    return render_template("barangay_creation_records.html", user=current_user, barang_files=barang_files)

@views.route('/barangay_link', methods=['GET', 'POST'])
def barangay_link():
    barangay_names = Barangay_Names.query.all()
    fields_to_check = [
        "road_clearing", "kp", "vawc", "first_time_job_seeking",
        "bfdp", "kasambahay", "manila_bay_w1", "manila_bay_w2",
        "manila_bay_w3", "manila_bay_w4", "manila_bay_w5", "kalinisan_w1",
        "kalinisan_w2", "kalinisan_w3", "kalinisan_w4", "kalinisan_w5"
    ]

    barangay_status = None
    submitted_links = []

    if request.method == 'POST':
        barang_name = request.form.get('name')
        subject = request.form.get('subject')
        link = request.form.get('link')
        month = request.form.get('month')
        year = request.form.get('year')
        added_by = current_user.first_name

        barang_to_edit = Brngy_files4.query.filter_by(
            year=year, month=month, barang_name=barang_name
        ).first()

        if barang_to_edit:
            existing_link = SubjectLinks3.query.filter_by(year=year, month=month, subject=subject, 
                                                          barangay_id = barang_to_edit.id).first()
            
            if existing_link:
                existing_link.link = link
                existing_link.added_by = added_by
                flash('Link Succesfully Updated', category='success')
                
            else:
                link_to_submit = SubjectLinks3(
                    year=year,
                    month=month,
                    subject=subject,
                    link=link,
                    added_by=added_by,
                    barangay=barang_to_edit
                )
                db.session.add(link_to_submit)
                flash('Link Submitted Succesfully', category='success')

                for field in fields_to_check:
                    if field == subject:
                        setattr(barang_to_edit, field, 'submitted')

            db.session.commit()
        else:
            flash('That Month Has Not Yet Been Added, Please Make Sure To Input Proper Barangay Name, Year And Month', category='error')

    return render_template(
        "barangay_link.html",user=current_user,barangay_names=barangay_names,submitted_links=submitted_links)

@views.route('/barangay_names', methods=['GET', 'POST'])
@login_required
def barangay_names():
    barangay_names = Barangay_Names.query.all()
    return render_template("barangay_names.html", user=current_user, barangay_names=barangay_names)

############################################### Action ####################################################################
############################################### Routes ####################################################################

@views.route('/find_barangay_year_month', methods=['POST', 'GET'])
@login_required
def find_barangay_year_month():
    barang_files = Brngy_files4.query.all()
    # barang_links = SubjectLinks3.query.all()

    barang_years1 = []
    for barang in barang_files:
        if barang.year not in barang_years1:
            barang_years1.append(barang.year)

    if request.method == 'POST':
        year = request.form.get('barangay_year')
        month = request.form.get('barangay_month')
        barang_links = SubjectLinks3.query.filter_by(year=year, month=month).all()

        month_year_list = Brngy_files4.query.filter_by(year=year, month=month).all()

        return render_template("barangay_list.html", user=current_user, barang_years1=barang_years1, barang_files=barang_files, month_year_list=month_year_list, barang_links=barang_links)

    return render_template("barangay_list.html", user=current_user, barang_years1=barang_years1, barang_files=barang_files, barang_links=barang_links)

@views.route('/find_barangay_save_changes', methods=['POST'])
@login_required
def find_barangay_save_changes():
    if request.method == 'POST':
        year = request.form.get('selected_barang_year')
        month = request.form.get('selected_barang_month')
        barang_name = request.form.get('selected_barang_name')

        barangay_to_edit = Brngy_files4.query.filter_by(year=year, month=month, barang_name=barang_name).first()

        # Check if a matching record is found
        if not barangay_to_edit:
            flash("No matching barangay record found.", "error")
            return redirect(url_for('views.find_barangay'))

        barangay_to_edit_id = barangay_to_edit.id
        
        if barangay_to_edit:
            barangay_to_edit.road_clearing = request.form.get(f'road_clearing_{ barangay_to_edit_id }')
            barangay_to_edit.kp = request.form.get(f'kp_{ barangay_to_edit_id }')
            barangay_to_edit.vawc = request.form.get(f'vawc_{ barangay_to_edit_id }')
            barangay_to_edit.first_time_job_seeking = request.form.get(f'first_time_job_seeking_{ barangay_to_edit_id }')
            barangay_to_edit.bfdp = request.form.get(f'bfdp_{ barangay_to_edit_id }')
            barangay_to_edit.kasambahay = request.form.get(f'kasambahay_{ barangay_to_edit_id }')

            for week in range(1, 6):
                setattr(barangay_to_edit, f'manila_bay_w{week}', request.form.get(f'manila_bay_w{ week }_{ barangay_to_edit_id }'))
                setattr(barangay_to_edit, f'kalinisan_w{week}', request.form.get(f'manila_bay_w{ week }_{ barangay_to_edit_id }'))

        db.session.commit()

        # Fetch updated data and render the template with the selected barangay
        barang_files = Brngy_files4.query.all()
        barang_names = Barangay_Names.query.all()

        barang_years1 = list(set([barang.year for barang in barang_files]))

        return render_template("find_barangay.html", user=current_user, barang_years1=barang_years1, 
                               barang_names=barang_names, selected_barang=barangay_to_edit)
    return redirect(url_for('views.find_barangay'))

@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/delete_barangay', methods=['POST'])
@login_required
def delete_barangay():
    year = request.form.get('year')
    month = request.form.get('month')

    if year and month:
        barang_list = Brngy_files4.query.filter_by(year=year, month=month).all()
        if barang_list:
            for barang in barang_list:
                # Delete associated SubjectLinks3 records first
                subject_links = SubjectLinks3.query.filter_by(barangay_id=barang.id).all()
                for link in subject_links:
                    db.session.delete(link)
                
                # Then delete the barangay entry
                db.session.delete(barang)

            db.session.commit()
            flash('All barangay records and their links for that month deleted successfully!', category='success')
        else:
            flash('No barangay records found for that month!', category='danger')
    else:
        flash('Invalid request!', category='danger')

    return redirect(url_for("views.barangay_creation_records"))