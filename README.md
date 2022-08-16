# roast-server-be
Coffee Roaster Control Server Backend (pairs with roast-server-fe)

This project is designed as a full-stack webapp interface for a coffee roaster - initially supporting the Aillio Bullet R2.

The [frontend](https://github.com/cathos/roast-server-fe/) uses:
  - React
  - SWR
  - Axios
  - React-Chartjs-2
  - Chart.js
  - JavaScript
The frontend is built and run with npm, but yarn should also work. 

The [backend](https://github.com/cathos/roast-server-be) uses: 
  - PyUSB
  - PyTest
  - Flask
  - Flask-CORS
  - Python
The backend will likely be updated soon to use a dedicated WSGI server such as gunicorn instead of the flask runner. It is currently built to run in a python virtual environment by installing the dependencies listed in requirements.txt. It is run with Flask. Update the frontend's reference to the backend address as necessary if running on the same host. 
