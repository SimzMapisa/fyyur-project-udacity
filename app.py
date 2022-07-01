#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from dateutil import parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from config import SQLALCHEMY_DATABASE_URI
from flask_migrate import Migrate
from extensions import db
from models import Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

with app.app_context():
    db.create_all()

# TODO: connect to a local postgresql database
app.config['SQLACHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'somethingsecret'

migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    data = []

    # quey all venues with entities venue.city and venue.state then group by city and state
    areas = Venue.query.with_entities(
        Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()

    # iterate through areas and create a dictionary for each area
    for area in areas:
        data = []
        # create a list of venues for each area
        venues = Venue.query.filter_by(city=area.city, state=area.state).all()
        # iterate through venues and create a list for each venue
        for venue in venues:
            # get the number of upcoming shows for each venue
            upcoming_shows = Show.query.filter_by(venue_id=venue.id).filter(
                Show.start_time > datetime.now()).count()

            # map the venue data to a dictionary and append to the list
            data.append({
                'id': venue.id,
                'name': venue.name,
                'upcoming_shows': upcoming_shows
            })

            # map the area data to a dictionary and append to the list
        data.append({
            'city': area.city,
            'state': area.state,
            'venues': data
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    search_term = request.form.get('search_term', '')
    # seach for Hop should return "The Musical Hop".

    res = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    response = res if res.count(res) > 0 else res.count(res)
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data = []
    # query the venue with the given venue_id and get the first result
    data = Venue.query.filter(Venue.id == venue_id).first()

    # get the upcoming shows for the venue
    upcoming_shows = Show.query.filter_by(venue_id=venue_id).filter(
        Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()

    # if length of upcoming shows is greater than 0, get the artist for each show
    if len(upcoming_shows) > 0:
        upcoming_shows_data = []
        # iterate through upcoming shows and get the artist for each show_id
        for show in upcoming_shows:
            # get an artist for each show_id
            artist = Artist.query.filter(Artist.id == show.artist_id).first()

            data.append({
                'artist_id': artist.id,
                'artist_name': artist.name,
                'artist_image_link': artist.image_link,
                'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
            })

            data.upcoming_shows = upcoming_shows_data
            data.upcoming_shows_count = len(upcoming_shows_data)
        previous_shows = Show.query.filter_by(venue_id=venue_id).filter(
            Show.start_time < datetime.now()).all()

        if previous_shows.count() > 0:
            previous_shows_data = []
            for show in previous_shows:
                artist = Artist.query.filter(
                    Artist.id == show.artist_id).first()
                previous_shows_data.append({
                    'artist_id': artist.id,
                    'artist_name': artist.name,
                    'artist_image_link': artist.image_link,
                    'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
                })
            data.previous_shows = previous_shows_data
            data.previous_shows_count = len(previous_shows_data)
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------
# define the Genre class

    # create one to many relationship with venue table


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = VenueForm()
    if form.validate_on_submit():
        name = form.name.data
        city = form.city.data
        state = form.state.data
        address = form.address.data
        phone = form.phone.data
        image_link = form.image_link.data
        website_link = form.website_link.data
        facebook_link = form.facebook_link.data
        seeking_talent = form.seeking_talent.data
        seeking_description = form.seeking_description.data
        genres = form.genres.data

        venue = Venue(name=name, city=city, address=address, phone=phone, state=state, facebook_link=facebook_link, image_link=image_link,
                      website=website_link, seeking_talent=seeking_talent, genres=genres, seeking_description=seeking_description)
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
        flash('Error occured. Venue ' +
              request.form['name'] + ' could not be listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@ app.route('/delete/<venue_id>', methods=['GET', 'DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    venue_to_delete = Venue.query.get_or_404(venue_id)

    try:
        db.session.delete(venue_to_delete)
        db.session.commit()
        flash('Venue ' + venue_to_delete.name + ' was successfully deleted!')

        return render_template('pages/home.html')
    except:
        flash('An error occurred. Venue ' +
              venue_to_delete.name + ' could not be deleted.')
        return render_template('pages/show_venue.html', venue=venue_to_delete)
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = []

    # quey all artists  with entities artist.city and artist.state then group by city and state
    artists = Artist.query.with_entities(
        Artist.city, Artist.state).group_by(Artist.city, Artist.state).all()

    # iterate through areas and create a dictionary for each area
    for artist in artists:
        data = []
        # create a list of venues for each area
        artists = Artist.query.filter_by(
            city=artist.city, state=artist.state).all()
        # iterate through venues and create a list for each venue
        for artist in artists:
            # get the number of upcoming shows for each venue
            upcoming_shows = Show.query.filter_by(artist_id=artist.id).filter(
                Show.start_time > datetime.now()).count()

            # map the venue data to a dictionary and append to the list
            data.append({
                'id': artist.id,
                'name': artist.name,
                'upcoming_shows': upcoming_shows
            })

            # map the area data to a dictionary and append to the list
        data.append({
            'city': artist.city,
            'state': artist.state,
            'venues': data
        })
    return render_template('pages/artists.html', artists=data)


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    # seach for Hop should return "The Musical Hop".

    res = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    response = res if res.count(res) > 0 else res.count(res)
    return render_template('pages/search_artist.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    data = []
    # query the venue with the given venue_id and get the first result
    data = Artist.query.filter(Artist.id == artist_id).first()

    # get the upcoming shows for the venue
    upcoming_shows = Show.query.filter_by(artist_id=artist_id).filter(
        Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()

    # if length of upcoming shows is greater than 0, get the artist for each show
    if len(upcoming_shows) > 0:
        upcoming_shows_data = []
        # iterate through upcoming shows and get the artist for each show_id
        for show in upcoming_shows:
            # get an artist for each show_id
            artist = Artist.query.filter(Artist.id == show.artist_id).first()

            data.append({
                'artist_id': artist.id,
                'artist_name': artist.name,
                'genres': artist.genres,
                'artist_image_link': artist.image_link,
                'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
            })

            data.upcoming_shows = upcoming_shows_data
            data.upcoming_shows_count = len(upcoming_shows_data)
        previous_shows = Show.query.filter_by(artist_id=artist_id).filter(
            Show.start_time < datetime.now()).all()

        if previous_shows.count() > 0:
            previous_shows_data = []
            for show in previous_shows:
                artist = Artist.query.filter(
                    Artist.id == show.artist_id).first()
                previous_shows_data.append({
                    'artist_id': artist.id,
                    'artist_name': artist.name,
                    'artist_image_link': artist.image_link,
                    'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
                })
            data.previous_shows = previous_shows_data
            data.previous_shows_count = len(previous_shows_data)

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    artist_to_edit = Artist.query.get_or_404(artist_id)
    if request.method == 'GET':
        form.name.data = artist_to_edit.name
        form.city.data = artist_to_edit.city
        form.state.data = artist_to_edit.state
        form.phone.data = artist_to_edit.phone
        form.genres.data = artist_to_edit.genres
        form.facebook_link.data = artist_to_edit.facebook_link
        form.image_link.data = artist_to_edit.image_link
        form.seeking_venue.data = artist_to_edit.seeking_venue
        form.seeking_description.data = artist_to_edit.seeking_description

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist_to_edit)


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    artist_to_edit = db.session.query(Artist).get_or_404(artist_id)
    form = ArtistForm(Artist=artist_to_edit)

    if request.method == 'POST':
        artist_to_edit.name = form.name.data
        artist_to_edit.city = form.city.data
        artist_to_edit.state = form.state.data
        artist_to_edit.phone = form.phone.data
        artist_to_edit.genres = form.genres.data
        artist_to_edit.facebook_link = form.facebook_link.data
        artist_to_edit.image_link = form.image_link.data
        artist_to_edit.seeking_venue = form.seeking_venue.data
        artist_to_edit.seeking_description = form.seeking_description.data

        try:
            db.session.commit()
            flash('Artist ' + request.form['name'] +
                  ' was successfully updated!')
            return redirect(url_for('show_artist', artist_id=artist_id))
        except:
            db.session.rollback()
            flash('An error occurred. Artist could not be edited.')
            return redirect(url_for('edit_artist', artist_id=artist_id, form=form))
    else:
        return render_template('forms/edit_artist.html', form=form, artist=artist_to_edit)


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    venue_to_edit = Venue.query.get_or_404(venue_id)
    if request.method == 'GET':
        form.name.data = venue_to_edit.name
        form.city.data = venue_to_edit.city
        form.state.data = venue_to_edit.state
        # form.data.address = venue_to_edit.address
        form.phone.data = venue_to_edit.phone
        form.genres.data = venue_to_edit.genres
        form.facebook_link.data = venue_to_edit.facebook_link
        form.image_link.data = venue_to_edit.image_link
        # form.seeking_talent.data = venue_to_edit.seeking_talent
        form.seeking_description.data = venue_to_edit.seeking_description
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue_to_edit)


@ app.route('/venues/<int:venue_id>/edit', methods=['GET', 'POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue_to_edit = db.session.query(Venue).get_or_404(venue_id)
    form = VenueForm(Venue=venue_to_edit)

    if request.method == 'POST':
        venue_to_edit.name = form.name.data
        venue_to_edit.city = form.city.data
        venue_to_edit.state = form.state.data
        venue_to_edit.address = form.address.data
        venue_to_edit.phone = form.phone.data
        venue_to_edit.genres = form.genres.data
        venue_to_edit.facebook_link = form.facebook_link.data
        venue_to_edit.image_link = form.image_link.data
        venue_to_edit.seeking_talent = form.seeking_talent.data
        venue_to_edit.seeking_description = form.seeking_description.data

        try:
            db.session.commit()
            flash('Venue ' + request.form['name'] +
                  ' was successfully updated!')
            return redirect(url_for('show_venue', venue_id=venue_id))
        except:
            db.session.rollback()
            flash('An error occurred. Venue could not be edited.')
            return redirect(url_for('edit_venue', venue_id=venue_id, form=form))
    else:
        return render_template('forms/edit_venue.html', form=form, venue=venue_to_edit)

    #  Create Artist
    #  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = ArtistForm()
    if form.validate_on_submit():
        name = form.name.data
        city = form.city.data
        state = form.state.data
        phone = form.phone.data
        image_link = form.image_link.data
        website_link = form.website_link.data
        facebook_link = form.facebook_link.data
        seeking_venue = form.seeking_venue.data
        seeking_description = form.seeking_description.data
        genres = form.genres.data

        artist = Artist(name=name, city=city, phone=phone, state=state, facebook_link=facebook_link, image_link=image_link,
                        website=website_link, seeking_venue=seeking_venue, genres=genres, seeking_description=seeking_description)
        db.session.add(artist)
        db.session.commit()
    # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    else:
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = [{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
    }]
    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm()
    if form.validate_on_submit():
        try:
            artist_id = form.artist_id.data
            venue_id = form.venue_id.data
            start_time = form.start_time.data
            show = Show(artist_id=artist_id, venue_id=venue_id,
                        start_time=start_time)
            db.session.add(show)
            db.session.commit()

        # on successful db insert, flash success
            flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
        except:
            flash('Show could not be listed! Please double check the information.')
            return render_template('pages/new_show.html')
    else:
        flash('An error occurred. Show could not be listed.')
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
