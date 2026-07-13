from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from models import get_db

staff_bp = Blueprint('staff', __name__)

def staff_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('role') != 'staff':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrap

@staff_bp.route('/dashboard')
@staff_required
def dashboard():
    sid = session['user_id']
    db = get_db()
    treks = db.execute("SELECT * FROM treks WHERE staff_id=?", (sid,)).fetchall()
    result = []
    for t in treks:
        count = db.execute("SELECT COUNT(*) as c FROM bookings WHERE trek_id=? AND status='Booked'", (t['id'],)).fetchone()['c']
        trek_dict = dict(t)
        trek_dict['registered'] = count
        result.append(trek_dict)
    db.close()
    return render_template('staff/dashboard.html', treks=result)

@staff_bp.route('/trek/<int:tid>/update', methods=['POST'])
@staff_required
def update_trek(tid):
    db = get_db()
    trek = db.execute("SELECT * FROM treks WHERE id=?", (tid,)).fetchone()
    if not trek or trek['staff_id'] != session['user_id']:
        flash('Not authorized.')
        return redirect(url_for('staff.dashboard'))
    db.execute("UPDATE treks SET slots=?, status=? WHERE id=?",
               (request.form['slots'], request.form['status'], tid))
    db.commit()
    db.close()
    flash('Trek updated.')
    return redirect(url_for('staff.dashboard'))

@staff_bp.route('/trek/<int:tid>/participants')
@staff_required
def participants(tid):
    sid = session['user_id']
    db = get_db()
    trek = db.execute("SELECT * FROM treks WHERE id=?", (tid,)).fetchone()
    if not trek or trek['staff_id'] != sid:
        flash('Not authorized.')
        return redirect(url_for('staff.dashboard'))
    parts = db.execute("""SELECT u.id, u.name, u.email, b.status, b.booking_date
                          FROM bookings b JOIN users u ON b.user_id=u.id
                          WHERE b.trek_id=?""", (tid,)).fetchall()
    db.close()
    return render_template('staff/participants.html', trek=trek, participants=parts)
