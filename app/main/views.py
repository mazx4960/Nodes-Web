"""
Notes Web App
Copyright (C) 2019 DesmondTan
"""


###########
# Imports #
###########

from . import main

from flask import (
    request, render_template, redirect, session, flash, url_for, abort
)

from .forms import AddNoteForm

from ..utils.decorators import login_required
from ..utils.functions import (
    add_new_note, get_notes, get_note_by_id, validate_access_to_note, get_folder_names_ids
)


#########
# Views #
#########

@main.route('/')
def index():
    """Home Page"""
    try:
        if session['username']:
            return render_template('main/index.html', username=session['username'])
        return render_template('main/index.html', username=None)
    except (KeyError, ValueError):
        return render_template('main/index.html', username=None)


@main.route('/today')
@login_required
def today():
    """
    Today Page:
    Displays all the notifications like the word of the day, news highlights or friends who added you or shared a
    note with you
    """

    return render_template('main/today.html', username=session['username'])


@main.route('/home')
@login_required
def home_page():
    """
    Home Page:
    Displays all the notes that other people has shared in the form of a card
    """

    return render_template('main/home_page.html', username=session['username'])


@main.route('/my_notes')
@login_required
def my_notes():
    """Notes Page"""

    notes = get_notes(session['user_id'])
    return render_template('main/my_notes.html', notes=notes, username=session['username'])


@main.route("/notes/<note_id>/")
@login_required
def view_note(note_id):
    """Page to view a specific note"""

    if validate_access_to_note(note_id, session['user_id']):
        note = get_note_by_id(note_id)
        return render_template('main/view_note.html', note=note, username=session['username'])
    else:
        return abort(403)


@main.route('/notes/add', methods=['GET', 'POST'])
@login_required
def add_note():
    """Adding Notes Page"""

    add_note_form = AddNoteForm()

    user_folders = get_folder_names_ids(session['user_id'])
    add_note_form.folder.choices += user_folders

    if add_note_form.validate_on_submit():
        folder_id = int(request.form['folder'])
        title = request.form['title']
        note_markdown = request.form['note']
        private = True if request.form['private'] == 'on' else False

        add_new_note(private, folder_id, title, note_markdown, session['user_id'])
        return redirect(url_for('main.my_notes'))

    return render_template('main/add_notes.html', form=add_note_form, username=session['username'])


@main.route('/notes/edit/<note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    """Edit note page"""

    pass


@main.route('/notes/delete/<note_id>')
@login_required
def delete_note(note_id):
    """Delete note page"""

    # You can only delete notes that you create !!
    note = get_note_by_id(note_id)
    if note == None:
        return abort(404)
    elif note.user_id == session['user_id']:

        return render_template('main/delete_note.html')
    else:
        abort(403)


@main.route('/profile')
@login_required
def profile():
    """Profile Page"""

    return render_template('main/profile.html', username=session['username'])
