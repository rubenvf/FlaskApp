import pandas as pd
import plotly.graph_objs as go
from collections import OrderedDict
import requests


# default list of all countries of interest
country_default = OrderedDict([('Germany', 'DEU'), ('United Kingdom', 'GBR'), 
  ('France', 'FRA'), ('Italy', 'ITA'), ('Russia', 'RUS'), ('Spain', 'ESP'), 
  ('Netherlands', 'NLD'), ('Switzerland', 'CHE'),  ('Poland', 'POL'), ('Sweden', 'SWE')])


def return_figures(countries=country_default):
  """Creates four plotly visualizations using the World Bank API

    Args:
        country_default (dict): list of countries for filtering the data
    Returns:
        list (dict): list containing the four plotly visualizations
  """

  # when the countries variable is empty, use the country_default dictionary
  if not bool(countries):
    countries = country_default

  # prepare filter data for World Bank API
  # the API uses ISO-3 country codes separated by ;
  country_filter = list(countries.values())
  country_filter = [x.lower() for x in country_filter]
  country_filter = ';'.join(country_filter)

  # World Bank indicators of interest for pulling data
  # https://data.worldbank.org/indicator/NY.GDP.MKTP.KD?end=2019&start=1961&view=chart (GDP by country)
  # https://data.worldbank.org/indicator/TX.VAL.TECH.MF.ZS?view=chart  (Tech exports %)
  # https://data.worldbank.org/indicator/GB.XPD.RSDV.GD.ZS?view=chart (Research and development expenditure (% of GDP))
  # https://data.worldbank.org/indicator/IP.JRN.ARTC.SC?view=chart (Scientific and technical journal articles)
  # https://data.worldbank.org/indicator/IP.PAT.RESD?view=chart (Patent applications, residents)
  # https://data.worldbank.org/indicator/NE.IMP.GNFS.ZS?view=chart (Imports of goods and services (% of GDP))
  # https://data.worldbank.org/indicator/EN.ATM.CO2E.PC?view=chart (CO2 emissions (metric tons per capita))
  # https://data.worldbank.org/indicator/SE.XPD.TOTL.GD.ZS?view=chart (Government expenditure on education, total (% of GDP))
  # https://data.worldbank.org/indicator/SE.TER.ENRR?view=chart (School enrollment, tertiary (% gross))
  # https://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG?view=chart (GDP growth (annual %))
  indicators = ['NY.GDP.MKTP.KD', 'TX.VAL.TECH.MF.ZS', 'IP.JRN.ARTC.SC', 'GB.XPD.RSDV.GD.ZS', 'IP.PAT.RESD', 'EN.ATM.CO2E.PC', 'SE.XPD.TOTL.GD.ZS', 'SE.TER.ENRR', 'NY.GDP.MKTP.KD.ZG', 'NE.IMP.GNFS.ZS']

# https://data.worldbank.org/indicator/BX.GSR.ROYL.CD?view=chart


  data_frames = [] # stores the data frames with the indicator data of interest
  urls = [] # url endpoints for the World Bank API

  # pull data from World Bank API and clean the resulting json
  # results stored in data_frames variable
  for indicator in indicators:
    url = 'http://api.worldbank.org/v2/countries/' + country_filter +\
    '/indicators/' + indicator + '?date=1990:2019&per_page=1000&format=json'
    urls.append(url)

    try:
      r = requests.get(url)
      data = r.json()[1]
    except:
      print('could not load data ', indicator)

    for i, value in enumerate(data):
      value['indicator'] = value['indicator']['value']
      value['country'] = value['country']['value']

    data_frames.append(data)
 

  # first chart plots GDP (constant 2010 in US$) from 1990 to 2019 in top 10 economies of Europe
  # as a line chart
  graph_one = []
  df_one = pd.DataFrame(data_frames[8])

  # filter and sort values for the visualization
  # filtering plots the countries in decreasing order by their values
  df_one = df_one[(df_one['date'] == '2018') | (df_one['date'] == '1990')]
  df_one.sort_values('value', ascending=False, inplace=True)

  # this  country list is re-used by all the charts to ensure legends have the same
  # order and color
  countrylist = df_one.country.unique().tolist()
  
  for country in countrylist:
      x_val = df_one[df_one['country'] == country].date.tolist()
      y_val =  df_one[df_one['country'] == country].value.tolist()
      graph_one.append(
          go.Scatter(
          x = x_val,
          y = y_val,
          mode = 'lines',
          name = country
          )
      )

  layout_one = dict(title = 'GDP growth (annual %) <br> from 1990 to 2018',
                xaxis = dict(title = 'Year',
                  autotick=False, tick0=1990, dtick=28),
                yaxis = dict(title = 'Annual growth (%)'),
                )

  # second chart plots High-technology exports (% of manufactured exports) for 2018 as a bar chart
  graph_two = []
  df_two = pd.DataFrame(data_frames[1])
  df_two.sort_values('value', ascending=False, inplace=True)
  df_two = df_two[df_two['date'] == '2018'] 

  graph_two.append(
      go.Bar(
      x = df_two.country.tolist(),
      y = df_two.value.tolist(),
      )
  )

  layout_two = dict(title = 'High-technology exports in 2018 <br> (% manufactured exports)',
                xaxis = dict(title = 'Country',),
                yaxis = dict(title = '% of High-technology export'),
                )

  # third chart plots Patent applications, residents from 1990 to 2019
  graph_three = []
  df_three = pd.DataFrame(data_frames[9])
  df_three = df_three[(df_three['date'] == '2018') | (df_three['date'] == '1990')]

  df_three.sort_values('value', ascending=False, inplace=True)
  for country in countrylist:
      x_val = df_three[df_three['country'] == country].date.tolist()
      y_val =  df_three[df_three['country'] == country].value.tolist()
      graph_three.append(
          go.Scatter(
          x = x_val,
          y = y_val,
          mode = 'lines',
          name = country
          )
      )

  layout_three = dict(title = 'Imports of goods and services (% of GDP) <br> from 1990 to 2018',
                xaxis = dict(title = 'Year',
                  autotick=False, tick0=1990, dtick=28),
                yaxis = dict(title = 'Number of applications'),
                )

  # fourth chart shows Research and development expenditure (% of GDP) vs GDP 
  graph_four = []
  df_four_a = pd.DataFrame(data_frames[8])
  df_four_a = df_four_a[['country', 'date', 'value']]
  
  df_four_b = pd.DataFrame(data_frames[9])
  df_four_b = df_four_b[['country', 'date', 'value']]

  df_four = df_four_a.merge(df_four_b, on=['country', 'date'])
  df_four.sort_values('date', ascending=True, inplace=True)


  for i, country in enumerate(countrylist):


      x_val = df_four[df_four['country'] == country].value_x.tolist()
      y_val = df_four[df_four['country'] == country].value_y.tolist()
      years = df_four[df_four['country'] == country].date.tolist()
      country_label = df_four[df_four['country'] == country].country.tolist()

      text = []
      for country, year in zip(country_label, years):
          text.append(str(country) + ' ' + str(year))

      graph_four.append(
          go.Scatter(
          x = x_val,
          y = y_val,
          mode = 'markers',
          text = text,
          name = country,
          textposition = 'top'
          )
      )

  layout_four = dict(title = 'GDP growth vs Imports of goods and services',
                xaxis = dict(title = 'Annual GDP growth (%)', dtick=5),
                yaxis = dict(title = 'Imports of goods and services (%)', dtick=10),
                )


  # append all charts
  figures = []
  figures.append(dict(data=graph_one, layout=layout_one))
  figures.append(dict(data=graph_two, layout=layout_two))
  figures.append(dict(data=graph_three, layout=layout_three))
  figures.append(dict(data=graph_four, layout=layout_four))

  return figures

