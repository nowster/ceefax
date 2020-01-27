def shorten(name: str) -> str:
    if len(name) > 9:
        join = '.'
        if '-' in name:
            name = name.replace('-', ' ')
            join = '-'
        words = name.split()
        w = []
        split = 4
        if len(words) > 1:
            if words[:2] == ['van', 'der']:
                words[:2] = ['vd']
            for word in words[:-1]:
                if word in ["de", "vd"]:
                    w.append(word)
                    split = 6
                else:
                    w.append(f"{word[0]}{join}")
                    split = 5
            w.append(words[-1])
        else:
            w = words
        name = "".join(w)
        if len(name)>9:
            name = f"{name[:split]}'{name[split-8:]}"
    return name
