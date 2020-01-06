#! frontend.py
from datetime import date

# Layouts
from bokeh.layouts import grid
from bokeh.layouts import layout
from bokeh.models import Button
from bokeh.models import Panel, Tabs, CustomJS

# Visualizing imports
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Div
from bokeh.models.widgets import Select
from bokeh.models.widgets import TextInput
from bokeh.models.widgets.inputs import DatePicker
from bokeh.plotting import figure, curdoc

from core.trader import Trader


class GUI:
    def __init__(self):
        self.periodic_callback_id = 0
        self.ui_width = 300

        self.stockData = ColumnDataSource()
        self.Bars = ColumnDataSource()
        self.buySignals = ColumnDataSource()
        self.sellSignals = ColumnDataSource()
        self.portfolioData = ColumnDataSource()
        self.reset_column_data_sources()

        # Data selection
        self.DataSelectionTitle = Div(text="<center><b>Data Selection</b></center>", sizing_mode="stretch_both")
        self.tickerSelector = Select(title="Select", value="AAPL", options=["AAPL", "SPY", "MSFT", "GOOG"], sizing_mode="stretch_both")
        self.periodStartText = Div(text="Start date", width=int(self.ui_width*0.2))
        self.periodStart = DatePicker(value='10/1/2006', min_date="1/1/1900", max_date=date.today(), sizing_mode="stretch_both")
        self.periodEndText = Div(text="End date", width=int(self.ui_width*0.2))
        self.periodEnd = DatePicker(value='1/1/2012', min_date="1/1/1900", max_date=date.today(), sizing_mode="stretch_both")

        self.space = Div()

        # Trading Strategy selection
        self.TradingAlgoParamsTitle = Div(text="<b>Trading Algorithm Params</b>")
        self.methodSelector = Select(title="Select method",
                                     value="Moving Average Crossover",
                                     options=["Buy and Hold", "Moving Average Crossover"],
                                     sizing_mode="stretch_both")

        self.BackTestingParamsTitle = Div(text="<b>Backtesting parameters</b>")
        self.capitalMoney = TextInput(value="100000", title="Initial capital", sizing_mode="stretch_both")
        self.simulationSpeed = TextInput(value="5", title="Simulation speed [Data/s]", sizing_mode="stretch_both")

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
                              [self.tickerSelector],
                              [self.periodStartText, self.periodStart],
                              [self.periodEndText, self.periodEnd],
                              # [self.space],
                              [self.TradingAlgoParamsTitle],
                              [self.methodSelector],
                              # [self.space],
                              [self.BackTestingParamsTitle],
                              [self.capitalMoney],
                              [self.simulationSpeed],
                              [self.simulateButton, self.stopButton],
                              # [self.space],
                              [self.BackTestingResultsTitle],
                              [self.PortfolioTotal],
                              [self.PortfolioTotalReturn],
                              [self.SharpRatio],
                              [self.CAGR], width=self.ui_width)

        self.PortfolioVisu = figure(toolbar_location=None,
                                    x_axis_type='datetime',
                                    sizing_mode="stretch_both",
                                    height=100)
        self.PortfolioVisu.line(x='Date',
                                y='total',
                                source=self.portfolioData,
                                legend_label="Portfolio total",
                                line_color="red")
        self.PortfolioVisu.line(x='Date',
                                y='holdings',
                                source=self.portfolioData,
                                legend_label="Portfolio holdings",
                                line_color="green")
        self.PortfolioVisu.line(x='Date',
                                y='cash',
                                source=self.portfolioData,
                                legend_label="Portfolio cash",
                                line_color="blue")

        self.PortfolioVisu.legend.location = "top_left"
        self.PortfolioVisu.legend.click_policy = "hide"

        self.PortfolioVisu.xaxis.axis_label = 'Date'
        self.PortfolioVisu.yaxis.axis_label = 'Value [$]'

        self.priceMovementVisu = None
        self.create_pricemovement_visu()
        # self.priceMovementVisu = figure(toolbar_location=None, x_axis_type='datetime', sizing_mode="stretch_both")
        # self.priceMovementVisu.line(x='Date',
        #                             y='Close',
        #                             source=self.stockData,
        #                             legend_label="Stock price",
        #                             line_color="red")
        # self.priceMovementVisu.scatter(x='Date',
        #                                y='signal',
        #                                source=self.buySignals,
        #                                legend_label="Buy signal",
        #                                marker="triangle",
        #                                size=15,
        #                                fill_color='black')
        # self.priceMovementVisu.scatter(x='Date',
        #                                y='signal',
        #                                source=self.sellSignals,
        #                                legend_label="Sell signal",
        #                                marker="inverted_triangle",
        #                                size=15,
        #                                fill_color='purple')
        #
        # self.priceMovementVisu.legend.location = "top_left"
        # self.priceMovementVisu.legend.click_policy = "hide"
        #
        # self.priceMovementVisu.xaxis.axis_label = 'Date'
        # self.priceMovementVisu.yaxis.axis_label = 'Price [$]'

        self.candleStickVisu = figure(tools="pan,xwheel_zoom,reset,save",
                                      active_drag='pan',
                                      active_scroll='xwheel_zoom',
                                      # x_axis_type='linear',
                                      x_axis_type='datetime',
                                      sizing_mode="stretch_both")
        w = 12 * 60 * 60 * 1000  # half day in ms
        self.candleStickVisu.segment("Date", "High", "Date", "Low", source=self.Bars, color="black")
        self.candleStickVisu.vbar("Date", w, "Open","Close", source=self.Bars,
                                    fill_color="Color", line_color="black")

        self.tab1 = Panel(child=grid([self.candleStickVisu]), title="Candle")
        self.tab2 = Panel(child=grid([self.priceMovementVisu]), title="Stock")
        self.tab3 = Panel(child=grid([self.PortfolioVisu]), title="Portfolio")
        tabs = Tabs(tabs=[self.tab1, self.tab2, self.tab3])

        curdoc().add_root(grid([[self.UIPanel, tabs]]))
        curdoc().title = "Visual Trading Backtester"

        self.trader = Trader()

    def create_pricemovement_visu(self):
        self.priceMovementVisu = figure(toolbar_location=None, x_axis_type='datetime', sizing_mode="stretch_both")
        self.priceMovementVisu.line(x='Date',
                                    y='Close',
                                    source=self.stockData,
                                    legend_label="Stock price",
                                    line_color="red")
        self.priceMovementVisu.scatter(x='Date',
                                       y='signal',
                                       source=self.buySignals,
                                       legend_label="Buy signal",
                                       marker="triangle",
                                       size=15,
                                       fill_color='black')
        self.priceMovementVisu.scatter(x='Date',
                                       y='signal',
                                       source=self.sellSignals,
                                       legend_label="Sell signal",
                                       marker="inverted_triangle",
                                       size=15,
                                       fill_color='purple')

        self.priceMovementVisu.legend.location = "top_left"
        self.priceMovementVisu.legend.click_policy = "hide"

        self.priceMovementVisu.xaxis.axis_label = 'Date'
        self.priceMovementVisu.yaxis.axis_label = 'Price [$]'

    # Animation
    def start_animation(self):
        self.stop_animation()
        self.clear_figure()

        self.trader.initialize(self.methodSelector.value,
                               float(self.capitalMoney.value),
                               self.priceMovementVisu,
                               self.tickerSelector.value,
                               self.periodStart.value,
                               self.periodEnd.value)

        self.periodic_callback_id = \
            curdoc().add_periodic_callback(self.update_visu,
                                           int(1000/float(self.simulationSpeed.value)))  # num of ms to wait

    def stop_animation(self):
        if self.periodic_callback_id != 0:  # remove callback if exists
            curdoc().remove_periodic_callback(self.periodic_callback_id)
        self.periodic_callback_id = 0
        self.Bars.data = self.stockData.data

    def reset_column_data_sources(self):
        self.stockData.data = dict(Date=[], High=[], Low=[], Open=[], Close=[], Adj_Close=[], Color=[])
        self.Bars.data = dict(Date=[], High=[], Low=[], Open=[], Close=[], Adj_Close=[], Color=[])

        self.buySignals.data = dict(Date=[], signal=[])
        self.sellSignals.data = dict(Date=[], signal=[])

        self.portfolioData.data = dict(Date=[], holdings=[], cash=[], total=[])

    def clear_figure(self):
        self.reset_column_data_sources()
        self.create_pricemovement_visu()

    # Plots
    def plot_stock_price(self, data):
        new_data = dict(
            Date=[data.iloc[-1].name],
            High=[data.iloc[-1].High],
            Low=[data.iloc[-1].Low],
            Open=[data.iloc[-1].Open],
            Close=[data.iloc[-1].Close],
            Adj_Close=[data.iloc[-1]["Adj Close"]],
            Color=["#7CFC00" if data.iloc[-1].Close > data.iloc[-1].Open else "#F2583E"]
        )
        self.stockData.stream(new_data)
        self.Bars.stream(new_data, 70)

        # if data.iloc[-1].Close > data.iloc[-1].Open:
        #     self.UpBars.stream(new_data, 35)
        # else:
        #     self.DownBars.stream(new_data, 35)

    def plot_buy_sell_signals(self):
        if self.trader.strategy.signals is None:
            return
        curr_position = int(self.trader.get_last_signal().positions)
        if curr_position == 1:
            buy_data = dict(
                Date=[self.trader.get_last_signal().name],
                signal=[self.stockData.data["Close"][-1]]
            )
            self.buySignals.stream(buy_data)
        elif curr_position == -1:
            sell_data = dict(
                Date=[self.trader.get_last_signal().name],
                signal=[self.stockData.data["Close"][-1]]
            )
            self.sellSignals.stream(sell_data)

    def plot_portfolio(self):
        last_portfolio_value = self.trader.get_portfolio_manager().get_last_portfolio_value()
        if last_portfolio_value is None:
            return
        new_data = dict(
            Date=[last_portfolio_value.name],
            holdings=[last_portfolio_value.holdings],
            cash=[last_portfolio_value.cash],
            total=[last_portfolio_value.total]
        )
        self.portfolioData.stream(new_data)

    def plot_strategy_results(self):
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


