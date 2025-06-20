# 💰 CashFlow Pro – ATM Cash Depletion Predictor

CashFlow Pro is an AI-powered web application that predicts ATM cash depletion risk based on historical usage patterns. Designed for banks and cash logistics teams to optimize replenishment cycles and reduce ATM downtime.

![image](https://github.com/user-attachments/assets/1b2d823f-910f-4b0d-9710-1580e1618f72),![image](https://github.com/user-attachments/assets/fb230e29-cc60-4779-82cf-56fabfb61375)
![image](https://github.com/user-attachments/assets/f828b30e-1051-42aa-b1f6-d0db2320c045),![image](https://github.com/user-attachments/assets/7f463e17-e08c-46fe-9334-90495ae57f81)

---

## 🚀 Features

- 🔮 Predicts cash that will be dispensed from an ATM based on transactions and day of the week
- 📈 Provides alerts if the ATM is likely to run out of cash
- 🧠 Trained using a `RandomForestRegressor` on historical ATM data
- 📊 Analytics dashboard (top risky ATMs, timeline trends, total cash loaded, busiest ATM)
- 🧾 View and export prediction history
- 🗃️ MySQL backend for storing predictions
- 💡 Modern responsive UI using Flask + Chart.js

---

## 🛠️ Project Structure

```

atm-prediction-main/
├── app.py                # Main Flask app
├── train\_model.py        # Model training script
├── model.pkl             # Trained regression model
├── atm\_data.csv          # Dataset for training
├── requirements.txt      # Python dependencies
├── atm\_predictions.sql   # SQL schema (optional import)
├── templates/
│   ├── index.html        # Main form + prediction history
│   └── analytics.html    # Analytics dashboard
└── static/               # (Optional - CSS/JS/assets)

````

---

## 🧑‍💻 Installation & Setup

### ✅ Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/atm-prediction-main.git
cd atm-prediction-main
````

### ✅ Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

> If you get a `No module named 'mysql'` or `sklearn`, make sure all packages are installed.

### ✅ Step 3: Setup MySQL Database

#### Option A: Auto-Creation via Flask

Make sure MySQL is running (e.g., via XAMPP) and then simply run:

```bash
python app.py
```

The app will auto-create:

* Database: `atm_predictions`
* Table: `prediction_history`

#### Option B: Manual Setup via phpMyAdmin

1. Open [http://localhost/phpmyadmin](http://localhost/phpmyadmin)
2. Click **New** → Create database `atm_predictions`
3. Import `atm_predictions.sql` file or run the SQL code inside it

---

### ✅ Step 4: Train the Model (Optional)

To retrain the model using `atm_data.csv`:

```bash
python train_model.py
```

This creates `model.pkl` for prediction use.

---

### ✅ Step 5: Run the App

```bash
python app.py
```

Then open your browser:

```
http://127.0.0.1:5000/
```

---

## 📊 Screenshots

<img src="screenshots/dashboard.png" width="600">
<img src="screenshots/analytics.png" width="600">

---

## 📦 Requirements

* Python 3.8+
* MySQL Server (XAMPP or standalone)
* Flask
* Pandas, Scikit-learn, Joblib
* mysql-connector-python

Install with:

```bash
pip install -r requirements.txt
```

---

## 📌 Environment Variables (Optional)

If using `.env`:

```env
MYSQL_HOST=127.0.0.1
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_PORT=3306
MYSQL_DATABASE=atm_predictions
```

---

## 🧠 Model Details

* **Model**: Random Forest Regressor
* **Target**: `Cash_Dispensed`
* **Features**:

  * `Transactions`
  * Day of Week (one-hot encoded)

---

## 📜 License

MIT License. Free to use for education and experimentation.

---

## 👨‍💻 Author

Developed by [Hamiz Khan]((https://github.com/Hamizkhan08))

````

