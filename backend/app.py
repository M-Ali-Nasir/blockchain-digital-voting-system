from flask import Flask, jsonify, request, render_template,session, redirect, url_for, flash
from extensions import db
from models import User
from web3 import Web3
import config, os
from functools import wraps
from config import Config

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(config.Config)  # Load configuration
app.secret_key = os.urandom(24) 
# Initialize SQLAlchemy with the Flask app
db.init_app(app)

with app.app_context():
    db.create_all()
   
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', is_admin=True)
        admin.set_password('zxcvbnm')  
        db.session.add(admin)
        db.session.commit()

# Connect to Ganache
web3 = Web3(Web3.HTTPProvider(config.Config.GANACHE_URL))
contract = web3.eth.contract(address=config.Config.CONTRACT_ADDRESS, abi=config.Config.CONTRACT_ABI)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            flash('Login successful!', 'success')
            return redirect(url_for('admin')) if user.is_admin else redirect(url_for('user'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))




def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')

def admin():
    if 'user_id' not in session or not session.get('is_admin', False):
        return redirect(url_for('login'))
    
    # Pass is_admin to the template
    return render_template('admin.html', is_admin=True)



# Route for the user page
@app.route('/user')
def user():
  return render_template('user.html', is_admin=False)



# Example route to register a candidate
@app.route('/register_candidate', methods=['POST'])
@admin_required
def register_candidate():
    if Config.VOTING_STARTED:
        return jsonify({"error": "Candidate registration is closed."}), 400
    try:
        candidate_name = request.json.get('name')
        if not candidate_name:
            return jsonify({"error": "Candidate name is required"}), 400
        
        account = web3.eth.accounts[0]
        tx_hash = contract.functions.registerCandidate(candidate_name).transact({'from': account})
        web3.eth.wait_for_transaction_receipt(tx_hash)
        
        return jsonify({"message": "Candidate registered successfully"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500




@app.route('/delete_candidate', methods=['DELETE'])
@admin_required
def delete_candidate():

    if Config.VOTING_STARTED:
        return jsonify({"error": "Candidate registration is closed."}), 400
    
    try:
        candidate_id = request.json.get('candidateId')
        if candidate_id is None:
            return jsonify({"error": "Candidate ID is required"}), 400

        # Assuming you're using web3 to interact with Solidity contract
        admin_address = web3.eth.accounts[0]
        tx_hash = contract.functions.deleteCandidate(candidate_id).transact({'from': admin_address})
        web3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({"message": "Candidate deleted successfully"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500




# Route to cast a vote for a candidate
@app.route('/vote', methods=['POST'])
def vote():

    if not Config.VOTING_STARTED or Config.VOTING_ENDED:
        return jsonify({"error": "Voting is not currently active."}), 400
    try:
        candidate_id = request.json.get('candidateId')
        voter_address = request.json.get('voterAddress')
        
        if not candidate_id or not voter_address:
            return jsonify({"error": "Candidate ID and voter address are required"}), 400
        
        voter_address = Web3.to_checksum_address(voter_address)

        tx_hash = contract.functions.vote(candidate_id).transact({'from': voter_address})
        web3.eth.wait_for_transaction_receipt(tx_hash)
        
        return jsonify({"message": "Vote cast successfully"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# Route to get the total number of candidates
@app.route('/candidate_count', methods=['GET'])
def candidate_count():
    try:
        count = contract.functions.candidateCount().call()
        is_admin=False
        if 'user_id' not in session or not session.get('is_admin', False):
            is_admin=False
        else:
            is_admin=True
        return jsonify({"candidateCount": count, "is_admin":is_admin}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# Route to get candidate details by ID
@app.route('/candidate/<int:candidate_id>', methods=['GET'])
def get_candidate(candidate_id):
    try:
        candidate = contract.functions.candidates(candidate_id).call()
        candidate_data = {
            "id": candidate_id,
            "name": candidate[1],
            "voteCount": candidate[2]
        }
        return jsonify(candidate_data), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# Route to get specific candidate information
@app.route('/get_candidate/<int:candidate_id>', methods=['GET'])
def get_specific_candidate(candidate_id):
    try:
        candidate = contract.functions.getCandidate(candidate_id).call()
        candidate_data = {
            "name": candidate[0],
            "voteCount": candidate[1]
        }
        return jsonify(candidate_data), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# Route to check if an address has voted
@app.route('/has_voted/<string:voter_address>', methods=['GET'])
def has_voted(voter_address):
    try:
        has_voted = contract.functions.voters(voter_address).call()
        return jsonify({"hasVoted": has_voted}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    

@app.route('/start_voting', methods=['POST'])
def start_voting():
    candidate_count = contract.functions.candidateCount().call()
    if candidate_count < 2:
        return jsonify({"error": "At least 2 candidates are required to start voting."}), 400

    Config.VOTING_STARTED = True
    Config.VOTING_ENDED = False
    return jsonify({"message": "Voting started successfully."})

@app.route('/stop_voting', methods=['POST'])
def stop_voting():
    if not Config.VOTING_STARTED:
        return jsonify({"error": "Voting has not started yet."}), 400

    Config.VOTING_STARTED = False
    Config.VOTING_ENDED = True
    return jsonify({"message": "Voting stopped successfully."})

@app.route('/voting_status', methods=['GET'])
def voting_status():
    return jsonify({
        "voting_started": Config.VOTING_STARTED,
        "voting_ended": Config.VOTING_ENDED
    })

# Initialize the database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
