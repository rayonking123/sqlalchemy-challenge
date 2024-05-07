# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)
# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        f"Welcome to Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start_date<br/>"
        f"/api/v1.0/temp/start_date/end_date<br/>"
        f"<p>'start_date' and 'end_date' should be in MMDDYYYY format.</p>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    formatted_data = {date: prcp for date, prcp in results}
    return jsonify(formatted_data)

@app.route("/api/v1.0/stations")
def stations():
    station_names = session.query(Station.station).all()
    station_list = [name[0] for name in station_names]
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    last_year_date = dt.datetime.strptime(session.query(func.max(Measurement.date)).scalar(), '%Y-%m-%d') - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= last_year_date).all()
    tobs_data = [{"date": date, "temperature": tobs} for date, tobs in results]
    return jsonify(tobs_data)

@app.route("/api/v1.0/temp/<start_date>")
@app.route("/api/v1.0/temp/<start_date>/<end_date>")
def temps_start(start_date=None, end_date=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end_date:
        start_date = dt.datetime.strptime(start_date, "%m%d%Y")
        results = session.query(*sel).filter(Measurement.date >= start_date).all()
    else:
        start_date = dt.datetime.strptime(start_date, "%m%d%Y")
        end_date = dt.datetime.strptime(end_date, "%m%d%Y")
        results = session.query(*sel).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run(debug=True)