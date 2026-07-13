from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from models import get_db

user_bp = Blueprint('user', __name__)

def user_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('role') != 'user':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrap

@user_bp.route('/dashboard')
@user_required
def dashboard():
    uid = session['user_id']
    db = get_db()
    open_treks = db.execute("SELECT * FROM treks WHERE status='Open'").fetchall()
    my_bookings = db.execute("""SELECT b.*, t.name as trek_name, t.location, t.start_date, t.status as trek_status
                                FROM bookings b JOIN treks t ON b.trek_id=t.id
                                WHERE b.user_id=? ORDER BY b.booking_date DESC""", (uid,)).fetchall()
    db.close()
    return render_template('user/dashboard.html', treks=open_treks, bookings=my_bookings)

@user_bp.route('/treks')
@user_required
def treks():
    difficulty = request.args.get('difficulty', '')
    location = request.args.get('location', '')
    query = "SELECT * FROM treks WHERE status='Open'"
    params = []
    if difficulty:
        query += " AND difficulty=?"
        params.append(difficulty)
    if location:
        query += " AND location LIKE ?"
        params.append(f'%{location}%')
    db = get_db()
    rows = db.execute(query, params).fetchall()
    db.close()
    return render_template('user/treks.html', treks=rows, difficulty=difficulty, location=location)

@user_bp.route('/trek/<int:tid>/book', methods=['POST'])
@user_required
def book_trek(tid):
    uid = session['user_id']
    db = get_db()
    trek = db.execute("SELECT * FROM treks WHERE id=?", (tid,)).fetchone()
    if not trek:
        flash('Trek not found.')
        return redirect(url_for('user.treks'))
    if trek['status'] != 'Open':
        flash('Trek is not open for booking.')
        return redirect(url_for('user.treks'))
    booked = db.execute("SELECT COUNT(*) as c FROM bookings WHERE trek_id=? AND status='Booked'", (tid,)).fetchone()['c']
    if booked >= trek['slots']:
        flash('Trek is fully booked.')
        return redirect(url_for('user.treks'))
    existing = db.execute("SELECT * FROM bookings WHERE user_id=? AND trek_id=? AND status='Booked'", (uid, tid)).fetchone()
    if existing:
        flash('You have already booked this trek.')
        return redirect(url_for('user.treks'))
    db.execute("INSERT INTO bookings (user_id, trek_id) VALUES (?, ?)", (uid, tid))
    db.commit()
    db.close()
    flash('Trek booked successfully.')
    return redirect(url_for('user.dashboard'))

@user_bp.route('/booking/<int:bid>/cancel', methods=['POST'])
@user_required
def cancel_booking(bid):
    uid = session['user_id']
    db = get_db()
    booking = db.execute("SELECT * FROM bookings WHERE id=? AND user_id=?", (bid, uid)).fetchone()
    if booking and booking['status'] == 'Booked':
        db.execute("UPDATE bookings SET status='Cancelled' WHERE id=?", (bid,))
        db.commit()
        flash('Booking cancelled.')
    db.close()
    return redirect(url_for('user.dashboard'))

@user_bp.route('/history')
@user_required
def history():
    uid = session['user_id']
    db = get_db()
    rows = db.execute("""SELECT b.*, t.name as trek_name, t.location, t.start_date, t.end_date
                         FROM bookings b JOIN treks t ON b.trek_id=t.id
                         WHERE b.user_id=? ORDER BY b.booking_date DESC""", (uid,)).fetchall()
    db.close()
    return render_template('user/history.html', bookings=rows)

@user_bp.route('/profile', methods=['GET', 'POST'])
@user_required
def profile():
    uid = session['user_id']
    db = get_db()
    if request.method == 'POST':
        db.execute("UPDATE users SET name=?, email=? WHERE id=?",
                   (request.form['name'], request.form['email'], uid))
        db.commit()
        session['name'] = request.form['name']
        flash('Profile updated.')
        return redirect(url_for('user.profile'))
    user = db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    db.close()
    return render_template('user/profile.html', user=user)
