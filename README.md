# waiteraid-booking-tool
Modern restaurants use waiteraid for bookings. When the restaurant is popular, people book fast. 
This tool automates the booking so you can get a reservation at your favourite restaurant. 

Based on the waiteraid api at 31-10-2021. The key and keyValue for each restaurant is updated every night. 
This means that before running the script you need to update these by opening the developer mode in your browser and looking at the requests that are made when opening the booking page for your desired restaurant.
Copy the key, value hash pair and paste them into your desired restaurant in restaurants.cfg. Also, do not to update the config.cfg with your own booking details.

Requires Python > 3.9 and pprint (pip3 install pprint)
