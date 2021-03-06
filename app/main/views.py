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

from .forms import AddNoteForm, SearchForm

from ..utils.decorators import login_required
from ..utils.functions import *


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


@main.route('/my_notes', methods=['GET', 'POST'])
@login_required
def my_notes():
    """Notes Page"""

    search_form = SearchForm()

    if search_form.validate_on_submit():
        search = request.form['search']
        category = request.form['category']
        return redirect(url_for('main.search_results', search=search, category=category))

    notes = get_notes(session['user_id'])
    usernames = get_usernames()
    folders = get_folder_names_ids(session['user_id'])
    notes_sorted_by_folders = sort_notes_into_folders(notes, folders)
    folder_names = sorted(notes_sorted_by_folders.keys())

    return render_template(
        'main/my_notes.html',
        form=search_form,
        usernames=usernames,
        folder_names=folder_names,
        notes=notes_sorted_by_folders,
        username=session['username']
    )


@main.route('/search_results/?search=<search>&category=<category>')
@login_required
def search_results(search, category):
    """Search results Page"""

    search_form = SearchForm()

    results = get_search_result(search, category, session['user_id'])
    usernames = get_usernames()

    return render_template('main/search_results.html',
                           form=search_form,
                           results=results,
                           usernames=usernames,
                           category=category,
                           username=session['username'])


@main.route("/notes/<note_id>/")
@login_required
def view_note(note_id):
    """Page to view a specific note"""

    if validate_access_to_note(note_id, session['user_id']):
        note = get_note_by_id(note_id)
        can_edit = (note.user_id == int(session['user_id']))
        return render_template('main/view_note.html', note=note, can_edit=can_edit, username=session['username'])
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


@main.route('/notes/edit/<note_id>/', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    """Edit note page"""

    edit_note_form = AddNoteForm()

    note = get_note_by_id(note_id)
    if note.user_id != int(session['user_id']):
        return abort(403)

    user_folders = get_folder_names_ids(session['user_id'])
    edit_note_form.private.default = 'on' if note.private else 'off'
    edit_note_form.folder.choices += user_folders
    edit_note_form.folder.default = note.parent_folder_id
    edit_note_form.note.data = note.body
    edit_note_form.title.data = note.title

    if edit_note_form.validate_on_submit():
        folder_id = int(request.form['folder'])
        title = request.form['title']
        note_markdown = request.form['note']
        private = True if request.form['private'] == 'on' else False

        update_note(note_id, private, folder_id, title, note_markdown)
        return redirect(url_for('main.my_notes'))

    return render_template('main/edit_note.html', form=edit_note_form, note_id=note_id, username=session['username'])


@main.route('/notes/delete/<note_id>/')
@login_required
def delete_note(note_id):
    """Delete note page"""

    # You can only delete notes that you create !!
    note = get_note_by_id(note_id)
    if note is None:
        return abort(404)
    elif note.user_id != session['user_id']:
        return abort(403)
    else:
        delete_note_by_id(note_id)
        return my_notes()


@main.route('/profile')
@login_required
def profile():
    """Profile Page"""

    user = get_user_by_id(session['user_id'])
    return render_template('main/profile.html', username=session['username'], user=user)
