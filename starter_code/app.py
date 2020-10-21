
#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    venue_show = db.relationship('Shows', backref='venue_show')

    def __repr__(self):
        return f'< Venue id: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, address: {self.address},phone: {self.phone}, genres: {self.genres}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, website: {self.website}, seeking_description: {self.seeking_description}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    artist_show = db.relationship('Shows', backref='artist_show')

    def __repr__(self):
        return f'< Artist id: {self.id}, name: {self.name}, city: {self.city}, state: {self.state},phone: {self.phone}, genres: {self.genres}, image_link: {self.image_link}, facebook_link: {self.facebook_link},website: {self.website}, seeking_description: {self.seeking_description} >'

# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Shows(db.Model):
    __tablename__ = 'shows'

    show_id = db.Column(db.Integer, primary_key=True, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id', ondelete="CASCADE"))
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id', ondelete="CASCADE"))
    venue_name = db.Column(db.String)
    artist_name = db.Column(db.String)
    artist_image_link = db.Column(db.String(500))
    venue_image_link = db.Column(db.String(500))
    start_time = db.Column(db.DateTime())

    def __repr__(self):
        return f'<Shows show_id: {self.show_id}, artist_id: {self.artist_id}, venue_id: {self.venue_id}, start_time: {self.start_time}>'

#-------------- --------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


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
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    venue_data = Venue.query.all()
    data = []

    for i in venue_data:
        data.append({
            "city": i.city,
            "state": i.state,
            "venues": [{"id": i.id,
                        "name": i.name,
                        "num_upcoming_shows": len(db.session.query(Shows).filter(Shows.venue_id == i.id).filter(
                            Shows.start_time > datetime.now()).all())}]})

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    # Pseudo code:
    # 1- search about the word 'music'
    # 2- loop in the database to find that paticular word
    # 3- desplay what found
    # 4- count the upcoming shows
    search_term = request.form.get('search_term', '')

    venue_search = Venue.query.filter(
        Venue.name.ilike(f'%{search_term}%')).all()

    data = []
    for v in venue_search:

        data.append({
            "name": v.name,
            "id": v.id,
            "num_upcoming_shows": len(db.session.query(Shows).filter(Shows.venue_id == v.id).filter(
                Shows.start_time > datetime.now()).all())
        })

    response = {
        "count": len(venue_search),
        "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    venue = Venue.query.get(venue_id)
    data = []

    past_shows = (db.session.query(Shows).filter(Shows.venue_id == venue_id).filter(
        Shows.start_time < datetime.now()).all())
    past = []

    coming_shows = (db.session.query(Shows).filter(Shows.venue_id == venue_id).filter(
        Shows.start_time > datetime.now()).all())
    coming = []

    for i in past_shows:
        past.append({
            "artist_id": i.artist_id,
            "artist_name": i.artist_name,
            "artist_image_link": i.artist_image_link,
            "start_time": i.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    for i in coming_shows:
        coming.append({
            "artist_id": i.artist_id,
            "artist_name": i.artist_name,
            "artist_image_link": i.artist_image_link,
            "start_time": i.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past,
        "upcoming_shows": coming,
        "past_shows_count": len(past),
        "upcoming_shows_count": len(coming)
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False
    try:
        new = Venue(
            name=request.form.get('name'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            address=request.form.get('address'),
            genres=request.form.getlist('genres'),
            phone=request.form.get('phone'),
            facebook_link=request.form.get('facebook_link'),
            website=request.form.get('website'),
            seeking_description=request.form.get('seeking_description'),
            image_link=request.form.get('image_link')
        )

        db.session.add(new)
        db.session.commit()

    except():
        db.session.rollback()
        error = True
        print(sys.exc_info())
        flash('An error occurred. Venue ' +
              data.name + ' could not be listed.')
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')
    # on successful db insert, flash success
    # flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    error = False
    try:

        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash('Venue, ' + name + ' successfully deleted.')
        return render_template('pages/home.html')

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    # Pseudo code:
    # 1- retriving data from the database
    # 2- represent it as name and id

    artists = Artist.query.all()
    data = []

    for a in artists:
        data.append({
            "name": a.name,
            "id": a.id
        })

    print(data)

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')

    artist_search = Artist.query.filter(
        Artist.name.ilike(f'%{search_term}%')).all()

    data = []
    for a in artist_search:

        data.append({
            "name": a.name,
            "id": a.id,
            "num_upcoming_shows": len(db.session.query(Shows).filter(Shows.artist_id == a.id).filter(
                Shows.start_time > datetime.now()).all())
        })

    response = {
        "count": len(artist_search),
        "data": data
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    artist = Artist.query.get(artist_id)
    data = []

    past_shows = (db.session.query(Shows).filter(Shows.artist_id == artist_id).filter(
        Shows.start_time < datetime.now()).all())
    past = []

    coming_shows = (db.session.query(Shows).filter(Shows.artist_id == artist_id).filter(
        Shows.start_time > datetime.now()).all())
    coming = []

    for i in past_shows:
        past.append({
            "venue_id": i.venue_id,
            "venue_name": i.venue_name,
            "venue_image_link": i.venue_image_link,
            "start_time": i.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    for i in coming_shows:
        coming.append({
            "venue_id": i.venue_id,
            "venue_name": i.venue_name,
            "venue_image_link": i.venue_image_link,
            "start_time": i.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past,
        "upcoming_shows": coming,
        "past_shows_count": len(past),
        "upcoming_shows_count": len(coming)
    }
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    artist = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    artist.name = request.form['name']
    artist.genres = request.form.getlist('genres')
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.website = request.form['website']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_description = request.form['seeking_description']
    artist.image_link = request.form['image_link']

    db.session.commit()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    venue = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link
    }

    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    venue.name = request.form['name']
    venue.genres = request.form.getlist('genres')
    venue.address = request.form['address']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.website = request.form['website']
    venue.facebook_link = request.form['facebook_link']
    venue.seeking_description = request.form['seeking_description']
    venue.image_link = request.form['image_link']

    db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False
    try:
        new = Artist(
            name=request.form.get('name'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            phone=request.form.get('phone'),
            genres=request.form.getlist('genres'),
            website=request.form.get('website'),
            seeking_description=request.form.get('seeking_description'),
            image_link=request.form.get('image_link'),
            facebook_link=request.form.get('facebook_link'))

        db.session.add(new)
        db.session.commit()

    except():
        db.session.rollback()
        error = True
        print(sys.exc_info())
        flash('An error occurred. Artist ' +
              data.name + ' could not be listed.')
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    show = Shows.query.all()
    data = []

    for s in show:
        data.append({
            "venue_id": s.venue_id,
            "venue_name": s.venue_name,
            "artist_id": s.artist_id,
            "artist_name": s.artist_name,
            "artist_image_link": s.artist_image_link,
            "start_time": s.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create', methods=['GET'])
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    error = False
    try:
        new = Shows(
            artist_id=request.form.get('artist_id'),
            venue_id=request.form.get('venue_id'),
            start_time=request.form.get('start_time'),
            venue_name=request.form.get('venue_name'),
            artist_name=request.form.get('artist_name'),
            artist_image_link=request.form.get('artist_image_link'),
            venue_image_link=request.form.get('venue_image_link')
        )

        db.session.add(new)
        db.session.commit()

    except():
        db.session.rollback()
        error = True
        print(sys.exc_info())
        flash('An error occurred. Show could not be listed.')

    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash('Show was successfully listed!')
        return render_template('pages/home.html')

    # on successful db insert, flash success
    # flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
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
    app.run()

# Or specify port manually:
'''


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
