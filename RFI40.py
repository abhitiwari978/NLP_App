import sys
import pandas as pd
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication,QRadioButton, QMainWindow, QAction, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QComboBox,QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt, QTimer
import time
import warnings
import os
import math
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class RFIApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.threshold_values = []  # List to store threshold values
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_plot)
        self.frequency_values = None
        self.amplitude_values = None
        self.clean_amplitudes = None
        self.selected_band = None
        self.legend_item = None
        self.plot_widget
        self.f_values = []
        # self.p=[]
        self.plot_gray
        self.cumulative_amplitude1 = np.array([])
        self.cumulative_amplitude2 = np.array([])
        self.cumulative_time1 = 0
        self.index1 = 0
        self.index2 = 0
        self.cumulative_time2 = 0
        self.index = 0
        self.pre_before=0
        self.post_before=0
        self.pre_after=0
        self.post_after=0
        self.cbar=None
        self.glob_index=None
        self.date = np.array([])
        self.time = np.array([])


    def initUI(self):
        self.setWindowTitle('GMRT RFI Detection')
        self.setGeometry(70, 40, 1800, 850)  # Adjusted window size

        # Create actions for menu bar
        start_action = QAction('Start', self)
        stop_action = QAction('Stop', self)
        settings_action = QAction('Settings', self)
        help_action = QAction('Help', self)

        # Add menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        file_menu.addAction(start_action)
        file_menu.addAction(stop_action)

        settings_menu = menubar.addMenu('Settings')
        settings_menu.addAction(settings_action)

        help_menu = menubar.addMenu('Help')
        help_menu.addAction(help_action)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout for central widget
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Center heading with larger font size
        heading_label = QLabel('GMRT RFI Detection')
        heading_label.setAlignment(Qt.AlignCenter)
        heading_label.setStyleSheet("color: #D4AF37; font-size: 36px; font-weight: bold;")
        layout.addWidget(heading_label)

        # Antenna selection section
        antenna_selection_layout = QHBoxLayout()
        layout.addLayout(antenna_selection_layout)

        antenna_selection_label = QLabel('Antenna Selection:')
        antenna_selection_label.setStyleSheet("color: #D4AF37; font-size: 18px;")
        antenna_selection_layout.addWidget(antenna_selection_label)

        # Define antenna names
        antenna_names = ['C00', 'C01', 'C02', 'C03', 'C04', 'C05', 'C06', 'C08', 'C09', 'C10',
                         'C11', 'C12', 'C13', 'C14', 'W01', 'W02', 'W03', 'W04', 'W05', 'W06',
                         'E02', 'E03', 'E04', 'E05', 'E06', 'S01', 'S02', 'S03', 'S04', 'S06']

        # Create combo box for antenna selection
        self.antenna_combo = QComboBox()
        self.antenna_combo.addItems(antenna_names)
        antenna_selection_layout.addWidget(self.antenna_combo)

        # Button to confirm antenna selection
        self.confirm_button = QRadioButton('SELECT')
        self.confirm_button.clicked.connect(self.confirm_antenna)
        self.confirm_button.setStyleSheet("max-width: 100px ;font-size: 20px;")
        antenna_selection_layout.addWidget(self.confirm_button)

        reset_button = QPushButton("R E S E T")
        reset_button.clicked.connect(self.reset_plot)
        reset_button.setStyleSheet("background-color: red; color: black; font-size: 20px;")
        antenna_selection_layout.addWidget(reset_button)

        # Input fields for start and end frequencies
        start_freq_label = QLabel('        Start Frequency (MHz):')
        start_freq_label.setStyleSheet("color: blue; font-size: 20px;")
        antenna_selection_layout.addWidget(start_freq_label)

        self.start_freq_input = QLineEdit()
        self.start_freq_input.setStyleSheet("background-color: white; color: black; font-size: 14px; max-width: 200px;")
        antenna_selection_layout.addWidget(self.start_freq_input)

        end_freq_label = QLabel('End Frequency (MHz):')
        end_freq_label.setStyleSheet("color: blue; font-size: 20px;")
        antenna_selection_layout.addWidget(end_freq_label)

        self.end_freq_input = QLineEdit()
        self.end_freq_input.setStyleSheet("background-color: white; color: black; font-size: 14px; max-width: 200px;")
        antenna_selection_layout.addWidget(self.end_freq_input)

        # Button to update the graph
        update_graph_button = QPushButton('U P D A T E')
        update_graph_button.clicked.connect(self.update_graph)
        update_graph_button.setStyleSheet("background-color: lightgreen; color: black; font-size: 20px;")
        antenna_selection_layout.addWidget(update_graph_button)

        #reset update button
        defaultrange = QPushButton('DEFAULT')
        defaultrange.clicked.connect(self.default_range)
        defaultrange.setStyleSheet("background-color: yellow; color: black; font-size: 20px;")
        antenna_selection_layout.addWidget(defaultrange)
        
        l = QHBoxLayout()
        layout.addLayout(l)


        # Visualization section
        self.plot_widget = pg.PlotWidget()
        l.addWidget(self.plot_widget)
        
        #table
        self.grid=QTableWidget()
        self.grid.setRowCount(13)
        self.grid.setColumnCount(2)
        self.grid.setFixedSize(195, 490)
        l.addWidget(self.grid)

        self.data = []

        self.populate_table()


        self.grid.verticalHeader().setVisible(False)
        self.grid.horizontalHeader().setVisible(False)

        # Set size of cells
        self.grid.horizontalHeader().setDefaultSectionSize(85)
        self.grid.verticalHeader().setDefaultSectionSize(10)

        # antenna_selection_layout.setStretchFactor(self.grid, 1)

    
        # self.plot_gray = pg.PlotWidget()                    #note
        self.figure, self.ax = plt.subplots(1,2)
        self.plot_gray=FigureCanvas(self.figure)
        self.plot_gray.setFixedSize(1880, 310)
        layout.addWidget(self.plot_gray)

        self.show()

    def populate_table(self):
        for i, row in enumerate(self.data):
            for j, item in enumerate(row):
                self.grid.setItem(i, j, QTableWidgetItem(str(item)))
    
    def default_range(self):
        # Filter frequency values within the specified range
        
        filtered_frequency_values = self.frequency_values
        filtered_amplitude_values = self.amplitude_values
        filtered_clean_amplitudes = self.clean_amplitudes

        # Update the plot with the filtered data
        legend = df.iloc[0, 2]  # Get legend value for current row
        self.plot_data(filtered_amplitude_values, filtered_clean_amplitudes, filtered_frequency_values, legend)

        # Set y-axis range based on the filtered data
        min_value = min(np.min(filtered_amplitude_values), np.min(filtered_clean_amplitudes))
        max_value = max(np.max(filtered_amplitude_values), np.max(filtered_clean_amplitudes))
        self.plot_widget.setYRange(min_value, max_value)

        # Set x-axis range to focus on the specified frequency range
        # self.plot_widget.setXRange(df.iloc[index,3]/1000000,df.iloc[index,4]/1000000)
        self.plot_widget.plotItem.vb.setLimits(xMin=df.iloc[index,3]/1000000,xMax=df.iloc[index,4]/1000000)


    def reset_plot(self):
        self.confirm_button.setChecked(False)
        dataset_dir ="./data"

        # List all files in the directory
        #  # List all files in the directory
        # dataset_files = sorted(os.listdir(dataset_dir), key=lambda f: os.path.getmtime(os.path.join(dataset_dir, f)))

        dataset_files = os.listdir(dataset_dir)

        for file_name in dataset_files:
          file_path = os.path.join(dataset_dir, file_name)
          # List all files in the directory
        #   dataset_files = sorted(os.listdir(dataset_dir), key=lambda f: os.path.getmtime(os.path.join(dataset_dir, f)))

          if os.path.isfile(file_path):
            # file_name = dataset_files[-1]  # Select the most recent file
            # file_path = os.path.join(dataset_dir, file_name)
            # # Check if it's a file (not a directory)
            # if os.path.isfile(file_path):
                # Read data from text file
                df = pd.read_csv(file_path, delimiter='\t', header=None)

                # Extract amplitude values from each row starting from the 11th column
                amplitude_df = df.iloc[:, 12:]
                # Iterate through rows and perform RFI mitigation
                for index, row in amplitude_df.iterrows():
                    rfi_app.amplitude_values = row.iloc[:].values

                    # Perform RFI mitigation on the set of amplitude values
                    rfi_app.clean_amplitudes = rfi_app.mitigate_rfi(rfi_app.amplitude_values)

                    # Generate x-axis values for frequency from 500 to 1000
                    rfi_app.frequency_values = np.linspace(df.iloc[0,3]/1000000, df.iloc[0,4]/1000000, len(rfi_app.amplitude_values))
                    

                    #first logic for detection
                    if index >= 60:
                        # Calculate the difference in dB between the current row and the row 60 indices before it
                        current_amplitudes = row.iloc[:]  
                        past_amplitudes = df.iloc[index - 60, 12:]  # Amplitude values from the row 60 indices before
        
                        # Calculate the difference in dB
                        amplitude_difference = (current_amplitudes - past_amplitudes).abs()
                        t=[]
                        # Check if any difference exceeds 2 dB
                        if not amplitude_difference.empty and 0 in amplitude_difference.index:
                            for j in range (0,len(amplitude_difference)):

                                if(amplitude_difference[j]>6):  
                                    t.append(rfi_app.frequency_values[j])
                                else:
                                    rfi_app.add(t)

                    # Plot data inside the GUI with a delay of 1 second
                    legend = df.iloc[index, 2]  # Get legend value for current row
                    rfi_app.plot_data(rfi_app.amplitude_values, rfi_app.clean_amplitudes, rfi_app.frequency_values, legend)
                

                    # Show the updated plot
                    app.processEvents()  # Process GUI events to update the plot
                    time.sleep(1)  # Introduce a delay of 1 second

    def confirm_antenna(self):
        self.confirm_button.setChecked(False)
        self.antenna_name = self.antenna_combo.currentText()
        print(type(self.antenna_name))
        QMessageBox.information(self, "Antenna Confirmation", f"Selected antenna: {self.antenna_name}")

        if self.cumulative_amplitude1.size > 0 or self.cumulative_amplitude2.size > 0 :
            # Save the current plot as an image
            # self.date[-1]=datetime.datetime.today()
            clean_date_start = self.date[0].replace('/', '-')
            clean_time_start = self.time[0].replace(':', '-')
            clean_date_end = self.date[-1].replace('/', '-')
            clean_time_end = self.time[-1].replace(':', '-')
            plt.savefig(f'gray_scale_plot_img.png')
            # plt.savefig(f'p_{clean_date_start}_{clean_time_start}_to_{clean_date_end}_{clean_time_end}.png')
            # plt.savefig(f'previous_plot_{self.index2}.png')
            self.cumulative_amplitude1 = np.array([])
            self.cumulative_amplitude2 = np.array([])
            self.date = np.array([])
            self.time=np.array([])
            self.cumulative_time1 = 0
            self.index1 = 0
            self.index2 = 0
            self.cumulative_time2 = 0
        self.plot_for_selected_antenna()

    def plot_for_selected_antenna(self):
        if self.antenna_name is None:
            return

        dataset_dir ="./data"
        #  # List all files in the directory
        # dataset_files = sorted(os.listdir(dataset_dir), key=lambda f: os.path.getmtime(os.path.join(dataset_dir, f)))
        dataset_files = os.listdir(dataset_dir)

        for file_name in dataset_files:
        #   file_path = os.path.join(dataset_dir, file_name)
          
        #   # List all files in the directory
        #   dataset_files = sorted(os.listdir(dataset_dir), key=lambda f: os.path.getmtime(os.path.join(dataset_dir, f)))

          if os.path.isfile(file_path):
            # file_name = dataset_files[-1]  # Select the most recent file
            # file_path = os.path.join(dataset_dir, file_name)

            # if os.path.isfile(file_path):
                df = pd.read_csv(file_path, delimiter='\t', header=None)
                amplitude_df2 = df[df[2].apply(lambda x: x.split()[0]) == self.antenna_name]  # Filter rows by antenna name
                amplitude_df = amplitude_df2.iloc[:,12:]
                
                 # Reset index of amplitude_df
                amplitude_df = amplitude_df.reset_index(drop=True)

                # Iterate through rows and perform RFI mitigation
                for index, row in amplitude_df.iterrows():
                    rfi_app.amplitude_values = row.iloc[:].values
                    
                    self.index=index

                    # Perform RFI mitigation on the set of amplitude values
                    rfi_app.clean_amplitudes = rfi_app.mitigate_rfi(rfi_app.amplitude_values)

                    #check index start for looking frequencychanges from previous row
                    if(index>0):
                       self.pre_before=amplitude_df2.iloc[index-1,3]
                       self.pre_after=amplitude_df2.iloc[index-1,4]
                       self.post_before=amplitude_df2.iloc[index,3]
                       self.post_after=amplitude_df2.iloc[index,4]
  
                    # Generate x-axis values for frequency from 500 to 1000
                    rfi_app.frequency_values = np.linspace(amplitude_df2.iloc[index,3]/1000000, amplitude_df2.iloc[index,4]/1000000, len(rfi_app.amplitude_values))

                    if index >= 60:
                        # Calculate the difference in dB between the current row and the row 60 indices before it
                        current_amplitudes = row.iloc[:]  
                        past_amplitudes = df.iloc[index - 60, 12:]  # Amplitude values from the row 60 indices before
        
                        # Calculate the difference in dB
                        amplitude_difference = (current_amplitudes - past_amplitudes).abs()
                        t=[]
                        # Check if any difference exceeds 2 dB
                        if not amplitude_difference.empty and 0 in amplitude_difference.index:
                            for j in range (0,len(amplitude_difference)):

                                if(amplitude_difference[j]>6):  
                                    t.append(rfi_app.frequency_values[j])
                                else:
                                    rfi_app.add(t)
                    
                    if ((self.pre_before != self.post_before) or (self.pre_after != self.post_after)):
                               self.frequency_changed()


                    # Plot data inside the GUI with a delay of 1 second
                    legend = amplitude_df2.iloc[index, 2]  # Get legend value for current row
                    rfi_app.plot_data(rfi_app.amplitude_values, rfi_app.clean_amplitudes, rfi_app.frequency_values, legend)
                    
                    # Plot data as grayscale
                    self.plot_grayscale(rfi_app.amplitude_values, rfi_app.frequency_values, legend,amplitude_df2.iloc[index,0],amplitude_df2.iloc[index,1])
                    

                    # Show the updated plot
                    app.processEvents()  # Process GUI events to update the plot
                    time.sleep(1)  # Introduce a delay of 1 second

    def frequency_changed(self):
        if self.cumulative_amplitude1.size > 0 or self.cumulative_amplitude2.size > 0 :
            # Save the current plot as an image
            clean_date_start = self.date[0].replace('/', '-')
            clean_time_start = self.time[0].replace(':', '-')
            clean_date_end = self.date[-1].replace('/', '-')
            clean_time_end = self.time[-1].replace(':', '-')
            # plt.savefig(f'p_{clean_date_start}_{clean_time_start}_to_{clean_date_end}_{clean_time_end}.png')
            plt.savefig(f'gray_scale_plot_img.png')

            # plt.savefig(f'previous_plot_{self.index2}.png')
            self.cumulative_amplitude1 = np.array([])
            self.cumulative_amplitude2 = np.array([])
            self.date = np.array([])
            self.time=np.array([])
            self.cumulative_time1 = 0
            self.index1 = 0
            self.index2 = 0
            self.cumulative_time2 = 0

    def plot_grayscale(self,amplitude_values, frequency_values, legend,date,time):
       if self.index % 2 == 0: 
          self.date = np.append(self.date,date)
          self.time = np.append(self.time,time)
          self.cumulative_amplitude1 = np.append(self.cumulative_amplitude1, amplitude_values)
          self.ax[0].clear()
          im=self.ax[0].imshow(self.cumulative_amplitude1.reshape(-1, len(amplitude_values)), aspect='auto', cmap='viridis', origin='lower', extent=[frequency_values.min(), frequency_values.max(), 0, self.cumulative_time1 + 1])
          self.ax[0].set_xlabel('Frequency (MHz)')
          self.ax[0].set_ylabel('Time (s)')
          self.ax[0].set_title(f'Grayscale Plot for {legend}')
          self.plot_gray.draw()
          self.index1 += 1
          self.cumulative_time1 += 1
       else:
          self.date = np.append(self.date,date)
          self.time = np.append(self.time,time)
          self.cumulative_amplitude2 = np.append(self.cumulative_amplitude2, amplitude_values)
          self.ax[1].clear()
          im=self.ax[1].imshow(self.cumulative_amplitude2.reshape(-1, len(amplitude_values)), aspect='auto', cmap='viridis', origin='lower', extent=[frequency_values.min(), frequency_values.max(), 0, self.cumulative_time2 + 1])
          self.ax[1].set_xlabel('Frequency (MHz)')
          self.ax[1].set_ylabel('Time (s)')
          self.ax[1].set_title(f'Grayscale Plot for {legend}')
          self.plot_gray.draw()
          self.index2 += 1
          self.cumulative_time2 += 1
       # Add color bar to the subplot
       if self.cbar is None:
          self.cbar = plt.colorbar(im, ax=self.ax.ravel().tolist())
          self.cbar.set_label('Amplitude')

       self.plot_gray.draw()

    def plot_data(self, amplitude_values, clean_amplitudes, frequency_values, legend):
        
        p=[]
        for index in range(len(amplitude_values)):

            if((amplitude_values[index]-clean_amplitudes[index])>6):
                p.append(frequency_values[index])
            else:
                if p:
                  mid=len(p)//2
                  self.f_values.append(p[mid])
                  p=[]


        # Clear previous plot
        self.plot_widget.clear()

        # Plot "Before mitigation"
        before_mitigation_curve = self.plot_widget.plot(frequency_values, amplitude_values, pen='r', name=f'{legend}')

        # Plot "After mitigation"
        # after_mitigation_curve = self.plot_widget.plot(frequency_values, clean_amplitudes, pen='g', name=f'{legend}: After mitigation')

        # Calculate threshold value for the current row
        threshold = np.median(amplitude_values) + rfi_app.std_around_median(amplitude_values)
        self.threshold_values.append(threshold)  # Store the threshold value

        # Add threshold line for each row
        threshold_max = np.max(self.threshold_values)+6
        threshold_line = pg.InfiniteLine(pos=threshold_max, angle=0, pen='b')
        # self.plot_widget.addItem(threshold_line)                                              threshold line

        # Set axis labels
        self.plot_widget.setLabel('bottom', text='Frequency (MHz)')
        self.plot_widget.setLabel('left', text='Amplitude (dB)')
        

        # Set y-axis range
        self.plot_widget.setYRange(-110, -10)

        # Add LinearRegionItem for highlighting fixed y-axis regions
        freq_start = np.min(frequency_values)
        freq_end = np.max(frequency_values)
   
   
        self.plot_widget.setXRange(freq_start, freq_end)

        for i in self.f_values:
        # if np.any((frequency_values >= freq_start) & (frequency_values <= freq_end) & (amplitude_values > threshold)):
            message_label = pg.TextItem(text='RFI', color=(255, 0, 0))
            message_label.setPos(i, np.max(clean_amplitudes))  
            self.plot_widget.addItem(message_label)  

        self.f_values=[]

        # for i in self.p:
        # # if np.any((frequency_values >= freq_start) & (frequency_values <= freq_end) & (amplitude_values > threshold)):
        #     message_label = pg.TextItem(text='nnnrfi', color=(255, 0, 0))
        #     message_label.setPos(i, np.max(clean_amplitudes))  
        #     self.plot_widget.addItem(message_label)  

        if np.any((frequency_values >= 800) & (frequency_values <= 975) & (amplitude_values > threshold_max)):
            frequency_range_mask=(frequency_values >= 800) & (frequency_values <= 975)
            amplitude_within_range = np.max(amplitude_values[frequency_range_mask])
            # Display message if RFI signal is detected
            message_label = pg.TextItem(text=' RFI', color=(255, 0, 0))
            message_label.setPos(890, max(amplitude_values))  # Position the message at (800, threshold_mean)
            self.plot_widget.addItem(message_label)  # Add the message label to the plot
            new_data=["mobile",amplitude_within_range]
            if(len(self.data)<13):
                self.data.insert(0, new_data)
            else:
                self.data.pop()
                self.data.insert(0, new_data)

            self.populate_table()
               
        

        if np.any((frequency_values >= 750) & (frequency_values <= 800) & (amplitude_values > threshold_max)):
            frequency_range_mask=(frequency_values >= 750) & (frequency_values <= 800)
            amplitude_within_range = np.max(amplitude_values[frequency_range_mask])
            # Display message if RFI signal is detected
            message_label = pg.TextItem(text='RFI', color=(255, 0, 0))
            message_label.setPos(775, max(amplitude_values))  # Position the message at (800, threshold_mean)
            self.plot_widget.addItem(message_label)  # Add the message label to the plot
            new2=["RF",amplitude_within_range]
            if(len(self.data)<13):
                self.data.insert(0, new2)
            else:
                self.data.pop()
                self.data.insert(0, new2)

            self.populate_table()

        
        region1 = pg.LinearRegionItem(values=[-80, -10], orientation=pg.LinearRegionItem.Vertical)
        region1.setRegion([108, 137])  
        region1.setBrush((255, 255, 0, 50))  
        region1.setZValue(-10)
        self.plot_widget.addItem(region1)
        
        
        region2 = pg.LinearRegionItem(values=[-80, -10], orientation=pg.LinearRegionItem.Vertical)
        region2.setRegion([158, 165])  
        region2.setBrush((255, 255, 0, 50))  
        region2.setZValue(-10)
        self.plot_widget.addItem(region2)

        
        region3 = pg.LinearRegionItem(values=[-80, -10], orientation=pg.LinearRegionItem.Vertical)
        region3.setRegion([174, 230])  
        region3.setBrush((255, 255, 0, 50))  
        region3.setZValue(-10)
        self.plot_widget.addItem(region3)

        
        region3 = pg.LinearRegionItem(values=[-80, -10], orientation=pg.LinearRegionItem.Vertical)
        region3.setRegion([225, 400])  
        region3.setBrush((255, 255, 22, 50)) 
        region3.setZValue(-10)
        self.plot_widget.addItem(region3)

        region3 = pg.LinearRegionItem(values=[-80, -10], orientation=pg.LinearRegionItem.Vertical)
        region3.setRegion([240, 270])  
        region3.setBrush((255, 255, 22, 50)) 
        region3.setZValue(-10)
        self.plot_widget.addItem(region3)

        
        region4 = pg.LinearRegionItem(values=[-80, -10], orientation=pg.LinearRegionItem.Vertical)
        region4.setRegion([290, 320])  
        region4.setBrush((255, 255, 30, 50)) 
        region4.setZValue(-10)
        self.plot_widget.addItem(region4)

        
        region5 = pg.LinearRegionItem(values=[-80, -10], orientation=pg.LinearRegionItem.Vertical)
        region5.setRegion([471, 860])  
        region5.setBrush((255, 255, 40, 50)) 
        region5.setZValue(-10)
        self.plot_widget.addItem(region5)
       
       
        region6 = pg.LinearRegionItem(values=[-80, -10], orientation=pg.LinearRegionItem.Vertical)
        region6.setRegion([824, 889])  
        region6.setBrush((255, 165, 0, 50))  
        region6.setZValue(-10)
        self.plot_widget.addItem(region6)


        region7 = pg.LinearRegionItem(values=[-80, -10], orientation=pg.LinearRegionItem.Vertical)
        region7.setRegion([890, 960])  
        region7.setBrush((0, 255, 255, 50))  
        region7.setZValue(-10)
        self.plot_widget.addItem(region7)

        
        region8 = pg.LinearRegionItem(values=[-80, -10], orientation=pg.LinearRegionItem.Vertical)
        region8.setRegion([767, 787])  
        region8.setBrush((0, 255, 225, 60))  
        region8.setZValue(-10)
        self.plot_widget.addItem(region8)

        region9 = pg.LinearRegionItem(values=[-80, -10], orientation=pg.LinearRegionItem.Vertical)
        region9.setRegion([962, 1213])  
        region9.setBrush((0, 255, 25, 65))  
        region9.setZValue(-10)
        self.plot_widget.addItem(region9)

        region10 = pg.LinearRegionItem(values=[-80, -10], orientation=pg.LinearRegionItem.Vertical)
        region10.setRegion([1250, 1350])  
        region10.setBrush((0, 55, 255, 70))  
        region10.setZValue(-10)
        self.plot_widget.addItem(region10)

        region11 = pg.LinearRegionItem(values=[-80, -10], orientation=pg.LinearRegionItem.Vertical)
        region11.setRegion([1164,1300])  
        region11.setBrush((0, 25, 255, 20))  
        region11.setZValue(-10)
        self.plot_widget.addItem(region11)
        
        message_label = pg.TextItem(text='Mobile', color=(255, 0, 0))
        message_label.setPos(850, -10)  
        self.plot_widget.addItem(message_label) 
        
        message_label2 = pg.TextItem(text='Mobile', color=(255, 0, 0))
        message_label2.setPos(920, -10)  
        self.plot_widget.addItem(message_label2) 

        message_label3 = pg.TextItem(text='Civil Aviation', color=(255, 0, 0))
        message_label3.setPos(117, -10)  
        self.plot_widget.addItem(message_label3)
 
        message_label4 = pg.TextItem(text='Police', color=(255, 0, 0))
        message_label4.setPos(161, -10)  
        self.plot_widget.addItem(message_label4) 

        message_label5 = pg.TextItem(text='TV', color=(255, 0, 0))
        message_label5.setPos(200, -10)  
        self.plot_widget.addItem(message_label5) 

        message_label6 = pg.TextItem(text='Air Navigation, Fixed Mobile', color=(255, 0, 0))   #region[225,400]
        message_label6.setPos(330, -10)  
        self.plot_widget.addItem(message_label6) 

        # message_label7 = pg.TextItem(text='Millitary DN', color=(255, 0, 0))
        # message_label7.setPos(265, -10)  
        # self.plot_widget.addItem(message_label7) 

        message_label7 = pg.TextItem(text='Millitary', color=(255, 0, 0))
        message_label7.setPos(300, -10)  
        self.plot_widget.addItem(message_label7) 

        message_label8 = pg.TextItem(text='Millitary', color=(255, 0, 0))
        message_label8.setPos(255, -10)  
        self.plot_widget.addItem(message_label8) 

        message_label9 = pg.TextItem(text='TV', color=(255, 0, 0))
        message_label9.setPos(600, -10)  
        self.plot_widget.addItem(message_label9) 

        message_label10 = pg.TextItem(text='Surveillence', color=(255, 0, 0))      #Region([1250, 1350])
        message_label10.setPos(1300, -10)  
        self.plot_widget.addItem(message_label10)

        message_label11 = pg.TextItem(text='DMA', color=(255, 0, 0))     #Region([962, 1213])
        message_label11.setPos(1100, -10)  
        self.plot_widget.addItem(message_label11)

        message_label12 = pg.TextItem(text='GNSS-GPS', color=(255, 0, 0))     #Region([1164, 1300])
        message_label12.setPos(1210, -10)  
        self.plot_widget.addItem(message_label12)                                                          


        if self.legend_item is not None:
            self.plot_widget.removeItem(self.legend_item)

        self.legend_item = self.plot_widget.addLegend()
        before_mitigation_curve.setPen('r')
        # after_mitigation_curve.setPen('g')
        self.plot_widget.addItem(before_mitigation_curve, name=f'{legend}', pen='r')
        # self.plot_widget.addItem(after_mitigation_curve, name=f'{legend}: After mitigation', pen='g')

        # Start the timer with a 1-second interval
        self.timer.start(1000)

    def next_plot(self):
        # Stop the timer to prevent repeated plotting
        self.timer.stop()

    def select_band(self, band):
        # Placeholder function to handle band selection
        self.selected_band = band
        print(f'Selected Band {band}')

    def update_graph(self):
        # Read start and end frequencies from input fields
        start_freq_text = self.start_freq_input.text()
        end_freq_text = self.end_freq_input.text()

        # Check if start and end frequencies are valid numbers
        try:
            start_freq = float(start_freq_text)
            end_freq = float(end_freq_text)
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid frequency input. Please enter valid numbers.")
            return

        # Check if start frequency is within the range
        if start_freq < df.iloc[0, 3] / 1000000 or start_freq > df.iloc[0, 4] / 1000000:
            QMessageBox.warning(self, "Error", f"Start frequency must be within {df.iloc[0, 3] / 1000000} MHz and {df.iloc[0, 4] / 1000000} MHz.")
            return

        # Check if end frequency is within the range
        if end_freq < df.iloc[0, 3] / 1000000 or end_freq > df.iloc[0, 4] / 1000000:
            QMessageBox.warning(self, "Error", f"End frequency must be within {df.iloc[0, 3] / 1000000} MHz and {df.iloc[0, 4] / 1000000} MHz.")
            return

        # Filter frequency values within the specified range
        mask = (self.frequency_values >= start_freq) & (self.frequency_values <= end_freq)
        filtered_frequency_values = self.frequency_values[mask]
        filtered_amplitude_values = self.amplitude_values[mask]
        filtered_clean_amplitudes = self.clean_amplitudes[mask]

        # Update the plot with the filtered data
        legend = df.iloc[0, 2]  # Get legend value for current row
        self.plot_data(filtered_amplitude_values, filtered_clean_amplitudes, filtered_frequency_values, legend)

        # Set y-axis range based on the filtered data
        min_value = min(np.min(filtered_amplitude_values), np.min(filtered_clean_amplitudes))
        max_value = max(np.max(filtered_amplitude_values), np.max(filtered_clean_amplitudes))
        self.plot_widget.setYRange(min_value, max_value)
   
        min_freq = np.min(filtered_frequency_values)
        max_freq = np.max(filtered_frequency_values)
        # Set x-axis range to focus on the specified frequency range
        self.plot_widget.plotItem.vb.setLimits(xMin=min_freq, xMax=max_freq)

    def std_around_median(self,row):
        median_value = np.median(row)
        abs_deviations = np.abs(row - median_value)**2
        a=np.mean(abs_deviations)
        return math.sqrt(a)

    def first(self,amplitudes):
        return amplitudes[0:]

    def mitigate_rfi(self,amplitudes):
        warnings.filterwarnings("ignore")

    # Convert amplitudes to float type if they are not already
        amplitudes = np.asarray(amplitudes, dtype=np.float64)

    # Filter out NaN and infinite values
        valid_indices = np.logical_and(~np.isnan(amplitudes), ~np.isinf(amplitudes))
        amplitudes = amplitudes[valid_indices]

        if len(amplitudes) == 0:
            return np.zeros_like(amplitudes)  # Return zeros if all values are invalid

        clean_amplitudes = amplitudes.copy()

    # Calculate the number of points to consider for median and std
        num_points = min(100, len(amplitudes))
        num_points2 = min(200, len(amplitudes))
        self.f_values=[]
        k=[]
        continuous_rfi = False
        for index in range(len(amplitudes)):
        # Consider previous 100 points if available, otherwise all points
            start_index = max(0, index - num_points)
            start_index2 = max(0, index - num_points2)
            end_index = index
        # Calculate median and standard deviation for the previous 20 points or all points
            std_amplitude =  rfi_app.std_around_median(amplitudes[start_index:end_index])
            med_amplitude = np.median(amplitudes[start_index:end_index])

        # Check if standard deviation is zero or NaN
            if np.isnan(std_amplitude) or std_amplitude == 0:
                threshold1 = med_amplitude  # Set threshold to median if std is zero or NaN
            else:
                threshold1 = med_amplitude + (std_amplitude)

            frequency_values=rfi_app.frequency_values[index]

            if amplitudes[index] > threshold1:
            # Calculate the median amplitude, ignoring NaN values
                
                
                median_amplitude = np.nanmedian(amplitudes[start_index:end_index])
                standard_amplitude=rfi_app.std_around_median(amplitudes[start_index:end_index])
                # message_label = pg.TextItem(text='RFI', color=(255, 0, 0))
                # message_label.setPos(frequency_values, np.max(amplitudes))  
                # self.plot_widget.addItem(message_label)
                clean_amplitudes[index] = median_amplitude+(standard_amplitude)
                # k.append(frequency_values)
            median_amplitude2 = np.nanmedian(amplitudes[start_index2:end_index])
            standard_amplitude2=rfi_app.std_around_median(amplitudes[start_index2:end_index])
            threshold2=median_amplitude2+standard_amplitude2
            if(amplitudes[index]>threshold2+2):
                k.append(frequency_values)


            else:
                if k:
                  mid=len(k)//2
                  self.f_values.append(k[mid])
                  k=[]
                pass

        return clean_amplitudes

    
    def add(self,t):
        if t:
                mid=len(t)//2
                self.f_values.append(t[mid])
                t=[]

if __name__ == '__main__':
    app = QApplication([])
    rfi_app = RFIApp()
    dataset_dir ="./data"
    # # List all files in the directory
    # dataset_files = sorted(os.listdir(dataset_dir), key=lambda f: os.path.getmtime(os.path.join(dataset_dir, f)))
    
    # List all files in the directory
    dataset_files = os.listdir(dataset_dir)
    for file_name in dataset_files:
      file_path = os.path.join(dataset_dir, file_name)
    #   # List all files in the directory
    #   dataset_files = sorted(os.listdir(dataset_dir), key=lambda f: os.path.getmtime(os.path.join(dataset_dir, f)))

      if os.path.isfile(file_path):
        # file_name = dataset_files[-1]  # Select the most recent file
        # file_path = os.path.join(dataset_dir, file_name)

        # # Check if it's a file (not a directory)
        # if os.path.isfile(file_path):
            # Read data from text file
            df = pd.read_csv(file_path, delimiter='\t', header=None)

            # Extract amplitude values from each row starting from the 11th column
            amplitude_df = df.iloc[:,12:]

            # Iterate through rows and perform RFI mitigation
            for index, row in amplitude_df.iterrows():
                rfi_app.amplitude_values = row.iloc[:].values
                # print(len( rfi_app.amplitude_values))
                rfi_app.frequency_values = np.linspace(df.iloc[index,3]/1000000, df.iloc[index,4]/1000000, len(rfi_app.amplitude_values))
                if index >= 60:
                # Calculate the difference in dB between the current row and the row 60 indices before it
                    current_amplitudes = row.iloc[:]  
                    past_amplitudes = df.iloc[index - 60, 12:]  # Amplitude values from the row 60 indices before
        
                 # Calculate the difference in dB
                    amplitude_difference = (current_amplitudes - past_amplitudes).abs()
                    t=[]
                # Check if any difference exceeds 2 dB
                    if not amplitude_difference.empty and 0 in amplitude_difference.index:
                      for j in range (0,len(amplitude_difference)):

                        if(amplitude_difference[j]>6):
                            t.append(rfi_app.frequency_values[j])
                        else:
                            rfi_app.add(t)
                        

                # rfi_app.amplitude_values = row.iloc[12:].values

                # Perform RFI mitigation on the set of amplitude values
                rfi_app.clean_amplitudes = rfi_app.mitigate_rfi(rfi_app.amplitude_values)

                # Plot data inside the GUI with a delay of 1 second
                legend = df.iloc[index, 2]  # Get legend value for current row
                rfi_app.plot_data(rfi_app.amplitude_values, rfi_app.clean_amplitudes, rfi_app.frequency_values, legend)

                # Show the updated plot
                app.processEvents()  # Process GUI events to update the plot
                time.sleep(1)  # Introduce a delay of 1 second

      sys.exit(app.exec_())
