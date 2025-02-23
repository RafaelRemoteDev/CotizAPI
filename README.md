# CotizAPI 🤖💸🐂

CotizAPI is a Telegram bot designed to provide up-to-date price information on key financial assets such as gold, silver, bitcoin, wheat and oil. This system combines modern technologies to provide an efficient, easy-to-use and fully automated API to query prices, generate alerts and manage historical data.

## **✨ Project Features**

- **📊 Current price query**: Allows to obtain real-time prices of financial assets.
- **🔔 Automatic alerts**: Generates notifications based on significant price changes.
- **📈 Price history**: Stores and allows querying historical prices for comparative analysis.
- **📅 Daily and weekly variation**: Automatically calculates the variation in prices with respect to previous days or weeks.
- **⏰ Automatic scheduling**: Updates asset prices periodically through a task scheduler.
- **🌍 Multi-asset support**: Currently supports gold, silver, bitcoin, wheat and oil, but is easily scalable to include more assets.
- **🚀 Fast REST API**: Designed with FastAPI to provide an efficient and easy-to-integrate interface.

## **🛠️ Technologies used**

The project was built using a set of modern tools that ensure efficiency and ease of deployment:

1. **🌐 Vercel**: For API deployment and hosting, ensuring high availability and performance.
2. **🐙 GitHub**: For version control and code development collaboration.
3. **📬 Postman**: For comprehensive testing of API paths and functionality.
4. **⚡ FastAPI**: Lightweight and fast framework for REST API development.
5. **💾 SQLite + SQLAlchemy**: SQLite as the lightweight database, with SQLAlchemy ORM to manage database operations in a scalable and maintainable way.
6. **🖥️ DBeaver**: Graphical tool to manage and query the SQLite database.
7. **⏲️ Task Scheduler**: Used to automate price updates and alert generation.

## **📋 System architecture**.

CotizAPI uses two main tables in its database:
1. **📁 Price table**: Records asset prices with their corresponding date.
2. **🔔 Alerts table**: Stores alerts generated based on significant price changes.


## **🤝 How CotizAPI works**.

1. **🚀 Price update**:
   - A task scheduler automates the daily update of prices in the database.
   - Asset prices are obtained from external sources and stored in the pricing table.
2. **🔔 Alert generation**:
   - When a significant change in prices is detected, an alert is generated in the corresponding table.
3. **📲 Interaction with Telegram**:
   - Users can interact with the bot to query current prices, historical prices and recent alerts.
4. **📉 Variance analysis**:
   - API calculates daily and weekly percentage variations based on stored data.

## **🚀 How to deploy the project**.

### **Prerequisites**
- Python 3.10+
- SQLite
- Vercel CLI
- Git

### **Installation**
1. Clone the repository:
   ````bash
   git clone https://github.com/RafaelRemoteDev/cotizAPI.git
   cd cotizAPI
   
2. Create and activate a virtual environment

- On Windows:
   ```bash
   python -m venv venv
   venv “scripts” activate

- On macOS/Linux:
   ````bash
   python -m venv venv
   source venv/bin/activate

3. Install dependencies
   ````bash  
   pip install -r requirements.txt

## **📬 Contact**
- **Mail:  _rmartinezomenaca@gmail.com_**

- **GitHub: _RafaelRemoteDev_**