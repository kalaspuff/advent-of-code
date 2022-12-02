from values import values


async def run():
    result = 0

    mapping = {
        "A": 1,
        "B": 2,
        "C": 3,
        "X": 1,
        "Y": 2,
        "Z": 3,
    }
    res_mapping = {
        "win": 6,
        "draw": 3,
        "loss": 0,
    }

    for row in values.rows:
        they, me = row.split(" ")

        game_result = ""
        if mapping[they] == mapping[me]:
            game_result = "draw"
        elif any([
            they == "A" and me == "Y",
            they == "B" and me == "Z",
            they == "C" and me == "X",
        ]):
            game_result = "win"
        else:
            game_result = "loss"

        result += mapping[me]
        result += res_mapping[game_result]

    return result


# [values.year]            (number)  2022
# [values.day]             (number)  2
# [values.part]            (number)  1
# [values.input_filename]  (str)     ./year2022/day2/input
#
# Result: 8933
