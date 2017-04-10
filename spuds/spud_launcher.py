

class Potatoes:

    @property
    def all(self):
        with open('/config/potatoes/all', 'r') as f:
            data = []
            for line in f.readlines():
                data.append(line.replace('\n',''))
            return data
