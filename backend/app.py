from flask import Flask, jsonify, request, render_template
from extensions import db
from models import User, Candidate, VoteLog
from web3 import Web3
import config

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(config.Config)  # Load configuration

# Initialize SQLAlchemy with the Flask app
db.init_app(app)

# Connect to Ganache
web3 = Web3(Web3.HTTPProvider(config.Config.GANACHE_URL))
contract = web3.eth.contract(address=config.Config.CONTRACT_ADDRESS, abi=config.Config.CONTRACT_ABI)


@app.route('/admin')
def admin():
    return render_template('admin.html')

# Route for the user page
@app.route('/user')
def user():
    return render_template('user.html')



# Example route to register a candidate
@app.route('/register_candidate', methods=['POST'])
def register_candidate():
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

# Route to cast a vote for a candidate
@app.route('/vote', methods=['POST'])
def vote():
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
        return jsonify({"candidateCount": count}), 200
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

# Initialize the database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
