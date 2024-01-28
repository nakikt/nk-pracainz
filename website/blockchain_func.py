from flask import Blueprint
from flask_csp.csp import csp_header

from .blockchain import Blockchain
from . import blocks
from flask import jsonify
from .methods import New_blockchains

blockchain_func = Blueprint("blockchain_func", __name__)

@blockchain_func.route("/nodes/sync/<id>", methods=['GET', 'POST'])
@csp_header({'default-src':"'none'",'script-src':"'self'"})

def sync(id):
    updated = blocks[int(id)].update_blockchain(id)
    if updated:
        print( 'The blockchain has been updated to the latest')
        response = str ({'message': 'The blockchain has been updated to the latest', })
    else:
        response = {
            'message': 'There was a problem with block synchronization',

        }
    return response, 200


@blockchain_func.route("/blockchain/<id>", methods=['GET'])
@csp_header({'default-src':"'none'",'script-src':"'self'"})

def full_chain(id):

    response = {
            'chain': blocks[int(id)].chain,
            'length': len(blocks[int(id)].chain),
        }

    return jsonify(response), 200

@blockchain_func.route("/init_syn/<id>",methods = ['GET'])
@csp_header({'default-src':"'none'",'script-src':"'self'"})
def init_sync(id):
    updated= blocks[int(id)].initial_sync(id)
    if updated:
        print(f"The blockchain {id} has been synchronized")
        response = {
            'message':
                'The blockchain has been synchronized',
        }
    else:
        response = {
            'message': 'There was a problem with block synchronization',

        }
    return response, 200


@blockchain_func.route("/addblockchain/<id>",methods = ['GET', 'POST'])
@csp_header({'default-src':"'none'",'script-src':"'self'"})
def addblockchain(id):

    new_blockchain = New_blockchains(f'new_blockchain{id}')
    new_blockchain.name = Blockchain()
    blocks.append(new_blockchain.name)
    blocks[int(id)].add_node("https://127.0.0.1:5000")
    blocks[int(id)].add_node("https://127.0.0.1:5001")
    blocks[int(id)].add_node("http://127.0.0.1:5002")
    blocks[int(id)].add_node("http://127.0.0.1:5003")
    # new = Blockchain()
    # blocks.append(new)
    print(f'Blockchain #{id} has been added')
    add = blocks[int(id)].initial_sync(id)
    if add:
        print(f"The blockchain {id} has been added")
        response = {
            'message':
                'The blockchain has been added',
        }
    else:
        response = {
            'message': 'There was a problem with addition the blockchain',

        }
    return response, 200

