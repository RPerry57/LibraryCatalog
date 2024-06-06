from flask import render_template, flash, redirect, url_for, request, Blueprint, abort
from flask_login import current_user, login_user, login_required, logout_user
import sqlalchemy as s_alch

from app import app, db, mail
from ..forms import *
from ..models import *
from . import edit

@edit.route('/edit/<book_id>', methods=['GET','POST'])
@login_required
def edit(book_id):
    # Get user info from current_session and book info from <book_id>
    user = db.first_or_404(s_alch.select(User).where(User.username == current_user.username))
    book = db.first_or_404(s_alch.select(Book).where(Book.id == book_id), description="Invalid Book ID")
    form = EditBookForm()
    if form.validate_on_submit():    
        # Ensure that the book belongs to the user
        if book.owner_id == user.id:
    
            # For each of these if statements, update the data only if new information was given.
            if form.title.data != '':
                book.title = form.title.data
                db.session.commit()
            if form.author.data != '':
                book.author = form.author.data
                db.session.commit()
            if form.date_of_purchase.data != None:
                book.date_of_purchase = form.date_of_purchase.data
                db.session.commit()
            if form.notes.data != '':
                book.notes = form.notes.data
                db.session.commit()
                
            # Let the user know that the change was processed and send them back to their profile
            flash('Updated entry for {}!'.format(book.title))
            return redirect(url_for('user_prof.user', username=current_user.username))
        else:
            # If the book does not belong to the user, I'm not sure what happened.
            flash("Whoops, that book doesn't belong to you!")
            return redirect(url_for('user_prof.user', username=current_user.username))
    # Show them their list with book_ids listed
    return render_template('edit.html', form=form, user=user, book=book)

