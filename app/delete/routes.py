from flask import render_template, flash, redirect, url_for, request, Blueprint, abort
from flask_login import current_user, login_user, login_required, logout_user
import sqlalchemy as s_alch

from app import app, db, mail
from ..forms import *
from ..models import *
from . import delete

@delete.route('/delete/<book_id>', methods=['GET', 'POST'])
@login_required
def delete(book_id):
    # Get user info from current_session and book info from <book_id>
    user = db.first_or_404(s_alch.select(User).where(User.username == current_user.username))
    book = db.first_or_404(s_alch.select(Book).where(Book.id == book_id), description="Invalid Book ID")
    form = DeleteBookForm()

    # Ensure that the book belongs to the user

    if form.submit_yes.data:
        if book.owner_id == user.id:

            db.session.delete(book)
            db.session.commit()
                    
            # Let the user know that the change was processed and send them back to their profile
            flash('Deleted {} from your catalog!'.format(book.title))
            return redirect(url_for('user_prof.user', username=current_user.username))
        else:
            # If the book does not belong to the user, I'm not sure what happened.
            flash("Whoops, that book doesn't belong to you!")
            return redirect(url_for('user_prof.user', username=current_user.username))
    if form.submit_no.data:
        return redirect(url_for('user_prof.user', username=current_user.username))

    return render_template('delete.html', form=form, book=book)


