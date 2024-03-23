from util.handTracker import HandTracker


def press(d):
    if not d:
        return
    print(d[0][9])

def main():
    ht = HandTracker(press)
    ht.start()
    ht.show_text('test')
if __name__ == '__main__':
    main()