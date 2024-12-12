# GetOutGetCoffee

Most elderly people o those that struggle with mental health often end up staying too much time at home, and they forget to socialize. Which worsens their condition.
Our proyect aims to monitor how many times they go outside. If they stay at home for too long it will send them reminders to go outside.
We will do this using a raspberry pi with some sensors:
1: Motion sensor: it will detect movement from the front door to detect when someone goes outside.
2: Humidity and temperature sensor: The reminder to get out will come with a recomendation about something to do according to the weather.
3: Screen: It will show the temperature and humidity, and the background color will depend on them.

To send data we used a laptop as an mqtt broker. The raspi would send when movement was detected and when the laptop received it it would be saved on mysql. We also had a script to create a graph of the times they've gone outside, and it would update when mysql table was updated to achieve a real time graph.
We used this mqtt line to start it:
mosquitto -c "C:\Program Files\mosquitto\mosquitto.conf" -v

Scripts:
1:mqtt1.py : It's the one running on the raspy. It's in charge of the sensors functionality. It also gives the recomendations and sends the data to the broker.
2:mqtt_to_mysql.py : when mqtt receives data this script stores it on mysql.
3:grafico.py : It generated the graph. When closed it saves the last one on a folder.


For more information about the future of the proyect read the pdf.

Thank you!
