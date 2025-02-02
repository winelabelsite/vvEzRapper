import requests
import json
import io
import re
import wave
import copy
import jaconv

class VVEzRapperEngine:

    SERVER_URL = f'http://localhost:50021/'
    SUCCESSFUL_RESPONCE = 200
    VALIDATION_ERROR = 422
    last_error = 'No Error'

    def get_last_error_info(self):
        print(f'{VVEzRapperEngine.last_error}')
        return VVEzRapperEngine.last_error
    
    def audio_query(self, text, speaker=3):
        VVEzRapperEngine.last_error = 'No Error'
        query_payload = {'text': text, 'speaker': speaker}
        query_response = requests.post(f'{VVEzRapperEngine.SERVER_URL}audio_query', params=query_payload)
        if query_response.ok is False:
            VVEzRapperEngine.last_error = (query_response.status_code, query_response.text)
            return None
        query = query_response.json()
        return query

    def accent_phrases(self, text, speaker=2, is_kana=False):
        query_payload = {'text': text, 'speaker': speaker, 'is_kana' : is_kana}
        query_response = requests.post(f'{VVEzRapperEngine.SERVER_URL}accent_phrases', params=query_payload)
        if query_response.ok is False:
            VVEzRapperEngine.last_error = (query_response.status_code, query_response.text)
            return None
        query = query_response.json()
        return query
    

    def synthesis(self, query, speaker=2, enable_interrogative_upspeak=True):
        VVEzRapperEngine.last_error = 'No Error'
        query_payload = {'speaker': speaker, 'enable_interrogative_upspeak' : enable_interrogative_upspeak}
        query_response = requests.post(f'{VVEzRapperEngine.SERVER_URL}synthesis', params=query_payload, json=query)
        if query_response.ok is False:
            VVEzRapperEngine.last_error = (query_response.status_code, query_response.text)
            return None
        return query_response.content

    def write_wave(self, filename, query, speaker=2, enable_interrogative_upspeak=True):
        content = self.synthesis(query, speaker, enable_interrogative_upspeak)
        if content is None:
            vvre.get_last_error_info()
        else:
            with open(filename, 'wb') as f:
                f.write(content)
        return content

def calc_wavdata_duration_sec(wavedata):
    with wave.open(io.BytesIO(wavedata), "rb") as wav_file:
        frame_rate = wav_file.getframerate()  # サンプルレート（Hz）
        num_frames = wav_file.getnframes()   # 総フレーム数
        print(f'{frame_rate}, {num_frames}')

    # 長さ（秒単位）
    duration_sec = num_frames / frame_rate
    # 長さ（ミリ秒単位）
    duration_ms = duration_sec * 1000
    print(f"音声の長さ: {duration_ms:.2f} ミリ秒")
    return duration_sec

def convert_and_add_slash(text):
    # ひらがなをカタカナに変換
    katakana_text = jaconv.hira2kata(text)
    # 全角カタカナの後に '/ を追加
    result = re.sub(r'([ァ-ヺヽーヿ])', r"\1'/", katakana_text)
    return result[:-1]

if __name__ == "__main__":
    # 読み上げたいテキスト
    text = "じゅげむうじゅげむうごこうのすりきれ"
    text_aquestalkfu =  convert_and_add_slash(text)
    print(text_aquestalkfu)

    vvre = VVEzRapperEngine()
    
    # ひな形作成
    query_template = vvre.audio_query(text)
    if query_template is None:
        vvre.get_last_error_info()
    else:
        # print(json.dumps(query_template, indent=2, ensure_ascii=False))
        pass

    contents_template = vvre.write_wave('output1.wav', query_template)

    # アクセントフレーズをAquesTalk風フォーマットで作る。
    accent_phrases = vvre.accent_phrases(text_aquestalkfu, is_kana=True)
    if accent_phrases is None:
        vvre.get_last_error_info()
    else:
        # print(json.dumps(accent_phrases, indent=2, ensure_ascii=False))
        pass

    query_aquestalkfu = copy.deepcopy(query_template)

    query_aquestalkfu['accent_phrases'] = accent_phrases
    content_aquestalkfu = vvre.write_wave('output2.wav', query_aquestalkfu)
    # print(json.dumps(query_aquestalkfu, indent=2, ensure_ascii=False))
    
    content = content_aquestalkfu
    query_json = query_aquestalkfu
    duration_sec = calc_wavdata_duration_sec(content)
    print(f'{duration_sec}')

    # モーラの数を数える。
    mora_count = 0
    for ac in query_json['accent_phrases']:
        mora_count += len(ac['moras'])
        if ac['pause_mora'] is not None:
            mora_count += 1
    print(f'{mora_count}')

    # モーラの速さとか期待する再生スピードがらみの定数とか
    mpm = 60 / (duration_sec / mora_count)
    expected_mpm = 120 * 4
    speed_scale = expected_mpm / mpm
    print(f'mora per second = {mpm}, expected_mpm = {expected_mpm}, speed_scale = {speed_scale}')

    # スピード調整、前後の無音スペースをなくす等。
    query_json['speedScale'] = speed_scale
    query_json['prePhonemeLength'] = 0
    query_json['postPhonemeLength'] = 0

    # ファイナル
    content = vvre.synthesis(query_json, 1)
    vvre.write_wave('output_after2.wav', query_json)
