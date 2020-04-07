#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from datetime import *
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import Venue, Artist, Show, setup_db
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = setup_db(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, None, 'en_US')

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
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  venue_query = Venue.query.order_by(Venue.state, Venue.city).all()
  city_and_state = ''
  data = []
  for venue in venue_query:
      upcoming_shows = venue.shows.filter(Show.start_time > current_time).all()
      if city_and_state == venue.city + venue.state:
          data[len(data) - 1]["venues"].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(upcoming_shows)
          })
      else:
          city_and_state = venue.city + venue.state
          data.append({
            "city": venue.city,
            "state": venue.state,
            "venues": [{
              "id": venue.id,
              "name": venue.name,
              "num_upcoming_shows": len(upcoming_shows)
            }]
          })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  venue_query = Venue.query.filter(Venue.name.ilike('%' + request.form['search_term'] + '%'))
  venue_list = list(map(Venue.short, venue_query))
  response = {
      "count": len(venue_list),
      "data": venue_list
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue_query = Venue.query.get(venue_id)
    if venue_query:
        venue_details = Venue.details(venue_query)
        current_time = datetime.now()
        new_shows_query = Show.query.options(db.joinedload(Show.Venue)).filter(Show.venue_id == venue_id).filter(Show.start_time > current_time).all()
        new_shows_list = list(map(Show.artist_details, new_shows_query))
        venue_details["upcoming_shows"] = new_shows_list
        venue_details["upcoming_shows_count"] = len(new_shows_list)
        past_shows_query = Show.query.options(db.joinedload(Show.Venue)).filter(Show.venue_id == venue_id).filter(Show.start_time <= current_time).all()
        past_shows_list = list(map(Show.artist_details, past_shows_query))
        venue_details["past_shows"] = past_shows_list
        venue_details["past_shows_count"] = len(past_shows_list)
        return render_template('pages/show_venue.html', venue=venue_details)
    return render_template('errors/404.html')


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  if form.validate():
    try:
      seeking_talent = False
      seeking_description = ''
      if 'seeking_talent' in request.form:
          seeking_talent = request.form['seeking_talent'] == 'y'
      if 'seeking_description' in request.form:
          seeking_description = request.form['seeking_description']
      new_venue = Venue(
          name=request.form['name'],
          genres=request.form.getlist('genres'),
          address=request.form['address'],
          city=request.form['city'],
          state=request.form['state'],
          phone=request.form['phone'],
          website=request.form['website'],
          facebook_link=request.form['facebook_link'],
          image_link=request.form['image_link'],
          seeking_talent=seeking_talent,
          seeking_description=seeking_description,
      )
      Venue.insert(new_venue)
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except SQLAlchemyError:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  venue_data = Venue.query.get(venue_id)
  if venue_data:
      Venue.delete(venue_data)
  return redirect(url_for('index'))
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artist_query = Artist.query.all()
  artist_list = list(map(Artist.short, artist_query))
  return render_template('pages/artists.html', artists=artist_list)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  artist_query = Artist.query.filter(Artist.name.ilike('%' + request.form['search_term'] + '%'))
  artist_list = list(map(Artist.short, artist_query))
  response = {
    "count": len(artist_list),
    "data": artist_list
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist_query = Artist.query.get(artist_id)
  if artist_query:
      artist_details = Artist.details(artist_query)
      current_time = datetime.now()
      new_shows_query = Show.query.options(db.joinedload(Show.Artist)).filter(Show.artist_id == artist_id).filter(Show.start_time > current_time).all()
      new_shows_list = list(map(Show.venue_details, new_shows_query))
      artist_details["upcoming_shows"] = new_shows_list
      artist_details["upcoming_shows_count"] = len(new_shows_list)
      past_shows_query = Show.query.options(db.joinedload(Show.Artist)).filter(Show.artist_id == artist_id).filter(Show.start_time <= current_time).all()
      past_shows_list = list(map(Show.venue_details, past_shows_query))
      artist_details["past_shows"] = past_shows_list
      artist_details["past_shows_count"] = len(past_shows_list)
      return render_template('pages/show_artist.html', artist=artist_details)
  return render_template('errors/404.html')

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_query = Artist.query.get(artist_id)
  if artist_query:
      artist_details = Artist.details(artist_query)
      form.name.data = artist_details["name"]
      form.genres.data = artist_details["genres"]
      form.city.data = artist_details["city"]
      form.state.data = artist_details["state"]
      form.phone.data = artist_details["phone"]
      form.website.data = artist_details["website"]
      form.facebook_link.data = artist_details["facebook_link"]
      form.seeking_venue.data = artist_details["seeking_venue"]
      form.seeking_description.data = artist_details["seeking_description"]
      form.image_link.data = artist_details["image_link"]
  return render_template('forms/edit_artist.html', form=form, artist=artist_details)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  artist_data = Artist.query.get(artist_id)
  if artist_data:
      if form.validate():
          seeking_venue = False
          seeking_description = ''
          if 'seeking_venue' in request.form:
              seeking_venue = request.form['seeking_venue'] == 'y'
          if 'seeking_description' in request.form:
              seeking_description = request.form['seeking_description']
          setattr(artist_data, 'name', request.form['name'])
          setattr(artist_data, 'genres', request.form.getlist('genres'))
          setattr(artist_data, 'city', request.form['city'])
          setattr(artist_data, 'state', request.form['state'])
          setattr(artist_data, 'phone', request.form['phone'])
          setattr(artist_data, 'website', request.form['website'])
          setattr(artist_data, 'facebook_link', request.form['facebook_link'])
          setattr(artist_data, 'image_link', request.form['image_link'])
          setattr(artist_data, 'seeking_description', seeking_description)
          setattr(artist_data, 'seeking_venue', seeking_venue)
          Artist.update(artist_data)
          return redirect(url_for('show_artist', artist_id=artist_id))
      else:
          print(form.errors)
  return render_template('errors/404.html'), 404

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_query = Venue.query.get(venue_id)
  if venue_query:
      venue_details = Venue.details(venue_query)
      form.name.data = venue_details["name"]
      form.genres.data = venue_details["genres"]
      form.address.data = venue_details["address"]
      form.city.data = venue_details["city"]
      form.state.data = venue_details["state"]
      form.phone.data = venue_details["phone"]
      form.website.data = venue_details["website"]
      form.facebook_link.data = venue_details["facebook_link"]
      form.seeking_talent.data = venue_details["seeking_talent"]
      form.seeking_description.data = venue_details["seeking_description"]
      form.image_link.data = venue_details["image_link"]
      return render_template('forms/edit_venue.html', form=form, venue=venue_details)
  return render_template('errors/404.html'), 404

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  venue_data = Venue.query.get(venue_id)
  if venue_data:
      if form.validate():
          seeking_talent = False
          seeking_description = ''
          if 'seeking_talent' in request.form:
              seeking_talent = request.form['seeking_talent'] == 'y'
          if 'seeking_description' in request.form:
              seeking_description = request.form['seeking_description']
          setattr(venue_data, 'name', request.form['name'])
          setattr(venue_data, 'genres', request.form.getlist('genres'))
          setattr(venue_data, 'address', request.form['address'])
          setattr(venue_data, 'city', request.form['city'])
          setattr(venue_data, 'state', request.form['state'])
          setattr(venue_data, 'phone', request.form['phone'])
          setattr(venue_data, 'website', request.form['website'])
          setattr(venue_data, 'facebook_link', request.form['facebook_link'])
          setattr(venue_data, 'image_link', request.form['image_link'])
          setattr(venue_data, 'seeking_description', seeking_description)
          setattr(venue_data, 'seeking_talent', seeking_talent)
          Venue.update(venue_data)
          return redirect(url_for('show_venue', venue_id=venue_id))
      else:
          print(form.errors)
  return render_template('errors/404.html'), 404

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    seeking_venue = False
    seeking_description = ''
    if 'seeking_venue' in request.form:
        seeking_venue = request.form['seeking_venue'] == 'y'
    if 'seeking_description' in request.form:
        seeking_description = request.form['seeking_description']
    new_artist = Artist(name=request.form['name'],
                        genres=request.form.getlist('genres'),
                        city=request.form['city'],
                        state=request.form['state'],
                        phone=request.form['phone'],
                        website=request.form['website'],
                        facebook_link=request.form['facebook_link'],
                        image_link=request.form['image_link'],
                        seeking_venue=seeking_venue,
                        seeking_description=seeking_description)
    Artist.insert(new_artist)
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except SQLAlchemyError as e:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows_query = Show.query.all()
  shows_list = list(map(Show.details, shows_query))
  
  return render_template('pages/shows.html', shows=shows_list)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
      new_show = Show(venue_id=request.form['venue_id'],
                      artist_id=request.form['artist_id'],
                      start_time=request.form['start_time'])
      Show.insert(new_show)
      # on successful db insert, flash success
      flash('Show was successfully listed!')
  except SQLAlchemyError as e:
        flash('An error occurred. Show could not be listed.')
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
