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

    def calc_ratio(bpm, wave_length, moras_count):
        """bpmとwave_lengthから、1モーラあたりの秒数を計算し、それをbpmから求めた値と比較して、比率を求める"""
        spb_given = 60 / bpm / 4
        spb_before = wave_length / moras_count
        ratio = spb_given / spb_before
        print(f'spb_given = {spb_given:.6f}, spb_before = {spb_before:.6f}, ratio = {ratio:.6f}')
        return ratio

    def make_sample(text, is_kana=False, wavefilename=None):
        """テキストから音声波形を生成し、その長さとクエリを返す"""
        ae = AccessEngine()
        wh = WaveHandler()
        query = ae.audio_query(text)
        if is_kana is True:
            accent_phrases = ae.accent_phrases(text, is_kana=is_kana)
            query['accentPhrases'] = accent_phrases
            query['kana'] = text
        print(query['kana'])
        wave = ae.synthesis(query)
        length_before = wh.get_length(wave)
        if wavefilename is not None:
            wh.write(wavefilename, wave)
        return length_before, query 

    def set_average_length(query, wavefilename=None):
        """クエリの各モーラの長さを平均化し、そのクエリを返す"""
        ae = AccessEngine()
        wh = WaveHandler()
        average_length = APLengthAverageCalcurator().run(query)
        # query['prePhonemeLength'] = 0.0
        # query['postPhonemeLength'] = 0.0
        APMoraLengthAdjuster(average_length).run(query)
        APDumper().run(query)
        wave = ae.synthesis(query)
        length = wh.get_length(wave)
        if wavefilename is not None:
            wh.write(wavefilename, wave)
        return length, query
    
    bpm = 120

    text = 'じゅげむーじゅげむーごこーのすりきれじゅげむーじゅげむーごこーのすりきれ'
    text = "ジュ'ゲムウ/ジュ'ゲムウ/ゴコ'オノ/スリ'キレ'"
    l01, q01 = make_sample(text, is_kana=True, wavefilename='original.wav')
    print(json.dumps(q01, indent=2, ensure_ascii=False))
    APDumper().run(q01)
    moras_count = APMorasCounter().run(q01)
    print(f'moras_count = {moras_count}')

    l02, q02 = set_average_length(q01)
    print(f'length_before = {l01:.6f}')
    print(f'length_after = {l02:.6f}')
    APDumper().run(q02)
    
    ratio = calc_ratio(bpm, l02, moras_count)

    def make_rap(query, ratio, wavefilename=None):
        ae = AccessEngine()
        wh = WaveHandler()
        query['speedScale'] /= ratio
        query['postPhonemeLength'] /= ratio
        wave = ae.synthesis(query)
        length = wh.get_length(wave)
        if wavefilename is not None:
            wh.write(wavefilename, wave)
        return length, wave

    length_rap, wave =  make_rap(q01, ratio, 'rap.wav')
    APDumper().run(q01)
    print(f'length = {length_rap:.6f}')

    spb_rap = length_rap / moras_count
    length_expected = spb_given = 60 / bpm / 4 * moras_count
    print(f'length_rap = {length_rap:.6f}, len= {moras_count}, expected = {length_expected:.6f}, diff(total) = {length_rap - length_expected:.6f}, diff(per mora) = {(length_rap - length_expected) / moras_count}' )
    WaveHandler().play(wave)
