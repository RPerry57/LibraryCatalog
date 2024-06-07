from flask import render_template, flash, redirect, url_for, request, Blueprint, abort
from flask_login import current_user, login_user, login_required, logout_user
import flask_mail as f_mail
from flask_mail import Message
from urllib.parse import urlsplit
import sqlalchemy as s_alch

from app import app, db, mail
from ..forms import *
from ..models import *
from . import user_prof

@user_prof.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    # Select user and their book list. This should never 404 due to @login_required
    user = db.first_or_404(s_alch.select(User).where(User.username == username))
    books = db.session.scalars(user.get_owned_books()).all()

    # If this is the current user's profile
    if current_user.username == username:
        # Create forms for add, edit, delete, and export
        add_form = AddForm()
        export_form = ExportForm()
        
        # If the add button is pressed, send them to the add page
        if add_form.submit_add.data:
            return redirect(url_for('user_prof.user_add', username=current_user.username))

        # If export button is pressed, attempt to send an email to designated email
        if export_form.validate_on_submit():

            target_email = export_form.target_email.data

            # Basic book list message construction
            msg = Message('Library Catalog Share', sender=app.config['ADMINS'][0], recipients=[target_email])
            text = current_user.username + ' shared their Library Catalog with you:\n'

            if len(books) > 0:
                for book in books:
                    text += book.title + ' - ' + book.author + '\n'
            else:
                # Don't let a user send an empty list
                flash("You don't have any books to send!")
                return redirect(url_for('user_prof.user', username=current_user.username))

            msg.body = text
            mail.send(msg)
            flash('Sent your catalog to: ' + target_email)
            # We essentially refresh the page
            return redirect(url_for('user_prof.user', username=current_user.username, own_profile=True))


        # User page with extra forms for current user
        return render_template('user.html', add_form=add_form, export_form=export_form, user=user, books=books, searching=True)

    # Users can view other users' profiles. There is no user search function at the moment, but other profiles can be reached by entering their URLs
    else:
        return render_template('user.html', user=user, books=books, searching=True)

@user_prof.route('/user/<username>/add', methods=['GET', 'POST'])
@login_required
def user_add(username):
    # Make sure this is the user's profile, as these pages can be accessed through URLs
    if current_user.username == username:
        # Again, this should never return a 404
        user = db.first_or_404(s_alch.select(User).where(User.username == username))
        books = db.session.scalars(user.get_owned_books()).all()
    
        # Create Add Book Form
        book_form = AddBookForm()
    
        # Similar to most other forms, if the form validates on submit we can use it. This is handling the 'POST' request
        if book_form.validate_on_submit():
            # Create the book object and add it to the database
            book = Book(owner_id=user.id, title=book_form.title.data, author=book_form.author.data, date_of_purchase=book_form.date_of_purchase.data, notes=book_form.notes.data)
            db.session.add(book)
            db.session.commit()
            flash('Added {} by {} to your collection!'.format(book_form.title.data, book_form.author.data))
            # Send them back to their profile
            return redirect(url_for('user_prof.user', username=current_user.username))
    
        return render_template('user.html', book_form=book_form, user=user, books=books)
    else:
        flash("This profile doesn't belong to you!")
        return redirect(url_for('user_prof.user', username=username))
        
