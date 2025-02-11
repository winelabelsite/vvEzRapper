import requests
import json

class AccessEngine:
    SERVER_URL = f'http://localhost:50021/'

    def print_error(self, response):
        print(f'status code: {response.status_code}')
        print(f"{response.text}")

    # クエリ作成
    def audio_query(self, text, speaker=1):
        query_payload = {'text': text, 'speaker': speaker}
        query_response = requests.post(f'{AccessEngine.SERVER_URL}/audio_query', params=query_payload)
        if query_response.ok is False:
            self.print_error(query_response)
            return None
        return query_response.json()

    def audio_query_from_preset(self, text, preset_id):
        query_payload = {'text': text, 'preset_id': preset_id}
        query_response = requests.post(f'{AccessEngine.SERVER_URL}/audio_query_from_preset', params=query_payload)
        if query_response.ok is False:
            self.print_error(query_response)
            return None
        return query_response.json()

    # クエリ編集
    def accent_phrases(self, text, speaker=1):
        query_payload = {'text': text, 'speaker': speaker}
        query_response = requests.post(f'{AccessEngine.SERVER_URL}/accent_phrases', params=query_payload)
        if query_response.ok is False:
            self.print_error(query_response)
            return None
        return query_response.json()


    def mora_data(self, accent_phrases, speaker=1):
        query_payload = {'speaker': speaker}
        query_response = requests.post(f'{AccessEngine.SERVER_URL}/mora_data', params=query_payload, json=accent_phrases)
        if query_response.ok is False:
            self.print_error(query_response)
            return None
        return query_response.json()

    def mora_length(self, accent_phrases, speaker=1):     
        query_payload = {'speaker': speaker}
        query_response = requests.post(f'{AccessEngine.SERVER_URL}/mora_length', params=query_payload, json=accent_phrases)
        if query_response.ok is False:
            self.print_error(query_response)
            return None
        return query_response.json()

    def mora_pitch(self, accent_phrases, speaker=1):
        query_payload = {'speaker': speaker}
        query_response = requests.post(f'{AccessEngine.SERVER_URL}/mora_pitch', params=query_payload, json=accent_phrases)
        if query_response.ok is False:
            self.print_error(query_response)
            return None
        return query_response.json()

    # 音声合成
    def synthesis(self, query, speaker=1, enable_interrogative_upspeaking=True):
        query_payload = {'speaker': speaker, 'enable_interrogative_upspeak': enable_interrogative_upspeaking}
        query_response = requests.post(f'{AccessEngine.SERVER_URL}/synthesis', params=query_payload, json=query)
        if query_response.ok is False:
            self.print_error(query_response)
            return None
        return query_response.content

    # プリセット関連
    def presets(self):
        query_response = requests.get(f'{AccessEngine.SERVER_URL}/presets')
        if query_response.ok is False:
            self.print_error(query_response)
            return None
        return query_response.json()

    def add_preset(self, query):
        query_response = requests.post(f'{AccessEngine.SERVER_URL}/add_preset', json=query)
        if query_response.ok is False:
            self.print_error(query_response)
            return None
        return query_response.json()

    def update_preset(self, query):
        query_response = requests.post(f'{AccessEngine.SERVER_URL}/update_preset', json=query)
        if query_response.ok is False:
            self.print_error(query_response)
            return None
        return query_response.json()

    def delete_preset(self, id):
        query_payload = {'id': id}
        query_response = requests.post(f'{AccessEngine.SERVER_URL}/delete_preset', params=query_payload)
        if query_response.ok is False:
            self.print_error(query_response)
            return False
        return True
           
    # 話者情報
    def speakers(self):
        query_response = requests.get(f'{AccessEngine.SERVER_URL}/speakers')
        if query_response.ok is False:
            self.print_error(query_response)
            return None
        return query_response.json()

    def speaker_info(self, speaker_uuid):
        query_payload = {'speaker_uuid': speaker_uuid}
        query_response = requests.get(f'{AccessEngine.SERVER_URL}/speaker_info', params=query_payload)
        if query_response.ok is False:
            self.print_error(query_response)
            return None
        return query_response.json()

    # その他  
    def validate_kana(self, text):   
        query_payload = {'text': text}
        query_response = requests.get(f'{AccessEngine.SERVER_URL}/validate_kana', params=query_payload)
        if query_response.ok is False:
            self.print_error(query_response)
            return None
        return query_response.json() 

    def version(self):
        query_response = requests.get(f'{AccessEngine.SERVER_URL}/version')
        if query_response.ok is False:
            self.print_error(query_response)
            return None
        return query_response.json()

    def core_version(self):
        query_response = requests.get(f'{AccessEngine.SERVER_URL}/core_version')
        if query_response.ok is False:
            self.print_error(query_response)
            return None
        return query_response.json()

    def engine_manifest(self):
        query_response = requests.get(f'{AccessEngine.SERVER_URL}/engine_manifest')
        if query_response.ok is False:
            self.print_error(query_response)
            return None
        return query_response.json()

if __name__ == "__main__":
    ae = AccessEngine()

    speakers = ae.speakers()
    print(json.dumps(speakers, indent=2, ensure_ascii=False))

    speaker_uuid = speakers[0]['speaker_uuid']
    speaker_info = ae.speaker_info(speaker_uuid)
    print(speaker_info['policy'])
  
    query = ae.audio_query(u'じゅげむじゅげむごこうのすりきれ')
    print(json.dumps(query, indent=2, ensure_ascii=False))
   
    presets = ae.presets()
    print(json.dumps(presets, indent=2, ensure_ascii=False))

    preset_template = {k: v for k, v in query.items() if k != 'accent_phrases'}
    preset_template['id'] = 1
    preset_template['name'] = 'test_preset'
    preset_template['speaker_uuid'] = speaker_uuid
    preset_template['style_id'] = 1
    preset_template.pop('outputSamplingRate')
    preset_template.pop('outputStereo')
    preset_template.pop('kana')
    print(json.dumps(preset_template, indent=2, ensure_ascii=False))

    ae.add_preset(preset_template)
    presets = ae.presets()
    print(json.dumps(presets, indent=2, ensure_ascii=False))

    preset_template['name'] = 'test_preset_updated'
    ae.update_preset(preset_template)
    presets = ae.presets()
    print(json.dumps(presets, indent=2, ensure_ascii=False))

    query_preset = ae.audio_query_from_preset('にきにきにきにきにきのかし', 1)
    print(json.dumps(query_preset, indent=2, ensure_ascii=False))

    for p in presets:
        print(p['id'])
        ae.delete_preset(p['id'])
    presets = ae.presets()
    print(json.dumps(presets, indent=2, ensure_ascii=False))

    query = ae.accent_phrases(u'じゅげむじゅげむ')
    print(json.dumps(query, indent=2, ensure_ascii=False))

    query2 = ae.mora_data(query, 2)
    print(json.dumps(query2, indent=2, ensure_ascii=False))

    query3 = ae.mora_length(query, 3)
    print(json.dumps(query3, indent=2, ensure_ascii=False))

    query4 = ae.mora_length(query, 4)
    print(json.dumps(query4, indent=2, ensure_ascii=False))

    wavedata = ae.synthesis(query)
    open('test.wav', 'wb').write(wavedata)

    wavedata = ae.synthesis(query_preset)
    open('test_preset.wav', 'wb').write(wavedata)

    query = ae.version()
    print(json.dumps(query, indent=2, ensure_ascii=False))

    query = ae.engine_manifest()
    print(json.dumps(query, indent=2, ensure_ascii=False))

    
