import json
from AccentPhraseHandler import AccentPhraseHandler as APH

class APDumper(APH):

    def generate_result(self, accent_phrases):
        print(f'speedScale = {accent_phrases['speedScale']:.6f}')
        print(f'prePhonemeLength = {accent_phrases['prePhonemeLength']:.6f}')
        print(f'postPhonemeLength = {accent_phrases['postPhonemeLength']:.6f}')
        
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

    def pause_mora_handler(self, pause_mora):
        self.mora_handler(pause_mora)

    def generate_result(self, accent_phrases):
        accent_phrases['prePhonemeLength'] = 0.0
        # accent_phrases['postPhonemeLength'] = 0.0
        return accent_phrases

if __name__ == "__main__":
    import sys
    from accessEngine import AccessEngine
    from wavhandler import WaveHandler
    ae = AccessEngine()
    wh = WaveHandler()

    def test01(ae, wh, text):
        query = ae.audio_query(text)
        moras_count = APMorasCounter().run(query)
        print(f'moras_count = {moras_count}')
        query = ae.audio_query(text)
        wave = ae.synthesis(query)
        length_before = wh.get_length(wave)
        wh.write('test01.wav', wave)
        return length_before, query, 

    def test02(query):
        average_length = APLengthAverageCalcurator().run(query)
        # query['prePhonemeLength'] = 0.0
        # query['postPhonemeLength'] = 0.0
        APMoraLengthAdjuster(average_length).run(query)
        APDumper().run(query)
        wave = ae.synthesis(query)
        wh.write('test02.wav', wave)
        length = wh.get_length(wave)
        return length, query
    
    text = 'おきておきておきておきておきてー'
    l01, q01 = test01(ae, wh, text)
    moras_count = APMorasCounter().run(q01)
    APDumper().run(q01)

    l02, q02 = test02(q01)
    print(f'length_before = {l01:.6f}')
    print(f'length_after = {l02:.6f}')
    APDumper().run(q02)

    bpm = 120
    spb_given = 60 / bpm / 4
    spb_before = l02 / moras_count
    ratio = spb_given / spb_before
    print(f'spb_given = {spb_given:.6f}, spb_before = {spb_before:.6f}, ratio = {ratio:.6f}')

    q02['speedScale'] /= ratio
    q02['postPhonemeLength'] /= ratio
    APDumper().run(q02)
    wave = ae.synthesis(q02)
    length = wh.get_length(wave)
    print(f'length = {length:.6f}')
    wh.write('rap.wav', wave)

    length_rap = wh.get_length(wave)
    spb_rap = length_rap / moras_count
    length_expected = spb_given * moras_count
    print(f'length_rap = {length_rap:.6f}, len= {moras_count}, expected = {length_expected:.6f}, diff(total) = {length_rap - length_expected:.6f}, diff(per mora) = {(length_rap - length_expected) / moras_count}' )
    wh.play(wave)
