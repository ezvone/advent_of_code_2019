from itertools import groupby


def test_criteria1(n):
    s = str(n)
    if not any(ch1==ch2 for ch1, ch2 in zip(s, s[1:])):
        return False
    if any(ch1>ch2 for ch1, ch2 in zip(s, s[1:])):
        return False
    return True

def test_criteria2(n):
    s = str(n)
    groupsizes = (len(list(it)) for ch, it in groupby(s))
    if 2 not in groupsizes:
        return False
    if any(ch1>ch2 for ch1, ch2 in zip(s, s[1:])):
        return False
    return True


def find_matching(begin, end, test_criteria):
    return (n for n in range(begin, end+1) if test_criteria(n))


def puzzle1():
    return sum(1 for n in find_matching(136818, 685979, test_criteria1))


def puzzle2():
    return sum(1 for n in find_matching(136818, 685979, test_criteria2))


if __name__ == "__main__":
    assert puzzle1() == 1919
    assert puzzle2() == 1291
    print('OK.')


