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

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with = engine)

# Assign the Measurment class to a variable called `Measurment` and the station class to a variable called `Station`
Measurment = Base.classes.Measurment
Station = Base.classes.station

# The session is created and closed for each API route query instead of opening the session here and closing it at the end

session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)




# #################################################
# # Flask Routes
# #################################################

# Home page with all available API routes
@app.route("/")
def welcome():
    
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation | Returns jsonified precipitation(in) data for the last year<br/>"
        f"/api/v1.0/stations | Returns jsonified list of stations<br/>"
        f"/api/v1.0/tobs | Returns jsonified temp(F) data for the last year<br/>"
        f"/api/v1.0/startdate | returns min, max, and avg temp(F) after this date. startdate must be in format yyyy/mm/dd<br/>"
        f"/api/v1.0/startdate/enddate | returns min, max, and avg temp for this range. startdate and enddate must be in format yyyy/mm/dd"
    )
    
# Page with precipitation data
@app.route("/api/v1.0/precipitation")
def prcpdata():
    
    """Return a list of all precipitation data for the last year"""
    # Query for most recent year of precipitation data
    session = Session(engine)
    results = session.query(Measurment.date, Measurment.prcp).\
                      filter(Measurment.date >= dt.datetime(2016, 8, 23)).\
                      order_by(Measurment.date).all()

    session.close()

    # Create empty list
    prcp_list = []
	
	
    # Append each datapoint to the list
    for percp, date in prcp_list:
        prcp_dict = {}
        prcp_dict['precipitation'] = percp
        prcp_dict['date'] = date
        prcp_list.append(prcp_dict)

	
	
    # Return jsonified precipitation data
    return jsonify(dict(prcp_list))
	

# #stations
@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)

    active_station = session.query(Measurment.station,func.count(Measurment.station)).\
        group_by(Measurment.station).\
        order_by(func.count(Measurment.station).desc()).all()
    session.close()

    station_list = list(np.ravel(active_station))

    return jsonify(station_list)

# # observed temp
@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)

    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    first_station_data = session.query(Measurment.tobs, Measurment.date).\
        filter(Measurment.station=='USC00519281', Measurment.date >= year_ago).\
        order_by(Measurment.tobs).all()
    session.close()

    station1_list = list(np.ravel(first_station_data))
    return jsonify(station1_list)

# start
@app.route("/api/v1.0/start")
def temps():
    session=Session(engine)

    # start = dt.date(2017, 1, 1)
    start = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    start_query = session.query(func.min(Measurment.tobs), func.max(Measurment.tobs), func.avg(Measurment.tobs)).\
        filter(Measurment.date >= start).all()
    session.close()

    # start_query = []
    tempobs={}
    tempobs["min"]=start_query[0][0]
    tempobs["max"]=start_query[0][1]
    tempobs["avg"]=start_query[0][2]

    return jsonify(tempobs)

# end
@app.route("/api/v1.0/start/end")
def year_data():
    session = Session(engine)

    start = dt.date(2016, 10, 23)
    end = dt.date(2017, 8, 23)
    first_station_data = session.query(func.min(Measurment.tobs), func.max(Measurment.tobs), func.avg(Measurment.tobs)).\
        filter(Measurment.station=='USC00519281', Measurment.date > start, Measurment.date < end).\
        order_by(Measurment.tobs).all()

    session.close()

    tempobs={}
    tempobs["min"]=first_station_data[0][0]
    tempobs["max"]=first_station_data[0][1]
    tempobs["avg"]=first_station_data[0][2]
    
    return jsonify(tempobs)

if __name__ == '__main__':
    app.run(debug=True)