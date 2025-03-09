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
    # print(f'ratio = {ratio:.6f}')
    return ratio

def calc_expected_length(bpm, moras_count):
    """bpmとモーラ数から、期待される音声の長さを計算する"""
    expected_length = 60 * moras_count / bpm / 4
    # print(f'expected_length = {expected_length:.6f}')
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
        length = wh.get_length(wave)
        if wavefilename is not None:
            wh.write(wavefilename, wave)
        # print(f'make_sample length = {length}')
        return length, query 

def set_average_length(query, wavefilename=None):
        """クエリの各モーラの長さを平均化し、そのクエリを返す"""
        ae = AE.AccessEngine()
        wh = WH.WaveHandler()
        # APA.APDumper().run(query)
        average_length = APA.APLengthAverageCalcurator().run(query)
        query = APA.APMoraLengthAdjuster(average_length).run(query)
        wave = ae.synthesis(query)
        if wavefilename is not None:
            wh.write(wavefilename, wave)
        return query

def make_wavefile_from_query(query, wavefilename=None):
    """クエリから音声波形を生成し、その長さを返す"""
    ae = AE.AccessEngine()
    wh = WH.WaveHandler()
    wave = ae.synthesis(query)
    length = wh.get_length(wave)
    if wavefilename is not None:
        wh.write(wavefilename, wave)
    # print(f'make_wavefile_from_query length = {length}')
    return length

def query_operation(query, ratio):
    query['prePhonemeLength'] = 0.0
    query['postPhonemeLength'] = 0.0
    query["speedScale"] = 1 / ratio
    query['outputSamplingRate'] = 48000
    # APA.APDumper().run(query)
    return query


def trial_algo01(text):
    # print('お試し01 サンプル作って全体の長さ調整')

    # サンプル作る
    _, query = make_sample(text)
    moras_count = APA.APMorasCounter().run(query)
    print(f'algo01: text = {text}, moras_count = {moras_count}')

    # waveファイルを作成
    query = query_operation(query, 1.0)
    length_before = make_wavefile_from_query(query, wavefilename='algo01_before.wav')

    # 長さ調整
    ratio = calc_ratio(BPM, length_before, moras_count)
    query = query_operation(query, ratio)

    # waveファイルを作成
    length_after = make_wavefile_from_query(query, wavefilename='algo01_after.wav')
    expected_length = calc_expected_length(BPM, moras_count)
    difference = length_after - expected_length
    print(f'difference = {difference:.9f}, per mora = {(difference / moras_count):.9f}')
    return query

def trial_algo02(text):
    # print('お試し02 サンプルのMora長さを平均化してから長さ調整')

    # サンプル作る
    _, query = make_sample(text)
    moras_count = APA.APMorasCounter().run(query)
    print(f'algo02: text = {text}, moras_count = {moras_count}')
    # Moraの長さを平均化してwaveファイルを作成
    query = set_average_length(query)
    query = query_operation(query, 1.0)
    length_before = make_wavefile_from_query(query, wavefilename='algo02_before.wav')

    # 長さ調整
    ratio = calc_ratio(BPM, length_before, moras_count)
    query = query_operation(query, ratio)

    # waveファイルを作成
    length_after = make_wavefile_from_query(query, wavefilename='algo02_after.wav')
    expected_length = calc_expected_length(BPM, moras_count)
    difference = length_after - expected_length
    print(f'difference = {difference:.9f}, per mora = {(difference / moras_count):.9f}')

    # 最後に余白をつける
    query['prePhonemeLength'] = 0.5
    query['postPhonemeLength'] = 0.5
    length_after = make_wavefile_from_query(query, wavefilename='algo02_after02.wav')
    # WH.WaveHandler().show_wavefile_info('algo02_after02.wav')

    return query

def trial_algo03(text):
    # print('お試し03 サンプルのMora長さを平均化してから長さ調整、ずれを補正しながら収束を目指す')
    WAV_FILENAME = 'algo03_result.wav'
    # サンプル作る
    _, query = make_sample(text)
    moras_count = APA.APMorasCounter().run(query)
    expected_length = calc_expected_length(BPM, moras_count)
    print(f'algo03: text = {text}, moras_count = {moras_count}, expected_length = {expected_length:.9f}')

    # Moraの長さを平均化、これをもとにSpeedScaleを調整していく
    ratio = 1.0
    query = set_average_length(query)
    query = query_operation(query, ratio)
    length_before = make_wavefile_from_query(query, wavefilename=WAV_FILENAME)

    difference_min = 99999.9
    ratio = calc_ratio(BPM, length_before, moras_count)
    ratio_result = ratio
    for _ in range(10):
        # 長さ調整
        query = query_operation(query, ratio)

        # waveファイルを作成
        length_after = make_wavefile_from_query(query, wavefilename=WAV_FILENAME)
        difference = length_after - expected_length

        if difference_min > abs(difference):
            difference_min = abs(difference)
            ratio_result = ratio

        # 次の比率を計算
        ratio = ratio * expected_length / length_after
        print(f'length = {length_after:.9f}, difference = {difference:.9f} per beat = {(difference / moras_count) * 4:.9f}, ratio = {ratio:.9f}')

    print(f'result : ratio_result = {ratio_result:.9f}, difference_min = {difference_min:.9f}, length_after = {length_after:.9f}')

    # 一番差が小さかったものを選んでWaveファイル作って長さ確認。
    query = query_operation(query, ratio_result)
    length_after = make_wavefile_from_query(query, wavefilename=WAV_FILENAME)
    WH.WaveHandler().show_wavefile_info(WAV_FILENAME)

    # 最後に余白をつけてWaveファイル作成
    query['prePhonemeLength'] = 0.5
    query['postPhonemeLength'] = 0.5
    length_after = make_wavefile_from_query(query, wavefilename=WAV_FILENAME)

    return query

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

    """
    じゅげむ じゅげむ ごこうのすりきれ
    かいじゃりすいぎょの すいぎょうまつ
    うんらいまつ ふうらいまつ
    くうねるところに すむところ
    やぶらこうじの ぶらこうじ
    ぱいぽ ぱいぽ ぱいぽのしゅーりんがん
    しゅーりんがんの ぐーりんだい
    ぐーりんだいの ぽんぽこぴーの
    ぽんぽこなーの ちょうきゅうめいの
    ちょうすけ
    """

    texts = texts01[:]                   


    for text in texts:
        # trial_algo01(text)
        # trial_algo02(text)
        trial_algo03(text)
    
    
