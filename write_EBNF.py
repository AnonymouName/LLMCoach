import json, re


def read_EBNF():
    with open("Specs/China_spec_example_EBNF.txt", "r") as f:
        lines = f.readlines()

    result = []
    line = ''
    for i in lines:
        if i != '\n':
            line += i
        else:
            result.append(line)
            line = ''
    result.append(line)
    return result


def law_key_sort(law_name):
    law_name = law_name.lower()  
    match = re.match(r'law(\d+)(?:_(\d+))?', law_name)
    if match:
        major = int(match.group(1))  
        sub = int(match.group(2)) if match.group(2) else 0
        return (major, sub)
    else:
        return (float('inf'), float('inf'))

def write_example(result):
    with open('Specs/China_spec_example.json', 'r') as f:
        data = json.load(f)
    law_sort = sorted(data.keys(), key = law_key_sort)

    for i, key in enumerate(law_sort):
        if i < len(result):
            data[key]["Result"] = result[i]

    with open('Specs/China_spec_example.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    result = read_EBNF()
    write_example(result)