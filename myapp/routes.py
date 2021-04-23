from myapp import app

import json, plotly
from flask import render_template, request, Response, jsonify
from data.data import return_figures


@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
def index():

	# List of countries for filter
	country_codes = [['Germany', 'DEU'],['United Kingdom', 'GBR'],['France', 'FRA'],
	['Italy', 'ITA'],['Russia', 'RUS'],['Spain', 'ESP'],['Netherlands', 'NLD'],
	['Turkey', 'TUR'],['Switzerland', 'CHE'],['Sweden', 'SWE']]
    

	# Parse the POST request countries list
	if (request.method == 'POST') and request.form:
		figures = return_figures(request.form)
		countries_selected = []

		for country in request.form.lists():
			countries_selected.append(country[1][0])
	
	# GET request returns all countries for initial page load
	else:
		figures = return_figures()
		countries_selected = []
		for country in country_codes:
			countries_selected.append(country[1])

	# plot ids for the html id tag
	ids = ['figure-{}'.format(i) for i, _ in enumerate(figures)]

	# Convert the plotly figures to JSON for javascript in html template
	figuresJSON = json.dumps(figures, cls=plotly.utils.PlotlyJSONEncoder)

	return render_template('index.html', ids=ids,
		figuresJSON=figuresJSON,
		all_countries=country_codes,
		countries_selected=countries_selected)