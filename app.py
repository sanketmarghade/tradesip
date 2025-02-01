from flask import Flask, render_template, request, redirect, url_for, session
from tradingview_ta import TA_Handler, Interval

# Define interval options
INTERVAL_OPTIONS = {
    "1 Minute": Interval.INTERVAL_1_MINUTE,
    "5 Minutes": Interval.INTERVAL_5_MINUTES,
    "15 Minutes": Interval.INTERVAL_15_MINUTES,
    "30 Minutes": Interval.INTERVAL_30_MINUTES,
    "1 Hour": Interval.INTERVAL_1_HOUR,
    "2 Hours": Interval.INTERVAL_2_HOURS,
    "4 Hours": Interval.INTERVAL_4_HOURS,
    "1 Day": Interval.INTERVAL_1_DAY,
    "1 Week": Interval.INTERVAL_1_WEEK,
    "1 Month": Interval.INTERVAL_1_MONTH
}

# Create Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

@app.route('/', methods=['GET', 'POST'])
def home():
    analysis_result = None
    error_message = None

    # Use default settings if none exist in the session
    symbol_input = session.get('symbol', '')
    selected_interval_name = session.get('interval', '1 Hour')
    
    if request.method == 'POST':
        symbol_input = request.form['symbol'].strip().upper()
        selected_interval_name = request.form['interval']

        if not symbol_input:
            error_message = "Error: Trading symbol cannot be empty."
        else:
            selected_interval = INTERVAL_OPTIONS.get(selected_interval_name)

            if not selected_interval:
                error_message = "Error: Invalid interval selected."
            else:
                try:
                    # Set up the TA handler
                    handler = TA_Handler(
                        symbol=symbol_input,
                        screener="india",
                        exchange="NSE",
                        interval=selected_interval
                    )

                    analysis = handler.get_analysis()
                    analysis_result = {
                        "summary": analysis.summary,
                        "indicators": analysis.indicators
                    }

                    # Store symbol and interval in session for next visit
                    session['symbol'] = symbol_input
                    session['interval'] = selected_interval_name

                except Exception as e:
                    error_message = f"An error occurred: {str(e)}"

    return render_template('index.html', 
                           analysis_result=analysis_result,
                           error_message=error_message,
                           intervals=INTERVAL_OPTIONS.keys(),
                           symbol=symbol_input,
                           selected_interval=selected_interval_name)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    # Default settings to be displayed in the settings form
    current_symbol = session.get('symbol', '')
    current_interval = session.get('interval', '1 Hour')

    if request.method == 'POST':
        # Get the user input from the form
        new_symbol = request.form['default_symbol'].strip().upper()
        new_interval = request.form['default_interval']

        # Save the settings in the session
        session['symbol'] = new_symbol
        session['interval'] = new_interval

        return redirect(url_for('home'))

    return render_template('settings.html', 
                           current_symbol=current_symbol, 
                           current_interval=current_interval,
                           intervals=INTERVAL_OPTIONS.keys())

if __name__ == '__main__':
    app.run(debug=True, port=80)
    
