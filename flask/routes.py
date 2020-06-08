# imports
import numpy as np
import pickle
from flask import Flask,request, Response, render_template, jsonify
from werkzeug.utils import secure_filename

# libraries for geting the api
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib
import os

PEOPLE_FOLDER = os.getcwd()


# initialize the flask app
app = Flask('my_app')

app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER



# route 1: show a form to the user
@app.route('/')
@app.route('/form')
def form():
    return render_template('form.html')
# use flask's render_template function to display an html page
# route 2: show the output

@app.route('/submit', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['filename']
        address=request.form['address']
        f.save('./upload' + secure_filename(f.filename))






        #code for getting the api info
        address_1=address

        url="https://maps.googleapis.com/maps/api/geocode/json?address="+address_1+"&key=AIzaSyCOjoekeAEAG2NK86lGORMb8-WU5iqCN-g"
        r=requests.get(url)
        address = json.loads(r.text)

        lat=address['results'][0]['geometry']["location"]["lat"]
        lon=address['results'][0]['geometry']["location"]["lng"]
        url='http://api.openweathermap.org/data/2.5/forecast?lat='+str(lat)+'&lon='+str(lon)+'&appid=d5edb521b2c9f31b48aa50d09fc6be71'
        r=requests.get(url)
        weather = json.loads(r.text)


        #extracting the weather data as a data frame
        df = pd.DataFrame()
        for i in range(len(weather["list"])):
            df=pd.concat([df,pd.DataFrame.from_dict(weather["list"][i]['weather'][0],orient='index').transpose()])


        #extract the clouds percentage
        clouds=[]
        for i in range(len(weather["list"])):
            clouds.append(weather["list"][i]['clouds']["all"])

        df["clouds"]=clouds

        #extracting the humidity
        humidity=[]
        for i in range(len(weather["list"])):
            humidity.append(weather["list"][i]["main"]["humidity"])

        df["humidity"]=humidity

         #extracting the wind speed
        wind=[]
        for i in range(len(weather["list"])):
            wind.append(weather["list"][i]["wind"]["speed"])

        df["wind"]=wind


        #extracting the tempreture
        tempreture=[]
        for i in range(len(weather["list"])):
            tempreture.append(weather["list"][i]["main"]["temp"])


        df["tempreture"]=tempreture



        # extract time and use it as index
        time=np.array([])
        for i in range(len(weather["list"])):
            time=np.append(time,weather["list"][i]['dt_txt'])

        df=df.set_index(time)


        #droping unwanted columns
        df.drop(columns=["id","icon"],inplace=True)











        #location plot

        from mpl_toolkits.basemap import Basemap
        import matplotlib.pyplot as plt
        plt.figure(figsize=(12,6))
        m = Basemap(projection='mill',
            llcrnrlat = 25,
            llcrnrlon = -130,
            urcrnrlat = 50,
            urcrnrlon = -60,
            resolution='l')

        m.drawcoastlines()
        m.drawcountries(linewidth=2)
        m.drawstates(color='b')

        LAlat, LAlon = lat, lon
        xpt, ypt = m(LAlon, LAlat)
        m.plot(xpt, ypt, 'r^', markersize=15)
        plt.savefig('static/location.png', dpi=235);


        #full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'location.png')



        import matplotlib.pyplot as plt
        import matplotlib


        tmean=df['tempreture'].rolling(5,center=True).mean()
        rhmean =df['humidity'].rolling(5,center=True).mean()
        wspdmean=df['wind'].rolling(5,center=True).mean()
        cldsmean =df['clouds'].rolling(5,center=True).mean()


        matplotlib.style.use('bmh')

        fig, axes = plt.subplots(nrows=4, ncols=1, figsize=(15, 10))

        df['tempreture'].plot(ax=axes[0], color='dodgerblue',sharex=True)
        tmean.plot(ax=axes[0], kind='line',color='darkorchid', sharex=True)
        axes[0].set_ylabel('temperature [kelvin]')

        df['humidity'].plot(ax=axes[1], color='dodgerblue',sharex=True)
        rhmean.plot(ax=axes[1], kind='line',color='darkorchid', sharex=True)
        axes[1].set_ylabel('humidity [%]')

        df['clouds'].plot(ax=axes[2], color='dodgerblue',sharex=True)
        cldsmean.plot(ax=axes[2], kind='line',color='darkorchid', sharex=True)
        axes[2].set_ylabel('clouds [%]')

        df['wind'].plot(ax=axes[3], color='dodgerblue',sharex=False)
        wspdmean.plot(ax=axes[3], kind='line',color='darkorchid', sharex=True)
        axes[3].set_ylabel('wind [m s$^{-1}$]')
        plt.xticks(rotation=45);
        plt.savefig('static/weather.png', dpi=235);

        #full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'weather.png')



        #code for running the Yolov3 model


        #path for the imported image to apply the model









        #yolov3 output image and the n number of solar panels












        #plot the energy production plots
        #calcualting the solar energy production based on the rule of thumb


        a=[]
        for i in df.index:
            if (int(i[11:13])>=6) &(int(i[11:13])<=18):
                a.append(0.9)
            elif(int(i[11:13])>18) &(int(i[11:13])<23):
                a.append(0.1)
            else:
                a.append(0)

        n=3           #number of solar panel detected
        area=n*6*1.65 #in squared meter   area of each solar panel is 1.65 m2 and assumption we have 6 in each of the detected
        energy_produced=0.1*area          #the solar energy in kw
        df["hourley_energy"]= (100-df["clouds"])*energy_produced*0.2*a      #hourley produced based on weather situation

        #plot the hourley soalr panel energy generation
        plt.figure(figsize=(15,5))
        df['hourley_energy'].plot(color='dodgerblue',sharex=True).set_ylabel('solar_energy[kw]')
        plt.xticks(rotation=45)
        plt.savefig('static/energy_produced.png', dpi=235);


        #user_image =  'static/energy_produced.png';
        #user_weather = 'static/energy_produced.png';





        return render_template('results.html')#,user_image = full_filename, user_weather=user_weather)












# Call app.run(debug=True) when python script is called
if __name__ == '__main__':
    app.run(debug=True) #if you run app.py from terminal
