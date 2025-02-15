import json
import inspect


class AccentPhraseHandler:
    """
    実行する関数は子クラスが上書き
    """

    def __init__(self):
        self.mora_count = 0
        self.pause_mora_count = 0

    def preprocess(self, accent_phrases):
        return None

    def mora_handler(self, mora):
        raise NotImplementedError(
            f"Subclasses should implement {inspect.currentframe().f_code.co_name} method")

    def pause_mora_handler(self, pause_mora):
        raise NotImplementedError(
            f"Subclasses should implement {inspect.currentframe().f_code.co_name} method")

    def moras_handler(self, moras):
        return None

    def accent_phrase_handler(self, accent_phrase):
        return None

    def generate_result(self, accent_phrases):
        return None

    def run_accent_phrase(self, accent_phrase):
        moras = accent_phrase['moras']
        for mora in moras:
            self.mora_count += 1
            self.mora_handler(mora)
        self.moras_handler(moras)
        if 'pauseMora' in accent_phrase:
            self.pause_mora_handler(accent_phrase['pauseMora'])
            self.pause_mora_count += 1
        return

    def run(self, accent_phrases):
        self.preprocess(accent_phrases)
        for ap in accent_phrases:
            self.run_accent_phrase(ap)
        return self.generate_result(accent_phrases)


class APDumper(AccentPhraseHandler):

    def mora_handler(self, mora):
        text = mora.get('text', '')
        c = mora.get('consonantLength', 0)
        v = mora.get('vowelLength', 0)
        print(f'text = {text}, c = {c:.6f}, v = {v:.6f}, c + v = {c + v:.6f}')

    def pause_mora_handler(self, mora):
        self.mora_handler(mora)


class APLengthCalcrator(AccentPhraseHandler):
    def __init__(self):
        super().__init__()  # 親クラスのコンストラクタを呼び出す
        self.total_length = 0

    def mora_handler(self, mora):
        c = mora.get('consonantLength', 0)
        v = mora.get('vowelLength', 0)
        length = c + v
        self.total_length += length

    def pause_mora_handler(self, pause_mora):
        self.mora_handler(pause_mora)

    def generate_result(self, accent_phrases):
        return self.total_length


class APLengthAverageCalcurator(APLengthCalcrator):
    def generate_result(self, _):
        average = self.total_length / (self.mora_count + self.pause_mora_count)
        return average


class APMorasCounter(APLengthCalcrator):
    def generate_result(self, _):
        return self.mora_count + self.pause_mora_count


class APMorasCounter(APLengthCalcrator):
    def generate_result(self, _):
        return self.mora_count + self.pause_mora_count


class APMoraLengthAdjuster(AccentPhraseHandler):
    def preprocess(self, accent_phrases):
        self.average_length = APLengthAverageCalcurator().run(accent_phrases)

    def mora_handler(self, mora):
        if 'consonantLength' in mora:
            c = mora.get('consonantLength', 0)
            mora['vowelLength'] = self.average_length - c
        else:
            mora['vowelLength'] = self.average_length
        c = mora.get('consonantLength', 0)
        v = mora.get('vowelLength', 0)
        print(c + v)

    def pause_mora_handler(self, pause_mora):
        self.mora_handler(pause_mora)

    def generate_result(self, accent_phrases):
        return accent_phrases


with open(r'test.json.vvproj', 'r', encoding="utf-8") as f:
    di = json.load(f)

ap = di['talk']['audioItems']['89ea0174-6b44-44ac-b196-0882830238e1']['query']['accentPhrases']
APDumper().run(ap)
print(APMorasCounter().run(ap))
APMoraLengthAdjuster().run(ap)
APDumper().run(ap)

# s = json.dumps(di, indent=2, ensure_ascii=False)
# print(s)
# with open('test.json', 'w', encoding="utf-8") as f:
#     json.dump(di, f, indent=2, ensure_ascii=False)
