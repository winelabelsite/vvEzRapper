import json
import inspect
from AccentPhraseHandler import AccentPhraseHandler as APH

class APDumper(APH):

    def mora_handler(self, mora):
        text = mora.get('text', '')
        c = mora.get('consonant_length', 0)
        if c is None:   #キーがあって値がNoneの時があるから自前get必要？
            c = 0
        v = mora.get('vowel_length', 0)
        print(f'text = {text}, c = {c:.6f}, v = {v:.6f}, c + v = {c + v:.6f}')

    def pause_mora_handler(self, mora):
        self.mora_handler(mora)


class APLengthCalcrator(APH):
    def __init__(self):
        super().__init__()  # 親クラスのコンストラクタを呼び出す
        self.total_length = 0

    def mora_handler(self, mora):
        c = mora.get('consonant_length', 0)
        if c is None:   #キーがあって値がNoneの時があるから自前get必要？
            c = 0
        v = mora.get('vowel_length', 0)
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


class APMoraLengthAdjuster(APH):
    def __init__(self, average_length):
        super().__init__()
        self.average_length = average_length

    def mora_handler(self, mora):
        if 'consonant_length' in mora:
            c = mora.get('consonant_length', 0)
            if c is None:   #キーがあって値がNoneの時があるから自前get必要？
                c = 0
            mora['vowel_length'] = self.average_length - c
        else:
            mora['vowel_length'] = self.average_length
        c = mora.get('consonant_length', 0)
        if c is None:   #キーがあって値がNoneの時があるから自前get必要？
            c = 0
        v = mora.get('vowel_length', 0)
        print(c + v)

    def pause_mora_handler(self, pause_mora):
        self.mora_handler(pause_mora)

    def generate_result(self, accent_phrases):
        return accent_phrases

if __name__ == "__main__":
    from accessEngine import AccessEngine
    from wavhandler import WaveHandler
    ae = AccessEngine()
    wh = WaveHandler()

    query = ae.audio_query('じゅげむーじゅげむーごこうのすりきれ')

    wave_before = ae.synthesis(query)
    length_before = wh.get_length(wave_before)
    wh.write('ItsFineToday.wav', wave_before)

    APDumper().run(query)
    print(APMorasCounter().run(query))
    average_length = APLengthAverageCalcurator().run(query)
    APMoraLengthAdjuster(average_length).run(query)
    APDumper().run(query)
    s = json.dumps(query, indent=2, ensure_ascii=False)
    print(s)

    wave_after = ae.synthesis(query)
    length_after = wh.get_length(wave_after)
    wh.write('result.wav', wave_after)

    print(f'length_before = {length_before:.6f}')
    print(f'length_after = {length_after:.6f}')
    print(f'ratio = {length_after / length_before:.6f}')

    print('playing...')
    wh.play(wave_before)
    print('playing...')
    wh.play(wave_after)
    print('done')
