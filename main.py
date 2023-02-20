import msvcrt

class Screen:
    instance = None

    colors = {
        "black": '\u001b[30m',
        "red": '\u001b[31m',
        "green": '\u001b[32m',
        "yellow": '\u001b[33m',
        "blue": '\u001b[34m',
        "magenta": '\u001b[35m',
        "cyan": '\u001b[36m',
        "white": '\u001b[37m',
        "reset": '\u001b[0m',

    }

    @staticmethod
    def getScreenState():
        if not Screen.instance:
            Screen.instance = Screen()
        return Screen.instance

    @staticmethod
    def getBiggestLine(arrText: list[str]) -> str:
        arrText.sort(key=len, reverse=True)
        return arrText[0]

    @staticmethod
    def boundaryLine(text):
        line = ""
        lines = Screen.getBiggestLine(text.split("\n"))
        for i in range(len(lines)):
            line += "─"
        return line

    @staticmethod
    def boundaryNumber(text):
        num = 0
        for i in range(len(text)):
            num += 1
        return num

    @staticmethod
    def getChar():
        key = msvcrt.getch()
        if '\xe0' or '\x00' == key:
            key = msvcrt.getch()

            match key:
                case b'H':
                    print("Up")
                case b'M':
                    print("Right")
                case b'K':
                    print("Left")
                case b'P':
                    print("Down")
        return key
        

    @staticmethod
    def fprint(string, isArr=False):
        return string.format(**Screen.colors) + "\n"

class Signal:
    def __init__(self, value, label) -> list:
        self.value = value
        self.label = label
        self.topics = {

        }

    def getter(self):
        return self.value

    def setter(self, newValue, label=''):
        self.value = newValue

        self.publishTopics(self.value)

    def signal(self):
        return [self.getter, self.setter]

    def state(self):
        return {
            self.label: {
                'sub': self.getter(),
                'pub': self.publish
            }
        }

    def publish(self, publishLocation, label):
        self.topics.update({label: publishLocation})

        publishLocation(self.value, label)

    def publishTopics(self, value):
        for label in self.topics:

            self.topics[label](value, label)


class Component:
    def __init__(self, template: str, state: map, values={}) -> None:
        self.template = template
        self.state = state
        self.values = values

        self.hydrate()

    def preprocess(self):
        for process in self.values['processors']:
            self.templateEval = process(
                self.templateEval)

    def hydrate(self):
        for label in self.state:
            self.values.update({label: self.state[label]['sub']})
            self.templateEval = self.template.format(
                **self.values
            )

            self.preprocess()
            self.state[label]['pub'](self.topic, label)

    def topic(self, message, label):

        self.message = message

        self.state[label]['sub'] = lambda: self.message

        self.values.update({label: self.state[label]['sub']()})

        self.templateEval = self.template.format(
            **self.values
        )
        self.preprocess()

        for line in self.templateEval:
            print(line)

counter = Signal(0, 'clock')
[count, setCount] = counter.signal()


class Box(Component):
    def __init__(self, template: str, state: map):

        self.template = \
            """╭{{bound}}╮
│{template}
╰{{bound}}╯
""".format_map({"template": template})

        self.values = {}
        self.values.update({"bound": Screen.boundaryLine(template)})

        self.values.update({"processors": []})
        self.values["processors"].append(self.createVerticalBorders)

        super().__init__(self.template, state, self.values)

    def __repr__(self) -> str:
        ui = ""
        for line in self.templateEval:
            ui += line + "\n"
        return ui
        
    
    def getWindowLength(self, template):
        return len(template.split("\n")[0]) - 2

    def createVerticalBorders(self, template):
        windowSize = self.getWindowLength(template)
        templateSplit = template.split("\n")

        lines = []
        for count, line in enumerate(templateSplit):
            if "│" in line:
                lines += [line]
            if line.find("│") == -1 and line.find('─') == -1:
                line = "│" + line
                lines += [line]

        linesSorted = lines.copy()
        linesSorted.sort(key=len, reverse=True)
        biggestLine = linesSorted[0]

        remainingLenght = max(windowSize, len(biggestLine))
        lines.pop()
        for count, line in enumerate(lines):
            for space in range(remainingLenght):
                if space + len(line) == remainingLenght:
                    lines[count] += "│"
                    break
                lines[count] += " "

        for count, line in enumerate(templateSplit):
            if "│" in line:

                if count == len(lines):
                    line = lines[count-1]

        lines.insert(0, templateSplit[0])
        lines.append(templateSplit[len(templateSplit)-2])

        return lines


# boxClock = Box(
#     'Time: {clock}\nThe above line is a clock\n', counter.state())

# print('\u001b[1J')


# from datetime import datetime

# dt_now = datetime.now()

# minutes = dt_now.strftime("%H:%M:%S")

# while True:
#     if datetime.now().strftime("%H:%M:%S") != minutes:
#         dt_now = datetime.now()

#         minutes = dt_now.strftime("%H:%M:%S")
#         print('\u001b[1J')
#         print("\u001b[30A")
#         setCount(minutes)


class InputBox(Box):
    def __init__(self,  template: str, state: map):
        super().__init__(template, state)


boxClock = InputBox(
    '>opt1\n>opt2\n>opt3', counter.state())

