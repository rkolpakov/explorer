import json, argparse, sys
from web3 import Web3
from eth_event import get_topic_map, decode_log

parser = argparse.ArgumentParser()

parser.add_argument("-from_block")
parser.add_argument("-to_block")
parser.add_argument("-address")

web3 = Web3(
    Web3.HTTPProvider(
        "https://astar-mainnet.g.alchemy.com/v2/cBLjNhHbZW28m7ux7aKtcQCb6-QK7Cgr",
        request_kwargs={"timeout": 600},
    ) 
)


def decode_event_list(events, topic_map, specific_address):
    results = []
    for event in events:
        (address, value, block) = decode_event(event, topic_map)
        if specific_address and specific_address != address:
            continue
        results.append({"address": address, "value": value, block: "block"})
    return results


def decode_event(event, topic_map):
    decoded_event = decode_log(event, topic_map)
    [address_dict, value_dict] = decoded_event["data"][:2]
    return (address_dict["value"], value_dict["value"], event.blockNumber)


def create_filter(address, topics, fromBlock=1, toBlock="latest"):
    return web3.eth.filter(
        {
            "fromBlock": fromBlock,
            "toBlock": toBlock,
            "address": address,
            "topics": topics,
        }
    )


def main():
    args = parser.parse_args()

    with open("./algem_staking_abi.json", "r") as file:
        data = file.read()
        abi = json.loads(data)

    topic_map = get_topic_map(abi)
    contract_address = Web3.toChecksumAddress("0x70d264472327b67898c919809a9dc4759b6c0f27")

    stake_filter = create_filter(
        address=contract_address,
        topics=[Web3.keccak(text="Staked(address,uint256)").hex()],
        toBlock=args.to_block,
        fromBlock=args.from_block,
    )
    unstake_filter = create_filter(
        address=contract_address,
        topics=[Web3.keccak(text="Unstaked(address,uint256,bool)").hex()],
        toBlock=args.to_block,
        fromBlock=args.from_block,
    )

    staking_events = web3.eth.get_filter_logs(stake_filter.filter_id)
    unstaking_events = web3.eth.get_filter_logs(unstake_filter.filter_id)

    staking_results = decode_event_list(staking_events, topic_map, specific_address=args.address)
    unstaking_results = decode_event_list(
        unstaking_events, topic_map, specific_address=args.address
    )

    sys.stdout.write(json.dumps(staking_results))
    sys.stdout.write(json.dumps(unstaking_results))


main()
