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
        option_form = OptionForm()
        export_form = ExportForm()
        
        # If an option button is pressed, send them to the appropriate option page
        if option_form.submit_add.data:
            return redirect(url_for('user_prof.user_add', username=current_user.username))
        elif option_form.submit_edit.data:
            return redirect(url_for('user_prof.user_edit', username=current_user.username))
        elif option_form.submit_delete.data:
            return redirect(url_for('user_prof.user_delete', username=current_user.username))

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
            return redirect(url_for('user_prof.user', username=current_user.username))


        # User page with extra forms for current user
        return render_template('user.html', option_form=option_form, export_form=export_form, user=user, books=books, searching=True)

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

@user_prof.route('/user/<username>/edit', methods=['GET', 'POST'])
@login_required
def user_edit(username):
    # Same structure as user_add()
    if current_user.username == username:
        user = db.first_or_404(s_alch.select(User).where(User.username == username))
        books = db.session.scalars(user.get_owned_books()).all()
        book_form = EditBookForm()
        if book_form.validate_on_submit():
            try:
                # Ensure that a number was given as id
                book_id = int(book_form.book_id.data)
            except:
                # If not, let them try again
                flash('Invalid book ID, please try again!')
                return redirect(url_for('user_prof.user_edit', username=current_user.username))
    
            # Attempt to find the book in the database
            book = db.first_or_404(s_alch.select(Book).where(Book.id == book_id), description="Invalid Book ID")
    
            # Ensure that the book belongs to the user
            if book.owner_id == user.id:
    
                # For each of these if statements, update the data only if new information was given.
                if book_form.title.data != '':
                    book.title = book_form.title.data
                    db.session.commit()
                if book_form.author.data != '':
                    book.author = book_form.author.data
                    db.session.commit()
                if book_form.date_of_purchase.data != None:
                    book.date_of_purchase = book_form.date_of_purchase.data
                    db.session.commit()
                if book_form.notes.data != '':
                    book.notes = book_form.notes.data
                    db.session.commit()
                
                # Let the user know that the change was processed and send them back to their profile
                flash('Updated entry for {}!'.format(book.title))
                return redirect(url_for('user_prof.user', username=current_user.username))
            else:
                # If the book does not belong to the user, let them try again
                flash('Invalid book ID, please try again!')
                return redirect(url_for('user_prof.user_edit', username=current_user.username))
        # Show them their list with book_ids listed
        return render_template('user.html', book_form=book_form, user=user, books=books, editing=True)
    else:
        flash("This profile doesn't belong to you!")
        return redirect(url_for('user_prof.user', username=username))
        

@user_prof.route('/user/<username>/delete', methods=['GET', 'POST'])
@login_required
def user_delete(username):
    # Mostly the same as user_edit()
    if current_user.username == username:
        user = db.first_or_404(s_alch.select(User).where(User.username == username))
        books = db.session.scalars(user.get_owned_books()).all()
    
        book_form = DeleteBookForm()
        if book_form.validate_on_submit():
            try:
                book_id = int(book_form.book_id.data)
            except:
                flash('Invalid book ID, please try again!')
            book = db.first_or_404(s_alch.select(Book).where(Book.id == book_id), description="Invalid Book ID")
            if book.owner_id == user.id:
                # If book belongs to the user, delete it
                db.session.delete(book)
                db.session.commit()
                
                # Let the user know that the book was deleted and send them back to their profile
                flash('Deleted {} from your catalog!'.format(book.title))
                return redirect(url_for('user_prof.user', username=current_user.username))
            else:
                flash('Invalid book ID, please try again!')
                return redirect(url_for('user_prof.user_delete', username=current_user.username))
        return render_template('user.html', book_form=book_form, user=user, books=books, deleting=True)
    else:
        flash("This profile doesn't belong to you!")
        return redirect(url_for('user_prof.user', username=username))
