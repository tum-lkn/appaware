import redis


def pace():
    pass


def unpace():
    pass


def run():
    pacing = False
    promt = "Press ENTER to {}"
    try:
        while True:
            if pacing:
                input(promt.format("unpace"))
                unpace()
            else:
                input(promt.format("pace"))
                pace()
            pacing = not pacing
    except KeyboardInterrupt:
        print("\nStopping pacer")


if __name__ == "__main__":
    run()
