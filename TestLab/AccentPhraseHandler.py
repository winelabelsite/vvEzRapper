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
        return None

    def pause_mora_handler(self, pause_mora):
        return None

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
        self.preprocess(accent_phrases['accent_phrases'])
        for ap in accent_phrases['accent_phrases']:
            self.run_accent_phrase(ap)
        return self.generate_result(accent_phrases)


if __name__ == "__main__":
    class testAccentPhraseHandler(AccentPhraseHandler):
        def preprocess(self, accent_phrases):
            print(f'preprocess')
            return None

        def mora_handler(self, mora):
            print(f'mora_handler')

        def pause_mora_handler(self, pause_mora):
            print(f'pause_mora_handler')

        def moras_handler(self, moras):
            print(f'moras_handler')

        def accent_phrase_handler(self, accent_phrase):
            print(f'accent_phrase_handler')

        def generate_result(self, accent_phrases):
            print(f'generate_result')

    with open(r'ItsFineToday.vvproj', 'r', encoding="utf-8") as f:
        di = json.load(f)
    s = json.dumps(di, indent=2, ensure_ascii=False)
    print(s)
    audiokey = list(di['talk']['audioItems'].keys())[0] 
    accent_phrases = di['talk']['audioItems'][audiokey]['query']['accentPhrases']
    ta = testAccentPhraseHandler()
    ta.run(accent_phrases)
