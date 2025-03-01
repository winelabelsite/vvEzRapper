import json
import AccentPhraseApps as APA
import wavhandler as WH
import accessEngine as AE

BPM = 120

def calc_ratio(bpm, wave_length, moras_count):
    """bpmとwave_lengthから、1モーラあたりの秒数を計算し、それをbpmから求めた値と比較して、比率を求める"""
    spb_given = 60 / bpm / 4
    spb_before = wave_length / moras_count
    ratio = spb_given / spb_before
    print(f'spb_given = {spb_given:.6f}, spb_before = {spb_before:.6f}, ratio = {ratio:.6f}')
    return ratio

def calc_expected_length(bpm, moras_count):
    """bpmとモーラ数から、期待される音声の長さを計算する"""
    expected_length = 60 * moras_count / bpm / 4
    return expected_length

def make_sample(text, is_kana=False, wavefilename=None):
        """テキストから音声波形を生成し、その長さとクエリを返す"""
        ae = AE.AccessEngine()
        wh = WH.WaveHandler()
        query = ae.audio_query(text)
        if is_kana is True:
            accent_phrases = ae.accent_phrases(text, is_kana=is_kana)
            query['accentPhrases'] = accent_phrases
            query['kana'] = text
        wave = ae.synthesis(query)
        length_before = wh.get_length(wave)
        if wavefilename is not None:
            wh.write(wavefilename, wave)
        return length_before, query 

def set_average_length(query, wavefilename=None):
        """クエリの各モーラの長さを平均化し、そのクエリを返す"""
        ae = AE.AccessEngine()
        wh = WH.WaveHandler()
        average_length = APA.APLengthAverageCalcurator().run(query)
        APA.APMoraLengthAdjuster(average_length).run(query)
        APA.APDumper().run(query)
        wave = ae.synthesis(query)
        length = wh.get_length(wave)
        if wavefilename is not None:
            wh.write(wavefilename, wave)
        return length, query

def make_wavefile_from_query(query, wavefilename=None):
    """クエリから音声波形を生成し、その長さを返す"""
    ae = AE.AccessEngine()
    wh = WH.WaveHandler()
    wave = ae.synthesis(query)
    length = wh.get_length(wave)
    if wavefilename is not None:
        wh.write(wavefilename, wave)
    return length


def trial_algo01(text):
    # print('お試し01 サンプル作って全体の長さ調整')

    # サンプル作って長さ測ってみる
    length_before, query = make_sample(text, wavefilename='algo01_before.wav')
    moras_count = APA.APMorasCounter().run(query)
    ratio = calc_ratio(BPM, length_before, moras_count)

    # Queryを操作する
    query['prePhonemeLength'] = 0.0
    query['postPhonemeLength'] = 0.0
    query["speedScale"] = 1 / ratio
    query['outputSamplingRate'] = 48000

    # waveファイルを作成
    length_after = make_wavefile_from_query(query, wavefilename='algo01_after.wav')
    expected_length = calc_expected_length(BPM, moras_count)
    difference = length_after - expected_length
    # これ一つにまとめて使いまわしたいよね。
    # print(f'moras_count = {moras_count}')   # queryから出せる
    # print(f'length_before = {length_before:.6f}') # make_sampleから出せる
    # print(f'ratio = {ratio:.6f}') # 上二つがわかれば出せる 
    # print(f'length_after = {length_after:.6f}')   # 長さいじった後なら出せる
    # print(f'expected_length = {expected_length:.6f}') # すぐ出せる
    # print(f'difference = {difference}')   # すぐ出せる
    # print(json.dumps(query, indent=2, ensure_ascii=False))    # 気になったら表示
    print(expected_length / difference)
    pass


if __name__ == "__main__":
    texts01 = [
    'じゅ',
    'じゅげ',
    'じゅげむー',
    'じゅげむーじゅげむー',
    'じゅげむーじゅげむーごこおのすりきれ',
    'じゅげむーじゅげむーごこおのすりきれじゅげむーじゅげむー',
    'じゅげむーじゅげむーごこおのすりきれじゅげむーじゅげむーごこおのすりきれ',
    ]

    texts02 = ['じぇじぇじぇじぇ' * i for i in range(1, 10)]

    texts = texts02 + texts01

    for text in texts[-1:]:
        trial_algo01(text)

    
    
