#! frontend.py
from datetime import date

from bokeh.palettes import Category20 as palette

# Layouts
from bokeh.layouts import grid
from bokeh.layouts import layout
from bokeh.models import Button
from bokeh.models import Panel, Tabs, CustomJS

# Visualizing imports
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Div
from bokeh.models.widgets import Select
from bokeh.models.widgets import MultiSelect
from bokeh.models.widgets import TextInput
from bokeh.models.widgets.inputs import DatePicker
from bokeh.models.callbacks import CustomJS
from bokeh.plotting import figure, curdoc

from bokeh.embed import components

from core.trader import Trader

stocks = {
          "Apple": "AAPL",
          "Microsoft": "MSFT",
          "Alphabet Inc": "GOOG",
          "Alphabet Inc Class A": "GOOGL",
          "Tesla, Inc.": "TSLA",
          "Netflix": "NFLX",
          "Vanguard Total Stock Market Index Fund": "VTSAX",
          "SPDR S&P 500": "SPY",
          "Nasdaq-100 Index": "NDX"}


class GUI:
    def __init__(self):
        self.periodic_callback_id = 0
        self.ui_width = 300

        self.stockData = {}
        self.Bars = {}
        self.buySignals = {}
        self.sellSignals = {}
        self.portfolioData = ColumnDataSource()

        # Data selection
        self.DataSelectionTitle = Div(text="<center><b>Data Selection</b></center>", sizing_mode="stretch_both")
        stock_names = list(stocks.keys())
        # self.tickerSelector = Select(title="Select:",
        # value=stock_names[0], options=stock_names, sizing_mode="stretch_both")
        self.tickerMultiSelector = MultiSelect(title="Select:", value=[stock_names[0]],
                                   options=stock_names, sizing_mode="stretch_both")
        self.periodStartText = Div(text="Start date", width=int(self.ui_width*0.2))
        self.periodStart = DatePicker(value='10/1/2010', min_date="1/1/1900", max_date=date.today(), sizing_mode="stretch_both")
        self.periodEndText = Div(text="End date", width=int(self.ui_width*0.2))
        self.periodEnd = DatePicker(value='1/1/2012', min_date="1/1/1900", max_date=date.today(), sizing_mode="stretch_both")

        # Trading Strategy selection
        self.TradingAlgoParamsTitle = Div(text="<b>Trading Algorithm Params</b>")
        self.methodSelector = Select(title="Select method",
                                     value="Moving Average Crossover",
                                     options=["Buy and Hold", "Moving Average Crossover"],
                                     sizing_mode="stretch_both")

        self.BackTestingParamsTitle = Div(text="<b>Backtesting parameters</b>")
        self.capitalMoney = TextInput(value="100000", title="Initial capital [$]", sizing_mode="stretch_both")
        self.simulationSpeed = TextInput(value="15", title="Simulation speed [Data/s]", sizing_mode="stretch_both")

        self.simulateButton = Button(label="Simulate", sizing_mode="stretch_both")
        self.stopButton = Button(label="Stop", sizing_mode="stretch_both")

        # Results
        self.BackTestingResultsTitle = Div(text="<b>Backtesting results</b>")
        self.PortfolioTotal = Div(text="Portfolio total:")
        self.PortfolioTotalReturn = Div(text="Portfolio total return:")
        self.SharpRatio = Div(text="Sharp Ratio:")
        self.CAGR = Div(text="Compound Annual Growth Rate:")

        self.simulateButton.on_click(self.start_animation)
        self.stopButton.on_click(self.stop_animation)

        self.UIPanel = layout([self.DataSelectionTitle],
                              [self.tickerMultiSelector],
                              # [self.tickerSelector],
                              [self.periodStartText, self.periodStart],
                              [self.periodEndText, self.periodEnd],
                              [self.TradingAlgoParamsTitle],
                              [self.methodSelector],
                              [self.BackTestingParamsTitle],
                              [self.capitalMoney],
                              [self.simulationSpeed],
                              [self.simulateButton, self.stopButton],
                              [self.BackTestingResultsTitle],
                              [self.PortfolioTotal],
                              [self.PortfolioTotalReturn],
                              [self.SharpRatio],
                              [self.CAGR], width=self.ui_width)

        self.portfolioVisu = figure(toolbar_location=None,
                                    x_axis_type='datetime',
                                    sizing_mode="stretch_both",
                                    height=100,
                                    name="portfolio_visu")
        self.portfolioVisu.xaxis.axis_label = 'Date'
        self.portfolioVisu.yaxis.axis_label = 'Value [$]'

        self.priceMovementVisu = figure(toolbar_location=None,
                                        x_axis_type='datetime',
                                        sizing_mode="stretch_both",
                                        name="pricemovement_visu")
        self.priceMovementVisu.xaxis.axis_label = 'Date'
        self.priceMovementVisu.yaxis.axis_label = 'Price [$]'

        self.candleStickVisu = figure(tools="pan,wheel_zoom,reset,save",
                                      active_drag='pan',
                                      active_scroll='wheel_zoom',
                                      # x_axis_type='linear',
                                      x_axis_type='datetime',
                                      sizing_mode="stretch_both",
                                      name="candlestick_visu")
        self.candleStickVisu.xaxis.axis_label = 'Date'
        self.candleStickVisu.yaxis.axis_label = 'Price [$]'

        self.tab1 = Panel(child=grid([self.candleStickVisu]), title="Candle")
        self.tab2 = Panel(child=grid([self.priceMovementVisu]), title="Stock")
        self.tab3 = Panel(child=grid([self.portfolioVisu]), title="Portfolio")
        tabs = Tabs(tabs=[self.tab1, self.tab2, self.tab3])

        curdoc().add_root(grid([[self.UIPanel, tabs]]))
        curdoc().title = "Visual Trading Backtester"

        self.trader = Trader()

    def create_pricemovement_visu(self):
        self.priceMovementVisu = figure(toolbar_location=None, x_axis_type='datetime', sizing_mode="stretch_both")
        for idx, ticker in enumerate(self.trader.strategy.tickers):
            self.priceMovementVisu.line(x='Date',
                                        y='Close',
                                        source=self.stockData[ticker],
                                        legend_label=ticker + " price",
                                        line_color=palette[20][idx])
            self.priceMovementVisu.scatter(x='Date',
                                           y='signal',
                                           source=self.buySignals[ticker],
                                           legend_label=ticker + " Buy signal",
                                           marker="triangle",
                                           size=15,
                                           fill_color='black')
            self.priceMovementVisu.scatter(x='Date',
                                           y='signal',
                                           source=self.sellSignals[ticker],
                                           legend_label=ticker + " Sell signal",
                                           marker="inverted_triangle",
                                           size=15,
                                           fill_color='purple')

        self.priceMovementVisu.legend.location = "top_left"
        self.priceMovementVisu.legend.click_policy = "hide"

        self.priceMovementVisu.xaxis.axis_label = 'Date'
        self.priceMovementVisu.yaxis.axis_label = 'Price [$]'

    def create_candlestick_visu(self):
        self.candleStickVisu = figure(tools="pan,wheel_zoom,reset,save",
                                      active_drag='pan',
                                      active_scroll='wheel_zoom',
                                      # x_axis_type='linear',
                                      x_axis_type='datetime',
                                      sizing_mode="stretch_both")
        w = 12 * 60 * 60 * 1000  # half day in ms
        for ticker in self.trader.strategy.tickers:
            self.candleStickVisu.segment("Date", "High", "Date", "Low", source=self.Bars[ticker], color="black")
            self.candleStickVisu.vbar("Date", w, "Open","Close", source=self.Bars[ticker],
                                        fill_color="Color", line_color="black")

        self.candleStickVisu.xaxis.axis_label = 'Date'
        self.candleStickVisu.yaxis.axis_label = 'Price [$]'

    def create_portfolio_visu(self):
        self.portfolioVisu = figure(toolbar_location=None,
                                    x_axis_type='datetime',
                                    sizing_mode="stretch_both",
                                    height=100)
        self.portfolioVisu.line(x='Date',
                                y='total',
                                source=self.portfolioData,
                                legend_label="Portfolio total",
                                line_color="red")
        self.portfolioVisu.line(x='Date',
                                y='benchmark',
                                source=self.portfolioData,
                                legend_label="S&P 500 Benchmark",
                                line_color="green")
        for idx, ticker in enumerate(self.trader.strategy.tickers):
            self.portfolioVisu.line(x='Date',
                                    y=ticker+'_holdings',
                                    source=self.portfolioData,
                                    legend_label=ticker+" holdings",
                                    line_color=palette[20][idx])
        self.portfolioVisu.line(x='Date',
                                y='cash',
                                source=self.portfolioData,
                                legend_label="Portfolio cash",
                                line_color="blue")

        self.portfolioVisu.legend.location = "top_left"
        self.portfolioVisu.legend.click_policy = "hide"

        self.portfolioVisu.xaxis.axis_label = 'Date'
        self.portfolioVisu.yaxis.axis_label = 'Value [$]'

    def start_animation(self):
        self.trader.initialize(list(map(lambda x: stocks[x], self.tickerMultiSelector.value)),
                               self.methodSelector.value,
                               float(self.capitalMoney.value),
                               self.periodStart.value,
                               self.periodEnd.value)

        self.stop_animation()
        self.clear_figures()
        self.trader.init_plots(self.priceMovementVisu)

        self.periodic_callback_id = \
            curdoc().add_periodic_callback(self.update_visu,
                                           int(1000/float(self.simulationSpeed.value)))  # num of ms to wait

    def stop_animation(self):
        # Stop animation, by deleting callback
        if self.periodic_callback_id != 0:
            curdoc().remove_periodic_callback(self.periodic_callback_id)
            # if periodic callback existed, it means, an animation ran at least once
            # Restore whole candle stick diagram
            for ticker in self.trader.strategy.tickers:
                self.Bars[ticker].data = self.stockData[ticker].data
        self.periodic_callback_id = 0

        self.trader.evaluate()
        self.plot_strategy_results()

    def clear_figures(self):
        self.create_column_data_sources()
        self.create_pricemovement_visu()
        self.create_portfolio_visu()
        self.create_candlestick_visu()
        curdoc().roots[0].children[1][0].tabs[0].child.children[0] = (self.candleStickVisu, 0, 0, 1, 1)
        curdoc().roots[0].children[1][0].tabs[1].child.children[0] = (self.priceMovementVisu, 0, 0, 1, 1)
        curdoc().roots[0].children[1][0].tabs[2].child.children[0] = (self.portfolioVisu, 0, 0, 1, 1)

    def create_column_data_sources(self):
        self.stockData = {}
        self.Bars = {}
        self.buySignals = {}
        self.sellSignals = {}
        # self.portfolioData =
        portfolio_data = dict(Date=[], cash=[], total=[], benchmark=[])
        for ticker in self.trader.strategy.tickers:
            self.stockData[ticker] = \
                ColumnDataSource(dict(Date=[], High=[], Low=[], Open=[], Close=[], Adj_Close=[], Color=[]))
            self.Bars[ticker] = \
                ColumnDataSource(dict(Date=[], High=[], Low=[], Open=[], Close=[], Adj_Close=[], Color=[]))
            self.buySignals[ticker] = ColumnDataSource(dict(Date=[], signal=[]))
            self.sellSignals[ticker] = ColumnDataSource(dict(Date=[], signal=[]))
            portfolio_data[ticker+"_holdings"] = []
        self.portfolioData = ColumnDataSource(portfolio_data)

    # Plots
    def plot_stock_price(self, data):
        for ticker in self.trader.strategy.tickers:
            new_data = dict(
                Date=[data.loc[ticker].iloc[-1].name],
                High=[data.loc[ticker].iloc[-1].High],
                Low=[data.loc[ticker].iloc[-1].Low],
                Open=[data.loc[ticker].iloc[-1].Open],
                Close=[data.loc[ticker].iloc[-1].Close],
                Adj_Close=[data.loc[ticker].iloc[-1]["Adj Close"]],
                Color=["#7CFC00" if data.loc[ticker].iloc[-1].Close > data.loc[ticker].iloc[-1].Open else "#F2583E"]
            )
            self.stockData[ticker].stream(new_data)
            self.Bars[ticker].stream(new_data, 70)

    def plot_buy_sell_signals(self):
        for ticker in self.trader.strategy.tickers:
            if ticker not in self.trader.strategy.signals:
                return
            curr_position = int(self.trader.get_last_signal_by_ticker(ticker).positions)
            if curr_position == 1:
                buy_data = dict(
                    Date=[self.trader.get_last_signal_by_ticker(ticker).name],
                    signal=[self.stockData[ticker].data["Close"][-1]]
                )
                self.buySignals[ticker].stream(buy_data)
            elif curr_position == -1:
                sell_data = dict(
                    Date=[self.trader.get_last_signal_by_ticker(ticker).name],
                    signal=[self.stockData[ticker].data["Close"][-1]]
                )
                self.sellSignals[ticker].stream(sell_data)

    def plot_portfolio(self):
        last_portfolio_value = self.trader.get_portfolio_manager().get_last_portfolio_value()
        last_benchmark_portfolio_value = self.trader.get_benchmark_portfolio_manager().get_last_portfolio_value()
        if last_portfolio_value is None:
            return
        new_data = dict(
            Date=[last_portfolio_value.name],
            # holdings=[last_portfolio_value.holdings],
            cash=[last_portfolio_value.cash],
            total=[last_portfolio_value.total],
            benchmark=[last_benchmark_portfolio_value.total]
        )
        for ticker in self.trader.strategy.tickers:
            new_data[ticker+"_holdings"] = \
                [self.trader.get_portfolio_manager().get_last_portfolio_value()[ticker+"_holdings"]]
        self.portfolioData.stream(new_data)

    def plot_strategy_results(self):
        if self.trader.get_portfolio_manager().portfolio_total is not None:
            self.PortfolioTotal.text = self.PortfolioTotal.text.split(":")[0] + \
                                       ": " + \
                                       str(self.trader.get_portfolio_manager().portfolio_total)
            self.PortfolioTotalReturn.text = self.PortfolioTotalReturn.text.split(":")[0] + \
                                             ": " + \
                                             str(self.trader.get_portfolio_manager().portfolio_total_return) + \
                                             "%"
            self.SharpRatio.text = self.SharpRatio.text.split(":")[0] + \
                                   ": " + \
                                   str(self.trader.get_portfolio_manager().sharp_ratio)
            self.CAGR.text = self.CAGR.text.split(":")[0] + \
                             ": " + \
                             str(self.trader.get_portfolio_manager().cagr)+"%"

    # Update visus
    def update_visu(self):
        d = self.trader.run()
        self.trader.plot()
        if d is None:
            # In the end of simulation, or online trading evaluate result and plot
            self.trader.evaluate()
            self.plot_strategy_results()
            self.stop_animation()
            return

        self.plot_stock_price(d)
        self.plot_buy_sell_signals()
        self.plot_portfolio()
