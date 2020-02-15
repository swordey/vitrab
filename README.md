# VITRAB - Visual Trading Backtester
This a bokeh platform where you can visualize different trading strategies, on different historical data.

![](imgs/showcase.gif)
![](imgs/showcase1.gif)

## Fun facts
* You can visualize ohlc (open-high-low-close) data as everyone with candles
* You can read about the used indicators, by clicking thi (i) button next to "select investing strategy" dropdown
* You can see how the portfolios value change by time, on the third tab

## How to test
* Visit [my demo site](https://vitrab.herokuapp.com/app) - it hosted on herokuapp, so you have to wait a little so the server loads.
* You can deploy it to your own heroku (you can reach it at <your selected name>.herokuapp.com)
```bash
heroku login
heroku git:clone -a <your selected name>
cd <your selected name>
git add .
git commit -am "initial commit"
git push heroku master
```
* Clone the dockerversion branch, run:
```bash
docker build -t vitrab .

docker run -d --name vitrab \
   -p 5000:5000 \
   -v $PWD:/app $1
```
then visit http://localhost:5000 in your browser

## Built With
* [Python](https://www.python.org/)
* [Bokeh](https://bokeh.org/) - Visualization library
* [pandas_datareader](https://pandas-datareader.readthedocs.io/en/latest/) - remote data access for panda
* [Docker](https://www.docker.com/) - App Containerization
* [Heroku](https://heroku.com/) - Cloud Application Platform

## Authors

* **Kardos Tamás** - [Swordy](https://github.com/swordey)