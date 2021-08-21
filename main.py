import sqlite3

import flask
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
class Form(FlaskForm):
    Rating=StringField("Rating Eg:7.5/10",validators=[DataRequired()])
    Review=StringField("Review",validators=[DataRequired()])
    Submit=SubmitField("Update")
class Add(FlaskForm):
    Movie=StringField("Add Anime",validators=[DataRequired()])
    Submit = SubmitField("Update")





app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
Bootstrap(app)
db = SQLAlchemy(app)
class Movies(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250),unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


db.create_all()

@app.route("/",methods=['POST','GET'])
def home():

    movies= Movies.query.order_by(Movies.rating).all()
    for i in range(len(movies)):
        movies[i].ranking = len(movies) - i
    db.session.commit()

    return render_template("index.html",movies=movies[::-1])


@app.route("/edit/<int:id>",methods=['POST','GET'])
def edit(id):
    form=Form()
    if form.validate_on_submit():
        movie = Movies.query.get(id)
        movie.rating=form.Rating.data
        movie.review=form.Review.data
        db.session.commit()
        return flask.redirect("/")
    return render_template("edit.html",form=form)

@app.route("/delete/<int:id>",methods=['POST','GET'])
def delete(id):
    movie = Movies.query.get(id)
    db.session.delete(movie)
    db.session.commit()
    return flask.redirect("/")


@app.route("/add",methods=['POST','GET'])
def add():
    form=Add()
    if form.validate_on_submit():
        anime=form.Movie.data
        res = requests.get(
            f"https://api.themoviedb.org/3/search/tv?api_key=fedf89fd53b4ddd9d212c5146075c20f&language=en-US&page=1&include_adult=false&query={anime}")
        data=(res.json())
        data=[values for values in (data['results'])]
        return render_template("select.html", data=data)
    return render_template("add.html", form=form)


@app.route("/find/<int:id>",methods=['POST','GET'])
def find(id):


    res = requests.get(f"https://api.themoviedb.org/3/tv/{id}?api_key=fedf89fd53b4ddd9d212c5146075c20f&language=en-US")
    data = (res.json())
    new_movie = Movies(
        title=data['name'],
        year=data['first_air_date'][0:4],
        description=data['overview'],
        rating=int(data['vote_average']),
        ranking=0,
        review="Not yet",
        img_url=f"https://image.tmdb.org/t/p/w500/{data['backdrop_path']}"
    )
    db.session.add(new_movie)
    db.session.commit()
    return flask.redirect("/")


if __name__ == '__main__':
    app.run(debug=True)

