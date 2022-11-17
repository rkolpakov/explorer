import json, sys
from web3 import Web3
from utils import get_client, create_filters, printProgressBar
from eth_event import get_topic_map, decode_log

contract_creation_block = 1002487
contract_to_check_list = [
    Web3.toChecksumAddress("0xa6B71E26C5e0845f74c812102Ca7114b6a896AB2"),
    Web3.toChecksumAddress("0xA602D021DA61eC4CC44dedBD4e3090A05c97A435"),
    Web3.toChecksumAddress("0xa5efb5bF75BbB607DC243707A83F2AF5ED4E9813"),
    Web3.toChecksumAddress("0xE915D2393a08a00c5A463053edD31bAe2199b9e7"),
    Web3.toChecksumAddress("0x70d264472327B67898c919809A9dc4759B6c0f27"),
    Web3.toChecksumAddress("0x03065E84748a9e4a1AEbef15AC89da1Cdf18B202"),
    Web3.toChecksumAddress("0x733ebcC6DF85f8266349DEFD0980f8Ced9B45f35"),
    Web3.toChecksumAddress("0x992bad137Fc8a50a486B5C6375f581964b4A15FC"),
    Web3.toChecksumAddress("0x7BAe21fB8408D534aDfeFcB46371c3576a1D5717"),
    Web3.toChecksumAddress("0x8489f4554790F5A103F2B0398537eAEe68B73884"),
    Web3.toChecksumAddress("0x9448610696659de8F72e1831d392214aE1ca4838"),
    Web3.toChecksumAddress("0x95f506E72777efCB3C54878bB4160b00Cd11cd84"),
    Web3.toChecksumAddress("0xc4335B1b76fA6d52877b3046ECA68F6E708a27dd"),
    Web3.toChecksumAddress("0xd59fC6Bfd9732AB19b03664a45dC29B8421BDA9a"),
    Web3.toChecksumAddress("0x8b5d62f396Ca3C6cF19803234685e693733f9779"),
    Web3.toChecksumAddress("0x48f292E9FDce07bA34217b0AA62E08B62376df3e"),
    Web3.toChecksumAddress("0x1de7c3A07918fb4BE9159703e73D6e0b0736CaBC"),
    Web3.toChecksumAddress("0x101b453a02f961b4e3f0526ecd4c533c3a80d795"),
    Web3.toChecksumAddress("0xAbF7230E022C9146DF9B4dBeD97e73CF61D612B8"),
    Web3.toChecksumAddress("0x431D5dfF03120AFA4bDf332c61A6e1766eF37BDB"),
    Web3.toChecksumAddress("0x7b2152E51130439374672AF463b735a59a47ea85"),
    Web3.toChecksumAddress("0xA0e232D596d6838d39DdDE9b63916B42246BE15e"),
    Web3.toChecksumAddress("0x190dA1B9fA124BD872e9166bA3c7Dd656A11E8F8"),
]


def main():
    with open("./dapp_staking_abi.json", "r") as file:
        data = file.read()
        abi = json.loads(data)

    web3 = get_client()

    latest_block = web3.eth.block_number
    contract_address = Web3.toChecksumAddress("0x8E2fa5A4D4e4f0581B69aF2f8F2Ef2CF205aE8F0")
    dapp_contract = web3.eth.contract(address=contract_address, abi=abi)
    topic_map = get_topic_map(abi)

    filter_list = create_filters(
        address=contract_address,
        topics=[Web3.keccak(text="AstarBaseRegistered(address)").hex()],
        fromBlock=contract_creation_block,
        toBlock=latest_block,
    )

    registered_addresses = []

    for (index, filter) in enumerate(filter_list):
        printProgressBar(
            index, len(filter_list), prefix="Retrieving progress:", suffix="Complete", length=50
        )
        try:
            [decoded_event] = [
                decode_log(event, topic_map) for event in web3.eth.get_filter_logs(filter.filter_id)
            ]
            registered_addresses.append(Web3.toChecksumAddress(decoded_event["data"][0]["value"]))
        except:
            print("Error processing:", filter.filter_id)

    stakers = {}

    for (index, registered_address) in enumerate(registered_addresses):
        printProgressBar(
            index,
            len(registered_addresses),
            prefix="Checking progress:",
            suffix="Complete",
            length=50,
        )

        stakers[registered_address] = {}
        for contract_address_to_check in contract_to_check_list:
            stake_value = dapp_contract.functions.checkStakerStatusOnContract(
                registered_address, contract_address_to_check
            ).call()
            if stake_value > 0:
                stakers[registered_address][contract_address_to_check] = stake_value

        if stakers[registered_address] == {}:
            del stakers[registered_address]

    sys.stdout.write(json.dumps(stakers))


main()
