import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#Database setup
engine = create_engine("sqlite:///resources/hawaii.sqlite")
# connection = engine.connect()

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the tables
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the Database
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# define route
@app.route("/")

# Create function for welcome page
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"

    )
    
# PRECIPITATION ROUTE
@app.route("/api/v1.0/precipitation")

def precipitation():
    last_date_row = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_date = dt.date.fromisoformat(last_date_row[0])
    query_date = last_date - dt.timedelta(days=365)
    precipitation = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= query_date).all()
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

# STATIONS ROUTE
@app.route("/api/v1.0/stations")

def stations():
    results = session.query(station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

# TEMPERATURE OBSERVATIONS ROUTE
@app.route("/api/v1.0/tobs")

def temp_monthly():
    last_date_row = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_date = dt.date.fromisoformat(last_date_row [0])
    query_date = last_date - dt.timedelta(days=365)
    results = session.query(measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date >= query_date).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

# SUMMARY STATISTICS REPORT ROUTE
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)] 
         
    if not end:
        results = session.query(*sel).\
            filter(measurement.date >= start).all()
        temps = list(np.ravel(results))
        session.close()
        return jsonify(temps)
       
    results = session.query(*sel).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()       
    temps = list(np.ravel(results))
    session.close()
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)
