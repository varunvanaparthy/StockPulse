import kivy
kivy.require('1.0.6')
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.garden.matplotlib import FigureCanvasKivyAgg
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivy.uix.image import Image, AsyncImage

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import linear_model

class MenuScreen(Screen) :
    selct_comp = StringProperty('None')

    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        root_widget = BoxLayout(orientation = 'vertical')
        companies = ["JSW Steel","Cipla Ltd","Tech Mahindra","Dr Reddy's Labs","Tata Steel","Bharti Infratel","Nestle India",
        "Maruti Suzuki India","Wipro Ltd","Hindustan Unilever"]
        button_grid = GridLayout(cols = 2)
        for company in companies :
            button_grid.add_widget(Button(text = company,height = 50))

        def button_click(instance) :
            self.selct_comp = instance.text
            self.manager.transition.direction = 'left'
            self.manager.current = 'graph'

        for button in button_grid.children[:] :
            button.bind(on_press = button_click)
        root_widget.add_widget(Label(text = '[b]' + "WELCOME TO STOCKPULSE" + '[/b]',markup = True,font_size = '30sp',size_hint_y = None,height = 100))
        root_widget.add_widget(Label(text = '[i]' + "India's trusted market analysis site since 2000...!" + '[/i]',markup = True,font_size = '12sp',size_hint_y = None,height = 0))
        root_widget.add_widget(Label(text = "Select company : ",size_hint_y = None,height = 100))
        root_widget.add_widget(button_grid)
        self.add_widget(root_widget)


class GraphScreen(Screen) :
    X_df = pd.DataFrame()
    Y_df = pd.DataFrame()

    def returnGraph(self,company) :
        file = company + ".csv"
        data = pd.read_csv(file)
        X_cols = data['Date']
        Y_cols = data['Close Price']
        X_cols = X_cols.to_frame()
        Y_cols = Y_cols.to_frame()
        month = X_cols.loc[0,'Date'][3:]
        for index in X_cols.index :
            X_cols.loc[index,'Date'] = X_cols.loc[index,'Date'][0:2]
        self.X_df = X_cols
        self.Y_df = Y_cols
        X_cols = X_cols.to_numpy(dtype = int)
        Y_cols = Y_cols.to_numpy(dtype = float)
        plt.plot(X_cols,Y_cols,color='r',linewidth=1.25)
        plt.scatter(X_cols,Y_cols,color='darkgreen',s=20)
        plt.title(company + "  -  (%s)"% month)
        plt.xlabel("Date")
        plt.ylabel("Closing Price")
        return FigureCanvasKivyAgg(plt.gcf())

    def on_enter(self,*args) :
        company = self.manager.get_screen('menu').selct_comp
        graph = self.returnGraph(company)
        graph.height = 2500
        next_page = BoxLayout(orientation = 'vertical')
        choice = FloatLayout(size_hint = (1.0,0.1))
        prev_btn = Button(text = "Prev.",size_hint=(0.2,0.2),pos_hint={'x':0.01,'y':0.9})
        yes_btn = Button(text = "YES",size_hint=(0.1,0.2),pos_hint={'x':0.40,'y':0.9})
        no_btn = Button(text = "NO",size_hint=(0.1,0.2),pos_hint={'x':0.51,'y':0.9})

        def callback(instance) :
            if instance.text == "Prev." :
                plt.cla()
                self.manager.transition.direction = 'right'
                self.manager.current = 'menu'
            else :
                self.manager.transition.direction = 'left'
                if instance.text == "YES" :
                    self.manager.current = 'estm'
                else :
                    self.manager.current = 'tqpage'

        yes_btn.bind(on_press = callback)
        no_btn.bind(on_press = callback)
        prev_btn.bind(on_press = callback)
        choice.add_widget(prev_btn)
        choice.add_widget(yes_btn)
        choice.add_widget(no_btn)
        next_page.add_widget(graph)
        next_page.add_widget(Label(text = "Do you want prediction ..?",size_hint_y = None,height = 50))
        next_page.add_widget(choice)
        self.manager.get_screen('graph').add_widget(next_page)


class EstimateScreen(Screen) :
    def on_enter(self,*args) :
        plt.cla()
        root_widget = FloatLayout()
        X_train = self.manager.get_screen('graph').X_df
        Y_train = self.manager.get_screen('graph').Y_df
        X_train = X_train.to_numpy(dtype = int)
        Y_train = Y_train.to_numpy(dtype = float)
        regr = linear_model.LinearRegression()
        regr.fit(X_train,Y_train)
        X_test = [(X_train[-1]+i) for i in range(1,8)]
        X_test = np.array(X_test)
        X_test = X_test.reshape(len(X_test),1)
        Y_est = regr.predict(X_test)
        plt.plot(X_test,Y_est,color='c',linewidth=2.0)
        plt.scatter(X_test,Y_est,color='r',s=20)
        plt.title("Estimate data of " + self.manager.get_screen('menu').selct_comp + " for the next 7 days : ")
        plt.xlabel("Extended Days")
        plt.ylabel("Closing Price")
        X_test = [X_test[i][0] for i in range(len(X_test))]
        Y_est = [round(Y_est[i][0],2) for i in range(len(Y_est))]
        for i_x,i_y in zip(X_test,Y_est) :
            plt.text(i_x,i_y, "  " + str(i_y))

        def callback(instance) :
            if instance.text == "Prev." :
                plt.cla()
                self.manager.transition.direction = 'right'
                self.manager.current = 'graph'

        prev_btn = Button(text="Prev.",size_hint=(0.2,0.05),pos_hint={'x':0.01,'y':0.01})
        prev_btn.bind(on_press = callback)
        root_widget.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        root_widget.add_widget(prev_btn)
        self.add_widget(root_widget)

class ThankYouScreen(Screen) :
    def __init__(self, **kwargs):
        super(ThankYouScreen, self).__init__(**kwargs)
        img = Image(source='Thank You.jpg')
        self.add_widget(img)

class ScrnMgr(ScreenManager) :
    def __init__(self, **kwargs):
        super(ScrnMgr, self).__init__(**kwargs)
        self.add_widget(MenuScreen(name='menu'))
        self.add_widget(GraphScreen(name='graph'))
        self.add_widget(EstimateScreen(name='estm'))
        self.add_widget(ThankYouScreen(name='tqpage'))
        self.current = 'menu'

class StockPulseApp(App) :
    def build(self) :
        sm = ScrnMgr()
        return sm

if __name__ == '__main__':
    StockPulseApp().run()
