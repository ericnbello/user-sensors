import faker
import wx
import random
import json
from datetime import datetime
import csv
import pandas as pd
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

fake = faker.Faker() # constructs new Faker object
SAMPLING_TIME = 60*60*6 # 6 hours

# Creates and returns faker time series generator
def get_series():
    series = fake.time_series(start_date='-5y+23d', end_date='now', precision=SAMPLING_TIME)
    return series

sensor_records = set() # ensures no duplicate sensor records
sensor_records_no = 500 # number of sensor records per user

# populate the set with 1000 unique sensor records
while len(sensor_records) < sensor_records_no:
    sensor_records.add(fake.date())
    sensor_records.add(fake.time())
    sensor_records.add(fake.random_int())
    sensor_records.add(fake.random_int())
    sensor_records.add(fake.random_int())
    sensor_records.add(fake.random_int())

def gen_date():
    series = get_series()
    for sample in series:
        sample_date = datetime.strptime(str(sample[0]), '%Y-%m-%d %H:%M:%S').date()
        yield sample_date
        
def gen_time():
    series = get_series()
    for sample in series:
        sample_time = datetime.strptime(str(sample[0]), '%Y-%m-%d %H:%M:%S').time()
        yield sample_time
    
# Generates 500 Sensor Records per User Record
def get_sensor_data(sensor_records):
    sensor_date = gen_date()
    sensor_time = gen_time()
    sensor_data = []
    for sensor in sensor_records:
        sensor = { 
                  'date': next(sensor_date),
                  'time': next(sensor_time),
                  'outside temperature': fake.random_int(min=70, max=95),
                  'outside humidity': fake.random_int(min=50, max=95),
                  'room temperature': fake.random_int(min=70, max=95) - fake.random_int(min=0, max=10),
                  'room humidity': fake.random_int(min=50, max=95) - fake.random_int(min=0, max=10),
                }
        sensor_data.append(sensor)
    return sensor_data

user_records = set() # ensures no duplicate user records
user_records_no = 500 # number of users 

# populate the set with 500 unique users
while len(user_records) < user_records_no:
    user_records.add(fake.first_name())
    user_records.add(fake.last_name())
    user_records.add(fake.user_name())
    user_records.add(fake.address())
    user_records.add(fake.email())

# Generates random First/Last names and associates with Gender
def get_random_name_and_gender():
    skew = .5 # 50% of users will be female
    male = random.random() > skew
    if male:
        return fake.first_name_male(), fake.last_name_male(), 'M'
    else:
        return fake.first_name_female(), fake.last_name_female(), 'F'

# Generates User Records with desired attributes
def get_users(user_records):
    first_name, last_name, gender = get_random_name_and_gender()
    users = []
    for user in user_records:
        user = {
                'first name': first_name,
                'last name': last_name,
                'age': fake.random_int(18, 100),
                'gender': gender,
                'username': fake.user_name(),
                'address': fake.address(),
                'email': fake.email(),
                'sensor data': get_sensor_data(sensor_records),
                }
        users.append(user)
    return users
        
class windowClass(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(windowClass, self).__init__(*args, **kwargs)
        
        # Allows for text output to print within GUI window
        self.my_text = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        
        # Creates text output area in GUI window
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.my_text, 1, wx.ALL|wx.EXPAND)
                
        self.SetSizer(sizer)
        self.Centre()
        self.basicGUI()

    def basicGUI(self):
        panel = wx.Panel(self)
        menuBar = wx.MenuBar()

        # Dropdown Menu Buttons
        fileButton = wx.Menu()
        statisticsButton = wx.Menu()
        
        menuBar.Append(fileButton, 'File')
        menuBar.Append(statisticsButton,'Statistics')

        self.SetMenuBar(menuBar)

        # File Menu
        exitItem = fileButton.Append(wx.ID_EXIT, 'Exit', 'Exit program ...')
        generateItem  = fileButton.Append(wx.ID_ANY, 'Generate IoT', 'Generating IoT data...')
        saveJSONItem  = fileButton.Append(wx.ID_ANY, 'Save as JSON', 'Saving as JSON file...')
        saveCSVItem  = fileButton.Append(wx.ID_ANY, 'Save as CSV', 'Saving as CSV file...')

        # Binding File menu buttons to events
        self.Bind(wx.EVT_MENU, self.OnQuit, exitItem)
        self.Bind(wx.EVT_MENU, self.OnGenerateIoT, generateItem)
        self.Bind(wx.EVT_MENU, self.OnSaveAsJSON, saveJSONItem)
        self.Bind(wx.EVT_MENU, self.OnSaveAsCSV, saveCSVItem)
        
        # Statistics Menu
        descriptionItem  = statisticsButton.Append(wx.ID_ANY, 'Description', 'Description of data')
        plotAItem  = statisticsButton.Append(wx.ID_ANY, 'Plot A', 'Plotting A...')
        plotBItem  = statisticsButton.Append(wx.ID_ANY, 'Plot B', 'Plotting B...')
        plotCItem  = statisticsButton.Append(wx.ID_ANY, 'Plot C', 'Plotting C...')
        
        # Binding Statistics menu buttons to events
        self.Bind(wx.EVT_MENU, self.OnStatsDescription, descriptionItem)
        self.Bind(wx.EVT_MENU, self.OnPlotA, plotAItem)
        self.Bind(wx.EVT_MENU, self.OnPlotB, plotBItem)
        self.Bind(wx.EVT_MENU, self.OnPlotC, plotCItem)

        self.statusbar = self.CreateStatusBar(1)

        # Window title
        self.SetTitle('IoT User and Sensor Data ')
        self.Show(True)

    # Quit the program
    def OnQuit(self, e):
        yesNoBox = wx.MessageDialog(None, 'Are you sure you want to Quit?', 'Question', wx.YES_NO)
        yesNoAnswer = yesNoBox.ShowModal()
        yesNoBox.Destroy()
        if yesNoAnswer == wx.ID_YES:
            self.Close()

    # View Generated IoT Data
    def OnGenerateIoT(self, e):
        users = get_users(user_records)
        self.my_text.WriteText(str(users[:3])) # shows preview of generated IoT data

    # Enables saving IoT data to JSON file 
    def OnSaveAsJSON(self, e):
        with wx.FileDialog(self, "Save JSON file", wildcard="JSON files (*.json)|*.json",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'w') as file:
                    users = get_users(user_records)
                    json_data = json.dumps(str(users), indent=4, sort_keys=False)
                    json.dump(json_data, file)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)

    # Enables saving IoT data to CSV file
    def OnSaveAsCSV(self, e):
        with wx.FileDialog(self, "Save CSV file", wildcard="CSV files (*.csv)|*.csv",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'w') as file:
                    users = get_users(user_records)
                    csv_writer = csv.writer(file, delimiter=',')
                    csv_writer.writerow(users)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)
        
    # Enables viewing statistics of IoT data
    def OnStatsDescription(self, e):
        sensors = get_sensor_data(sensor_records)
        df = pd.DataFrame(sensors)
        
        # Prints output to GUI window
        self.my_text.WriteText('Statistics of IoT Sensor Data:')
        self.my_text.WriteText('\n----------------\n')
        self.my_text.WriteText(df.describe().to_string().strip())

    # Plots histogram when 'Plot A' button clicked
    def OnPlotA(self, e):
        sensors = get_sensor_data(sensor_records)
        df = pd.DataFrame(sensors)
        df[['outside temperature']].plot(kind='hist',bins=4,rwidth=0.8, title="Outside Temperature (˚F)")        
        plt.show()
    
    # Plots line graph when 'Plot B' button clicked
    def OnPlotB(self, e):
        sensors = get_sensor_data(sensor_records)
        
        # separate lists of data are needed for plotting
        out_temps_list = []
        room_temps_list = []
        
        # appending rows of data to individual lists
        for sensor in sensors:
            out_temp = sensor['outside temperature']
            out_temps_list.append(out_temp)
            room_temp = sensor['room temperature']
            room_temps_list.append(room_temp)
            
        # merge lists together
        merged = zip(out_temps_list, room_temps_list)
        
        # create DataFrame from merged lists for easy plotting
        df = pd.DataFrame(merged)
        df.columns = ['Outside Temperature','Room Temperature']
        df.plot.line()
        plt.show()
        
    # Plots histogram when 'Plot C' button clicked
    def OnPlotC(self, e):
        users = get_users(user_records)
        
        # separate lists are needed for plotting each type of data
        out_temps_list = [] 
        out_hums_list = []
        room_temps_list = []
        room_hums_list = []
        
        # appending rows of data to individual lists
        for user in users: 
            sensors = user['sensor data']
            for sensor in sensors: 
                outside_temp = sensor['outside temperature']
                out_temps_list.append(outside_temp)
                outside_hum = sensor['outside humidity']
                out_hums_list.append(outside_hum)
                room_temp = sensor['room temperature']
                room_temps_list.append(room_temp)
                room_hum = sensor['room humidity']
                room_hums_list.append(room_hum)
        
        # merge all lists together
        merged = zip(out_temps_list,out_hums_list,room_temps_list,room_hums_list)
        
        # create DataFrame from merged lists for easy plotting
        df = pd.DataFrame(merged) 
        df.columns = ['Outside Temperature','Outside Humidity','Room Temperature','Room Humidity']
        df.hist(column=['Outside Temperature','Outside Humidity','Room Temperature','Room Humidity'], sharex=True)
        plt.show() 

# Main function runs window
def main():
    app = wx.App()
    windowClass(None, 0, size=(500,400))
    app.MainLoop()

main()