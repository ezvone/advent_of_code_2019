from input_reader import read_nanofactory_specs


def calculate_required_ore(required_fuel):
    required = {'FUEL': required_fuel}
    surplus =   {}

    requirements = {out_name: (out_amount, inputs)
        for inputs, (out_amount, out_name) in read_nanofactory_specs('day14input.txt')}

    while list(required) != ['ORE']:
        chemical = list(set(required) - {'ORE'})[0]
        quantity = required[chemical]
        quantity -= surplus.get(chemical, 0)
        if quantity < 0:
            surplus[chemical] = -quantity
            quantity = 0
        else:
            surplus[chemical] = 0
        if quantity > 0:
            produced_quantity, inputs = requirements[chemical]
            num_reactions = (quantity - 1) // produced_quantity + 1

            for amount, name in inputs:
                required[name] = required.get(name, 0) + amount * num_reactions

            surplus[chemical] += produced_quantity * num_reactions - quantity
        del required[chemical]

    return required['ORE']


def puzzle1():
    return calculate_required_ore(1)


def puzzle2():
    available_ore = 1000000000000
    low = 1
    ore_for_one = calculate_required_ore(1)
    low = available_ore // ore_for_one
    assert calculate_required_ore(low) <= available_ore
    n = 10 * low
    while calculate_required_ore(n) <= available_ore:
        low = n
        n *= 10
    high = n
    while high - low > 1:
        n = (low + high) // 2
        if calculate_required_ore(n) <= available_ore:
            low = n
        else:
            high = n
    return low


if __name__ == "__main__":
    assert puzzle1() == 2556890
    assert puzzle2() == 1120408
    print('OK.')
