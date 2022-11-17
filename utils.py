from web3 import Web3

web3 = Web3(
    Web3.HTTPProvider(
        "https://astar-mainnet.g.alchemy.com/v2/cBLjNhHbZW28m7ux7aKtcQCb6-QK7Cgr",
        request_kwargs={"timeout": 6000},
    )
)


def get_client():
    return web3


def create_filters(address, topics, fromBlock=1, toBlock="latest"):
    step = 10000
    result = []
    current_block = fromBlock

    while current_block < toBlock:
        to_block_local = current_block + step
        result.append(
            web3.eth.filter(
                {
                    "fromBlock": current_block,
                    "toBlock": toBlock if to_block_local > toBlock else to_block_local,
                    "address": address,
                    "topics": topics,
                }
            )
        )
        current_block += step

    return result


def printProgressBar(
    iteration, total, prefix="", suffix="", decimals=1, length=100, fill="█", printEnd="\r"
):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + "-" * (length - filledLength)
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()
