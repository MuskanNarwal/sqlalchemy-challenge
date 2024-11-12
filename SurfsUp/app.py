# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)
print(Base.classes.keys())
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
station=Base.classes.station
measurements=Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route('/')
def home():
    return (
        """
        Welcome to the Hawaii Climate API!
        Available Routes:
        /api/v1.0/precipitation
        /api/v1.0/stations
        /api/v1.0/tobs
        /api/v1.0/<start>
        /api/v1.0/<start>/<end>
        """
    )

# Precipitation route
@app.route('/api/v1.0/precipitation')
def precipitation():
    # Get the most recent date from the measurements table
    most_recent_date = session.query(measurements.date).order_by(measurements.date.desc()).first()[0]
    last_year_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query for precipitation data for the last 12 months
    precip_data = session.query(measurements.date, measurements.prcp).filter(measurements.date >= last_year_date).all()

    # Convert query results to a dictionary
    precip_dict = {date: prcp for date, prcp in precip_data}

    return jsonify(precip_dict)

# Stations route
@app.route('/api/v1.0/stations')
def stations():
    # Query all stations from the database
    stations_data = session.query(station.station).all()
    
    # Convert the results into a list of stations
    stations_list = [station[0] for station in stations_data]
    
    return jsonify(stations_list)

# TOBS route (Temperature Observations)
@app.route('/api/v1.0/tobs')
def tobs():
    # Most active station ID
    most_active_station_id = 'USC00519281'  # Use the most active station ID

    # Get the most recent date from the measurements table
    most_recent_date = session.query(measurements.date).order_by(measurements.date.desc()).first()[0]
    last_year_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query for temperature observations for the last 12 months for the most active station
    tobs_data = session.query(measurements.date, measurements.tobs).filter(
        measurements.station == most_active_station_id,
        measurements.date >= last_year_date
    ).all()

    # Convert query results to a list of dictionaries
    tobs_list = [{'date': date, 'tobs': tobs} for date, tobs in tobs_data]

    return jsonify(tobs_list)

# Temperature statistics route (start)
@app.route('/api/v1.0/<start>')
def start_temp_stats(start):
    # Query for temperature statistics (min, avg, max) for the dates >= start
    temp_stats = session.query(
        func.min(measurements.tobs),
        func.avg(measurements.tobs),
        func.max(measurements.tobs)
    ).filter(measurements.date >= start).all()

    # Convert the results into a dictionary
    stats_dict = {
        'TMIN': temp_stats[0][0],
        'TAVG': temp_stats[0][1],
        'TMAX': temp_stats[0][2]
    }

    return jsonify(stats_dict)

# Temperature statistics route (start and end)
@app.route('/api/v1.0/<start>/<end>')
def start_end_temp_stats(start, end):
    # Query for temperature statistics (min, avg, max) for the date range [start, end]
    temp_stats = session.query(
        func.min(measurements.tobs),
        func.avg(measurements.tobs),
        func.max(measurements.tobs)
    ).filter(measurements.date >= start, measurements.date <= end).all()

    # Convert the results into a dictionary
    stats_dict = {
        'TMIN': temp_stats[0][0],
        'TAVG': temp_stats[0][1],
        'TMAX': temp_stats[0][2]
    }

    return jsonify(stats_dict)

if __name__ == '__main__':
    app.run(debug=True)