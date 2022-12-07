# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Generate the engine to the hawaii.sqlite datase
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect the database schema into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the taBles in the sqlite file
Measurement = Base.classes.measurement
Stations = Base.classes.station

session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


# Convert the query results from your precipitation analysis 
# (i.e. retrieve only the last 12 months of data) 
# to a dictionary using date as the key and prcp as the value.
@app.route("/")
def welcome():
        return(f'Welcome to my climate api<br/>'
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"
)

@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    most_recent_date_int = [int(i) for i in most_recent_date.split("-")]
    one_year_prior = dt.date(*most_recent_date_int) - dt.timedelta(days=365)
    
# Perform a query to retrieve the data and precipitation scores
    recent_12mos_list = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date>=one_year_prior.strftime('%Y-%m-%d')).order_by(Measurement.date).all()
    session.close()
    precipitationX = {date:prcp for date, prcp in recent_12mos_list}
    return jsonify(precipitationX)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Stations.station).all()
    session.close()
    stationsX = list(np.ravel(stations))
    return jsonify(stations=stationsX) 

# Query the dates and temperature observations of the most-active station 
# for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    station_lst = session.query(Measurement.tobs, Measurement.date).filter(Measurement.station=='USC00519281').\
        filter(Measurement.date>='2016-08-22').order_by(Measurement.date).all()
    station_lst = [i[0] for i in station_lst]
    session.close()
    station_lstX = list(np.ravel(station_lst))
    return jsonify(station_lst=station_lstX)

#Return a JSON list of the minimum temperature, the average temperature, 
# and the maximum temperature for a specified start or start-end range.
# For a specified start, calculate TMIN, TAVG, and TMAX for all 
# the dates greater than or equal to the start date.
#For a specified start date and end date, 
# # calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/temp/start")
def temp_metrics():
    find = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    sel_find = session.query(*find).\
        filter(Measurement.date>='2016-08-22').order_by(Measurement.date).all()
    session.close()
    sel_findX = list(np.ravel(sel_find))
    return jsonify(sel_find=sel_findX)

@app.route("/api/v1.0/temp/start/end")
def metrics():
    find1 = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    sel_find1 = session.query(*find1).\
        filter(Measurement.date >='2016-08-22', Measurement.date <='2017-08-22').order_by(Measurement.date).all()
    session.close()
    sel_find1X = list(np.ravel(sel_find1))
    return jsonify(sel_find1=sel_find1X)

if __name__ == "__main__":
    app.run(debug=True)
