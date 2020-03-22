from sqlalchemy import Column, String, Integer, Boolean, DateTime, ARRAY, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import *
db = SQLAlchemy()

def setup_db(app):
    db.app = app
    db.init_app(app)
    app.config.from_object('config')
    migrate = Migrate(app, db)

    
    return db

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    genres = Column(ARRAY(String))
    address = Column(String(120))
    city = Column(String(120))
    state = Column(String(120))
    address = Column(String(120))
    phone = Column(String(120))
    website = Column(String(120))
    facebook_link = Column(String(120))
    seeking_talent = Column(Boolean)
    seeking_description = Column(String(500))
    image_link = Column(String(500))
    shows = db.relationship('Show', backref='Venue', lazy='dynamic')

    def __init__(self, name, genres, address, city, state, phone, website, facebook_link, image_link,
                 seeking_talent=False, seeking_description=""):
        self.name = name
        self.genres = genres
        self.address = address
        self.city = city
        self.state = state
        self.phone = phone
        self.website = website
        self.facebook_link = facebook_link
        self.seeking_talent = seeking_talent
        self.seeking_description = seeking_description
        self.image_link = image_link

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def short(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    def long(self):
        print(self)
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
        }

    def details(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,
        }
    
    

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    genres = Column(ARRAY(String))
    city = Column(String(120))
    state = Column(String(120))
    phone = Column(String(120))
    website = Column(String(120))
    facebook_link = Column(String(120))
    seeking_venue =  Column(Boolean)
    seeking_description =  Column(String(500))
    image_link = Column(String(500))
    shows = db.relationship('Show', backref='Artist', lazy='dynamic')

    def __init__(self, id, name, genres, city, state, phone, website, facebook_link, image_link,
                 seeking_venue=False, seeking_description=""):
        self.id = id
        self.name = name
        self.genres = genres
        self.city = city
        self.state = state
        self.phone = phone
        self.website = website
        self.facebook_link = facebook_link
        self.seeking_venue = seeking_venue
        self.seeking_description = seeking_description
        self.image_link = image_link

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def short(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    def details(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,
        }



class Show(db.Model):
    __tablename__ = 'Show'

    id = Column(Integer, primary_key=True)
    venue_id = Column(Integer, ForeignKey('Venue.id'))
    artist_id = Column(Integer, ForeignKey('Artist.id'))
    start_time = Column(DateTime, nullable=False)

    def __init__(self, venue_id, artist_id, start_time):
        self.venue_id = venue_id
        self.artist_id = artist_id
        self.start_time = start_time

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def details(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.Venue.name,
            'artist_id': self.artist_id,
            'artist_name': self.Artist.name,
            'artist_image_link': self.Artist.image_link,
            'start_time': self.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        }

    def artist_details(self):
        return {
            'artist_id': self.artist_id,
            'artist_name': self.Artist.name,
            'artist_image_link': self.Artist.image_link,
            'start_time': self.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        }

    def venue_details(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.Venue.name,
            'venue_image_link': self.Venue.image_link,
            'start_time': self.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        }

def insert_venues():
    ven1 = Venue("The Musical Hop", ["Jazz", "Reggae", "Swing", "Classical", "Folk"], 
                 "1015 Folsom Street", "San Francisco", "CA", "123-123-1234", "https://www.themusicalhop.com", "https://www.facebook.com/TheMusicalHop",
                 "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80", 
                 True, "We are on the lookout for a local artist to play every two weeks. Please call us.")
    ven1.insert()

    ven2 = Venue("The Dueling Pianos Bar",["Classical", "R&B", "Hip-Hop"], "335 Delancey Street",
                 "New York", "NY", "914-003-1132", "https://www.theduelingpianos.com", 
                 "https://www.facebook.com/theduelingpianos", 
                 "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80")
    ven2.insert()

    ven3 = Venue("Park Square Live Music & Coffee",
                 ["Rock n Roll", "Jazz", "Classical", "Folk"],
                 "34 Whiskey Moore Ave",
                  "San Francisco", "CA", "415-000-1234", "https://www.parksquarelivemusicandcoffee.com",
                 "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
                 "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80")
    ven3.insert()
    
def insert_artists():
    artist1 = Artist(4, "Guns N Petals", ["Rock n Roll"], "San Francisco", "CA", "326-123-5000", "https://www.gunsnpetalsband.com",
                     "https://www.facebook.com/GunsNPetals",
                     "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
                    True, "Looking for shows to perform at in the San Francisco Bay Area!")

    artist1.insert()

    artist2 = Artist(5, "Matt Quevedo", ["Jazz"], "New York", "NY", "300-400-5000",  "", "https://www.facebook.com/mattquevedo923251523",
                     "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80")
    artist2.insert()

    artist3 = Artist(6, "The Wild Sax Band", ["Jazz", "Classical"], "San Francisco", "CA", "432-325-5432", "", "",
                     "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80")
    artist3.insert()

def insert_shows():

     show1 = Show(1, 4, "2019-05-21T21:30:00.000Z")
     show1.insert()

     show2 = Show(3, 5, "2019-06-15T23:00:00.000Z")
     show2.insert()

     show3 = Show(3, 6, "2035-04-01T20:00:00.000Z")
     show3.insert()

     show4 = Show(3, 6, "2035-04-08T20:00:00.000Z")
     show4.insert()

     show5 = Show(3, 6, "2035-04-15T20:00:00.000Z")
     show5.insert()
    
    